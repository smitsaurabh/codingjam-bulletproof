"""Resume Tailor — FastAPI Backend Application."""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from prompts import TailorRequest, TailorResponse, HealthResponse
from gemini_service import tailor_resume

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that validates GEMINI_API_KEY configuration at startup."""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        masked = api_key[:6] + "..."
        print(f"✓ [Startup] GEMINI_API_KEY loaded successfully ({masked})")
    else:
        print("⚠️ [Startup] WARNING: GEMINI_API_KEY is not configured or using placeholder.")
    yield


app = FastAPI(
    title="Resume Tailor API",
    description="Transforms raw resume bullet points into role-tailored, high-impact achievements.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local testing and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Liveness probe verifying that the API service is running."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/api/tailor", response_model=TailorResponse)
async def tailor(request: TailorRequest):
    """Tailors resume experience bullets according to target job posting requirements."""
    try:
        response = await tailor_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )
        return response

    except ValueError as e:
        error_msg = str(e)
        if "GEMINI_API_KEY" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model response formatting error: {error_msg}",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI inference error: {str(e)}",
        )


# Mount frontend static assets at root (must be after API routes)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
