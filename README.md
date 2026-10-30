# ⚡ Resume Tailor — Ruthless Focus

> Transform generic resume experience bullet points into high-impact, role-matched achievements in seconds.

---

## What This App Does

Applying to jobs often requires spending 30–45 minutes manually rewriting resume bullet points for every application to match specific job descriptions and get past initial recruiter/ATS screening.

**Resume Tailor** solves this with ruthless focus:
1. **Paste your existing resume bullets** on the left.
2. **Paste the target job description** below it.
3. Click **Tailor Bullets** (or press `⌘ + Enter` / `Ctrl + Enter`).
4. In under 3 seconds, Gemini AI analyzes the target job requirements and transforms your raw experience into quantifiable, role-aligned bullets following the **Google XYZ formula** ("Accomplished [X] as measured by [Y], by doing [Z]").
5. Click **Copy Bullet** or **Copy All** to paste the tailored text straight into your resume.

### What We Deliberately Cut
To keep the tool lightning fast and friction-free:
- **No PDF / DOCX file parsing:** Plain text paste avoids upload failures and formatting corruption.
- **No user accounts or databases:** 100% ephemeral and private; your resume data is never stored.
- **No Node.js / heavy build steps:** Single lightweight Python FastAPI server serves the static frontend directly.

---

## Source of Truth (Design Docs)

This application was designed using a three-tier design doc discipline. Anyone contributing or maintaining the codebase should consult these documents:

- **[product.md](product.md) (PM Design Doc):** Defines the target user, the magic moment, strict scope cuts, and primary success metrics.
- **[ui.md](ui.md) (UX Design Doc):** Specifies the single-screen split-pane layout (`Tailor Studio`), defining interaction, loading/empty/error states, and design system choices.
- **[engineering.md](engineering.md) (Engineering Design Doc):** Details system architecture, Pydantic schemas, API contracts, latency budgets, key trade-offs, and the testing strategy.

---

## Project Structure

```
bulletproofResume/
├── README.md              # Project overview and setup instructions
├── BRIEF.md               # Original project brief
├── product.md             # PM design doc & contract
├── ui.md                  # UX design doc & screen specs
├── engineering.md         # Engineering design doc & test plan
├── frontend/              # Static single-page application
│   ├── index.html         # Split-pane UI
│   ├── style.css          # Design system & dark slate theme
│   └── app.js             # Client state, shortcut keys & clipboard logic
└── backend/               # FastAPI backend service
    ├── pyproject.toml     # Python dependencies managed with uv
    ├── .env.example       # Environment template
    ├── .env               # Local API credentials (git-ignored)
    ├── main.py            # FastAPI entry point & static file server
    ├── prompts.py         # System prompt, schemas & prompt builder
    ├── gemini_service.py  # Google GenAI SDK integration (Gemini 3.8 Flash)
    └── tests/             # Pytest test suite (unit & integration)
        ├── test_validation.py
        ├── test_prompts.py
        └── test_integration.py
```

---

## Quickstart & Installation

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Fast Python package manager)
- A [Google Gemini API Key](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/gca-americas/codingjam-bulletproof.git
cd codingjam-bulletproof
```

### 2. Install Dependencies
Navigate to the `backend` directory and use `uv sync`:
```bash
cd backend
uv sync
```

### 3. Configure Environment Variables
Copy the example environment template and add your Gemini API key:
```bash
cp .env.example .env
```

Open `.env` and set your key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

---

## Running the Dev Server

From the `backend` directory, start the server using Uvicorn:

```bash
cd backend
.venv/bin/uvicorn main:app --reload --port 8000
```

Once running:
- **Web App UI:** Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## Running Tests

The test suite runs with `pytest` and mocks all Gemini API calls so tests run deterministically, instantly, and at zero cost:

```bash
cd backend
.venv/bin/pytest -v
```
