"""Unit tests for Pydantic input/output validation models."""

import pytest
from pydantic import ValidationError
from prompts import TailorRequest, TailoredBullet, TailorResponse


def test_validate_input_valid():
    """Verifies that TailorRequest accepts valid inputs within length constraints (20-10,000 chars)."""
    valid_resume = "• Engineered high-performance event notification microservices in Go."
    valid_job = "Seeking Senior Distributed Systems Engineer with Go and AWS experience."

    req = TailorRequest(resume_text=valid_resume, job_description=valid_job)
    assert req.resume_text == valid_resume
    assert req.job_description == valid_job


def test_validate_input_too_short():
    """Verifies that inputs shorter than 20 characters raise a validation error."""
    # Test resume_text too short
    with pytest.raises(ValidationError) as exc_info:
        TailorRequest(
            resume_text="Too short",
            job_description="Valid job description with sufficient length for testing requirements.",
        )
    assert "resume_text" in str(exc_info.value)

    # Test job_description too short
    with pytest.raises(ValidationError) as exc_info:
        TailorRequest(
            resume_text="Valid resume bullet with sufficient length for testing requirements.",
            job_description="Short job",
        )
    assert "job_description" in str(exc_info.value)


def test_validate_input_too_long():
    """Verifies that inputs exceeding 10,000 characters are rejected with a clear validation error."""
    oversized_text = "a" * 10001
    valid_text = "Valid text for testing constraints with plenty of characters."

    with pytest.raises(ValidationError) as exc_info:
        TailorRequest(
            resume_text=oversized_text,
            job_description=valid_text,
        )
    assert "resume_text" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        TailorRequest(
            resume_text=valid_text,
            job_description=oversized_text,
        )
    assert "job_description" in str(exc_info.value)


def test_tailor_response_pydantic_parsing():
    """Verifies that a valid Gemini JSON dictionary successfully parses into TailorResponse."""
    raw_data = {
        "role_title_detected": "Staff Distributed Systems Engineer",
        "bullets": [
            {
                "bullet": "Architected Go-based event streaming pipeline processing 10k events/sec.",
                "skill_tag": "Distributed Systems",
                "original_reference": "Built notifications microservice",
            },
            {
                "bullet": "Optimized AWS Aurora queries, reducing p99 database latency by 45%.",
                "skill_tag": "AWS & Database Tuning",
                "original_reference": "Reduced database latency on AWS",
            },
        ],
        "key_keywords_aligned": ["Go", "Kafka", "AWS", "Aurora"],
    }

    response = TailorResponse.model_validate(raw_data)
    assert response.role_title_detected == "Staff Distributed Systems Engineer"
    assert len(response.bullets) == 2
    assert response.bullets[0].skill_tag == "Distributed Systems"
    assert response.bullets[0].original_reference == "Built notifications microservice"
    assert "Go" in response.key_keywords_aligned
