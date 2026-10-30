"""Gemini AI client integration for resume bullet tailoring."""

import json
import os
from typing import Optional
from google import genai
from google.genai import types

from prompts import (
    RESUME_TAILOR_SYSTEM_PROMPT,
    TailorResponse,
    build_tailor_prompt,
)

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def create_gemini_client() -> genai.Client:
    """Create a fresh Gemini client for each request.

    Checks GEMINI_API_KEY first, then Google Cloud Vertex AI credentials.
    Raises ValueError if neither is available.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        return genai.Client(api_key=api_key)

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project:
        return genai.Client(
            vertexai=True,
            project=project,
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )

    raise ValueError(
        "GEMINI_API_KEY environment variable is not configured. "
        "Please set it in your .env file or environment."
    )


async def tailor_resume(
    resume_text: str,
    job_description: str,
    client: Optional[genai.Client] = None,
    model_name: Optional[str] = None,
) -> TailorResponse:
    """Calls the Gemini API with structured output schema to tailor resume bullets."""
    if client is None:
        client = create_gemini_client()

    model = model_name or DEFAULT_MODEL
    user_prompt = build_tailor_prompt(resume_text, job_description)

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": RESUME_TAILOR_SYSTEM_PROMPT + "\n\n" + user_prompt}
                    ],
                }
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=TailorResponse,
            ),
        )

        response_text = response.text.strip() if response.text else ""

        # Strip markdown fences if present
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        data = json.loads(response_text)
        return TailorResponse.model_validate(data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model output as valid JSON: {e}") from e
    except Exception as e:
        # Pass through ValueError so callers can differentiate schema/parsing vs other errors
        if isinstance(e, ValueError):
            raise
        raise RuntimeError(f"Gemini API inference failure: {e}") from e
