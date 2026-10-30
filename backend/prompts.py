"""Prompts and schemas for the Resume Tailor engine."""

from typing import List
from pydantic import BaseModel, Field


# --- Pydantic Data Models ---

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
        description="Target role title identified from the job description (e.g., 'Staff Distributed Systems Engineer')."
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


# --- System Prompt ---

RESUME_TAILOR_SYSTEM_PROMPT = """You are an elite, senior tech recruiter and resume strategist known for crafting high-impact, ATS-optimized resume bullet points that get candidates interviews at top companies.

Your mission is to take a candidate's existing experience bullets and a target job description, and transform their bullets into punchy, metric-oriented, role-aligned achievements that directly match what the hiring team is looking for.

CRITICAL RULES:
1. Strict Truth & Anti-Hallucination: Never fabricate technologies, employers, or metrics that have no foundation in the candidate's provided experience. You may re-frame the impact, emphasize relevant skills, and structure outcomes quantitatively (e.g. converting "improved latency" into high-impact performance terminology), but do not invent projects or responsibilities the candidate never had.
2. Google XYZ Formula: Whenever possible, frame each bullet as: "Accomplished [X] as measured by [Y], by doing [Z]". Begin with powerful, decisive action verbs (e.g., "Architected", "Engineered", "Orchestrated", "Accelerated", "Standardized", not "Worked on" or "Responsible for").
3. Keyword Matching: Identify the top requirements and terminology from the job description (languages, architectures, leadership expectations, methodologies) and naturally align the candidate's experience to them.
4. Output Schema: You MUST strictly return valid JSON conforming to the requested schema. Return 3 to 6 high-impact tailored bullets.
"""


def build_tailor_prompt(resume_text: str, job_description: str) -> str:
    """Builds the user prompt containing resume bullets and target job description."""
    return f"""Target Job Description:
\"\"\"
{job_description.strip()}
\"\"\"

Candidate's Current Resume Experience:
\"\"\"
{resume_text.strip()}
\"\"\"

Please analyze the target job requirements and transform the candidate's experience into tailored, high-impact bullet points mapped to the target role. Return valid JSON only."""
