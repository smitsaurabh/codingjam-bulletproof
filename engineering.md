# Resume Tailor — Engineering Design Doc

**Author:** Staff Software Engineer  
**Status:** Draft v0.1  
**Last updated:** 2026-10-30  
**Reviewers:** Engineering Team  

---

## 1. Summary

Resume Tailor is an ultra-focused web application that accepts raw resume experience bullet points alongside a target job description and generates role-tailored, high-impact bullet points mapped to critical job requirements. Architecturally, it follows the proven single-process web pattern from `reference/moodjar-example`: a lightweight Python FastAPI service managed via `uv`, leveraging Google's official `google-genai` SDK with structured JSON outputs, while directly serving a high-performance vanilla HTML/CSS/JS frontend as static assets. The system requires zero persistent database, zero Node.js build pipelines, and executes the core tailoring loop with a sub-3.5-second latency target.

## 2. Assumptions

The technical constraints and environmental assumptions framing this design:

- **Target scale:** < 2,000 daily active tailoring requests in v1.
- **Latency budget:** End-to-end p95 response time < 3,500ms; LLM generation budget < 2,500ms.
- **Platform & Environment:** Modern desktop and mobile web browsers (Chrome, Safari, Edge, Firefox); Python 3.11+ running with `uv`. No Node.js runtime installed or required.
- **Cost ceiling:** < $0.005 per tailoring request utilizing Gemini Flash models with structured outputs.
- **State boundary:** 100% ephemeral and stateless on the backend. No user accounts, database connections, or session persistence.

## 3. Goals & non-goals

**Goals (v1):**
- Deliver a single executable web service via `uv run uvicorn main:app` serving both API and frontend on port 8000.
- Provide a robust API endpoint (`POST /api/tailor`) that enforces strict input validation and returns schema-validated JSON with tailored bullets, skill tags, and rationale.
- Guarantee predictable, machine-parsable AI output by using the official `google-genai` SDK with strict JSON schema response types.
- Ensure p95 latency under 3.5 seconds end-to-end for payloads up to 8,000 characters.
- Maintain a self-contained code footprint that can be easily tested, containerized, or deployed to Google Cloud Run.

**Non-goals (v1):**
- No relational or document database (PostgreSQL, SQLite, Redis, or Firestore) — requests are strictly stateless.
- No asynchronous background task queues (Celery, RabbitMQ) — synchronous HTTP request-response fits the sub-3.5s SLA.
- No Node.js, Webpack, Vite, or TypeScript build toolchain — vanilla ES6+ and modern CSS keep development instantaneous.
- No user authentication, OAuth, or session management.
- No file parsing libraries (PyPDF2, pdfminer, python-docx) — text paste only.

## 4. Architecture

```mermaid
flowchart LR
  Browser[Client Browser\nVanilla HTML5 / CSS / JS] -->|POST /api/tailor\n(JSON: resume + job_desc)| FastAPI[FastAPI Backend\nPython + Uvicorn]
  FastAPI -->|Static File Mount /| Browser
  FastAPI -->|Input Validation & Prompt Builder| Service[Tailor Engine Service]
  Service -->|google-genai SDK\ngemini-2.5-flash / gemini-1.5-flash| Gemini[(Google Gemini API)]
  Gemini -->|Structured JSON Output| Service
  Service -->|Validated TailorResponse| FastAPI
  FastAPI -->|JSON Response 200 OK| Browser
```

**What's here:**
- **FastAPI / Uvicorn Server:** Single lightweight process handling routing, CORS, static file serving, and endpoint telemetry.
- **Gemini Client Service:** Encapsulates prompt orchestration, system instructions, and structured schema enforcement using `google-genai`.
- **Vanilla Frontend Client:** Single-page interface handling dual inputs, character count tracking, clipboard interaction, and error toasts.

**What's deliberately NOT here:**
- **No Database:** No storage layer; eliminates data retention concerns, PII leakage risks, and migration maintenance.
- **No Node.js / NPM Build Step:** Frontend is served directly by FastAPI from `frontend/`, eliminating `node_modules` overhead and build pipeline failures.
- **No Message Broker / Worker Nodes:** Gemini Flash model speeds make synchronous HTTP calls the most reliable, cost-effective path.

## 5. Key components

### 1. API Server (`backend/main.py`)
- **Responsibility:** Request handling, CORS policy configuration, error boundary handling, and mounting static frontend files at `/`.
- **Tech choice:** FastAPI + Uvicorn.
- **Why this choice:** As demonstrated in `reference/moodjar-example`, FastAPI provides automatic OpenAPI documentation, lightning-fast async performance, and built-in Pydantic validation.
- **Interface:**
  - `POST /api/tailor(payload: TailorRequest) -> TailorResponse`
  - `GET /api/health -> HealthResponse`

### 2. Prompt & Schema Orchestrator (`backend/prompts.py`)
- **Responsibility:** Defines the expert resume tailoring persona, action verb guidelines, anti-hallucination guardrails, and the target Pydantic output schema.
- **Tech choice:** Python Pydantic v2 + Gemini Structured Output configuration.
- **Why this choice:** Guarantees 100% compliant JSON responses without requiring manual regex parsing or JSON retry loops.
- **Interface:**
  - `RESUME_TAILOR_SYSTEM_PROMPT: str`
  - `class TailoredBullet(BaseModel)`
  - `class TailorResponse(BaseModel)`

### 3. Gemini Client Adapter (`backend/gemini_service.py`)
- **Responsibility:** Manages authentication (checking `GEMINI_API_KEY` from environment) and dispatches inference requests to `gemini-2.5-flash` or `gemini-1.5-flash`.
- **Tech choice:** `google-genai` official SDK.
- **Why this choice:** Google's latest official unified client library; native support for structured JSON schema outputs and low-latency streaming if needed.
- **Interface:**
  - `async def tailor_resume(resume_text: str, job_description: str) -> TailorResponse`

### 4. Static Single-Page Client (`frontend/app.js`, `index.html`, `style.css`)
- **Responsibility:** Renders the split workbench layout, executes client-side validation, handles `POST /api/tailor` network calls, and provides one-click clipboard copying.
- **Tech choice:** Modern Vanilla JS (ES6+), semantic HTML5, pure CSS with custom properties.
- **Why this choice:** Zero dependencies, instant browser load, zero compilation step, runs identically in all browsers.
- **Interface:**
  - `handleTailorSubmit(event)`
  - `copyBulletToClipboard(text, buttonElement)`
  - `loadSampleData()`

## 6. Data model

### Backend Schemas (Pydantic v2)

```python
from pydantic import BaseModel, Field
from typing import List

class TailorRequest(BaseModel):
    resume_text: str = Field(
        ..., 
        min_length=20, 
        max_length=10000, 
        description="Raw resume bullets or experience section pasted by the user."
    )
    job_description: str = Field(
        ..., 
        min_length=20, 
        max_length=10000, 
        description="Target job posting text, qualifications, and responsibilities."
    )

class TailoredBullet(BaseModel):
    bullet: str = Field(
        ..., 
        description="The polished, metric-driven, action-oriented bullet point tailored to the target role."
    )
    skill_tag: str = Field(
        ..., 
        description="The primary technical skill or requirement from the job posting addressed by this bullet."
    )
    original_reference: str = Field(
        ..., 
        description="Brief summary of the original experience that grounded this tailored bullet."
    )

class TailorResponse(BaseModel):
    role_title_detected: str = Field(
        ..., 
        description="Target role title identified from the job description (e.g., 'Senior Staff Engineer')."
    )
    bullets: List[TailoredBullet] = Field(
        ..., 
        min_length=1, 
        max_length=8, 
        description="List of tailored resume bullet points."
    )
    key_keywords_aligned: List[str] = Field(
        default_factory=list, 
        description="Key skill keywords matched between the resume and job posting."
    )

class HealthResponse(BaseModel):
    status: str = Field(default="ok")
    version: str = Field(default="1.0.0")
```

## 7. API surface

### `POST /api/tailor`
Transforms pasted resume bullets and job posting into tailored bullets.

- **Request Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "resume_text": "Built notification service. Led migration to AWS. Reduced database latency.",
    "job_description": "Looking for a Staff Distributed Systems Engineer with Go, Kafka, and high-throughput AWS experience..."
  }
  ```
- **Response Body (200 OK):**
  ```json
  {
    "role_title_detected": "Staff Distributed Systems Engineer",
    "bullets": [
      {
        "bullet": "Architected distributed event-driven notification service in Go and Kafka, sustaining 15,000 RPS with 99.99% delivery reliability across AWS regions.",
        "skill_tag": "Distributed Systems & Kafka",
        "original_reference": "Built notification service"
      },
      {
        "bullet": "Led cross-functional migration of core services to AWS, reducing p99 database query latency by 42% through query optimization and caching.",
        "skill_tag": "AWS & Performance Optimization",
        "original_reference": "Led migration to AWS and reduced database latency"
      }
    ],
    "key_keywords_aligned": ["Go", "Kafka", "AWS", "High-Throughput", "Distributed Systems"]
  }
  ```
- **Error Codes:**
  - `400 Bad Request`: Input text exceeds character limits or contains insufficient data.
  - `422 Unprocessable Entity`: Request body fails Pydantic schema validation.
  - `500 Internal Server Error`: Gemini API communication failure or model timeout.
  - `503 Service Unavailable`: Missing `GEMINI_API_KEY` configuration.
- **Latency Budget:** End-to-end p95 ≤ 3,500ms (Network: 200ms, Backend serialization: 50ms, Gemini inference: 2,800ms, Response render: 100ms).

### `GET /api/health`
Basic service liveness probe.

- **Response (200 OK):** `{"status": "ok", "version": "1.0.0"}`

## 8. Key trade-offs (with rejected alternatives)

### Decision 1: Python FastAPI + Vanilla JS vs. Full-Stack Next.js / TypeScript
- **Chose:** Python FastAPI with static vanilla JS files.
- **Considered:** Next.js (React + TypeScript) with Server Actions; Streamlit / Gradio.
- **Why we picked this:** The user environment specifically requires no Node.js installation. FastAPI with static file hosting (as demonstrated in `reference/moodjar-example`) is a zero-Node, lightning-fast architecture. Streamlit/Gradio were rejected because their UI components are sluggish and do not support our precise split-pane UX and custom clipboard micro-interactions.

### Decision 2: Structured JSON Output via Pydantic vs. Free-form Markdown with Regex Parsing
- **Chose:** Strict Pydantic JSON schema passed directly to `google-genai` SDK (`response_schema=TailorResponse, response_mime_type="application/json"`).
- **Considered:** Raw markdown output with `###` headers and regex string splitting.
- **Why we picked this:** Regex parsing breaks frequently on unexpected LLM formatting (bullet asterisks vs numbers, missing line breaks). Native structured outputs guarantee schema adherence on the first attempt, preventing malformed UI states and eliminating retry latency.

### Decision 3: Ephemeral Stateless Backend vs. Local SQLite Database
- **Chose:** 100% ephemeral stateless requests.
- **Considered:** SQLite database to persist session history.
- **Why we picked this:** Storing user resumes introduces privacy liabilities and PII risks. Resumes are personal documents; users feel significantly safer knowing their text is processed in memory and never written to a local or cloud database.

## 9. Risks & unknowns

- **Gemini API Key Missing or Invalid** — *Likelihood: Med* — *Mitigation:* Explicit server startup and request checks in `main.py` return an actionable 503 error message ("GEMINI_API_KEY environment variable is not configured. Please set it in your .env file.").
- **Model Latency Spikes on Large Job Postings** — *Likelihood: Med* — *Mitigation:* Impose an 8,000 character maximum validation cap on both inputs and instruct the system prompt to summarize requirements before generating bullets; enforce an HTTP client timeout of 10s.
- **Hallucinated Qualifications** — *Likelihood: Med* — *Mitigation:* System prompt strictly instructs Gemini: "Never fabricate job titles, employers, or metrics not grounded in the original resume text. Transform framing and impact, but do not invent work the candidate never did."
- **Browser Clipboard Permission Denial** — *Likelihood: Low* — *Mitigation:* Standard fallback implementation: try `navigator.clipboard.writeText`, if rejected or unavailable (e.g., non-HTTPS local IP), fall back to `document.execCommand('copy')` on a hidden textarea.

## 10. Testing strategy

This testing strategy defines the exact test suite implemented via `pytest` for backend verification.

**Unit tests (must have):**
- `test_validate_input_valid`: Verifies that `TailorRequest` accepts valid inputs within length constraints (20–10,000 characters).
- `test_validate_input_too_short`: Verifies that submitting inputs shorter than 20 characters raises a validation error (HTTP 422).
- `test_validate_input_too_long`: Verifies that inputs exceeding 10,000 characters are rejected with a clear validation error.
- `test_build_prompt_contains_inputs`: Verifies that the prompt constructor in `prompts.py` properly interpolates both resume text and job description into the model payload.
- `test_tailor_response_pydantic_parsing`: Verifies that a valid Gemini JSON dictionary successfully parses into `TailorResponse` with all expected attributes (`bullet`, `skill_tag`, `original_reference`).

**Integration tests (one per major flow):**
- `test_health_endpoint`: Simulates `GET /api/health` via `httpx.AsyncClient` / FastAPI `TestClient`, asserting HTTP status 200 and `{"status": "ok", "version": "1.0.0"}`.
- `test_tailor_endpoint_happy_path`: Simulates `POST /api/tailor` with a realistic mock payload, mocking the Gemini SDK client to return a valid `TailorResponse`, asserting HTTP 200, proper JSON structure, and valid bullet count.
- `test_tailor_endpoint_gemini_error_handling`: Simulates `POST /api/tailor` when the Gemini client raises an API error (e.g., rate limit or timeout), asserting that the endpoint handles the exception gracefully with an HTTP 500 and structured error detail.

**Deliberately not tested (and why):**
- **Actual LLM Creative Quality:** Non-deterministic output quality is impossible to assert reliably in automated CI; Gemini SDK calls are mocked in integration tests to ensure deterministic, zero-cost, and offline-capable test runs.
- **Frontend DOM Animations & Button Pulsing:** Visual CSS transitions and timing verified visually; headless UI automation adds unnecessary brittleness without functional gain.
- **Native Browser Clipboard APIs:** Clipboard write permissions require elevated browser security context; tested manually in supported browsers.

**Stack defaults:**
- Framework: `pytest` + `pytest-asyncio` + `httpx`
- Directory: `backend/tests/`
- Command: `uv run pytest backend/tests/`

## 11. Rollout & monitoring

- **Rollout:** Local execution via `uv sync && uv run uvicorn main:app --reload`. Production deployment as a single container on Google Cloud Run with `PORT=8000`.
- **Monitoring (Core Signals):**
  1. `request_count`: Total requests per minute to `/api/tailor`.
  2. `latency_p95`: End-to-end request duration; alerts if p95 exceeds 4,000ms over a 5-minute rolling window.
  3. `error_rate_5xx`: Ratio of 5xx errors to total requests; alerts if > 2%.
  4. `gemini_api_exceptions`: Specific counter tracking Google GenAI client exceptions (quota exhaustion or authentication failure).
- **Rollback plan:** Single-container rollback to previous container image tag in Cloud Run (< 30 seconds).

## 12. Cost & capacity

- **Model Selection:** `gemini-2.5-flash` (or `gemini-1.5-flash`).
- **Token Math:**
  - Input tokens: ~500 tokens (resume) + ~800 tokens (job posting) + ~400 tokens (system prompt) = ~1,700 tokens per request.
  - Output tokens: ~500 tokens (5 tailored bullets + metadata).
- **Per-request cost:**
  - Input: 1,700 tokens × $0.075 / 1M tokens ≈ $0.00013
  - Output: 500 tokens × $0.30 / 1M tokens ≈ $0.00015
  - Total per tailoring run: **~$0.00028** (< $0.0003).
- **Monthly budget at v1 scale (2,000 requests/day = 60,000/month):**
  - 60,000 × $0.00028 ≈ **$16.80 / month**.
- **What breaks at 10× scale (20,000 requests/day):**
  - Gemini API tier rate limits (RPM / TPM). Mitigation: request quota increase from Google Cloud Console or configure exponential backoff retries.

## 13. Open questions

- [ ] What is the optimal temperature setting for `gemini-2.5-flash` (e.g., 0.2 for strict factual precision vs 0.4 for action-verb variety)? — *Owner: Lead ML/Backend Engineer*
- [ ] Should the endpoint support optional streaming (`POST /api/tailor/stream`) in v1.1 for immediate first-token rendering? — *Owner: Backend Engineer*

## 14. Out of scope (will not do)

- **No file upload endpoints (`/api/upload`)** — No PDF or Word file parsing binaries or dependencies in the image.
- **No authentication or user sessions** — No JWT verification, session cookies, or user profile tables.
- **No background task queues** — No Redis, Celery, or worker processes.
- **No PDF / DOCX generation engines** — No headless Chrome, Puppeteer, or WeasyPrint libraries.
- **No external analytics telemetry scripts** — Clean, privacy-first implementation without third-party tracking cookies.
