"""Unit tests for prompt construction and system instructions."""

from prompts import build_tailor_prompt, RESUME_TAILOR_SYSTEM_PROMPT


def test_build_prompt_contains_inputs():
    """Verifies that build_tailor_prompt properly interpolates both inputs."""
    resume_text = "• Architected high-throughput notification system using Go."
    job_description = "Staff Software Engineer with deep expertise in distributed architectures."

    prompt = build_tailor_prompt(resume_text, job_description)

    assert resume_text in prompt
    assert job_description in prompt
    assert "Target Job Description:" in prompt
    assert "Candidate's Current Resume Experience:" in prompt


def test_system_prompt_rules_integrity():
    """Verifies that the system prompt contains anti-hallucination and format rules."""
    assert "Strict Truth & Anti-Hallucination" in RESUME_TAILOR_SYSTEM_PROMPT
    assert "Google XYZ Formula" in RESUME_TAILOR_SYSTEM_PROMPT
    assert "JSON" in RESUME_TAILOR_SYSTEM_PROMPT
