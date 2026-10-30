"""Integration tests for FastAPI endpoints with mocked Gemini AI interactions."""

from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from prompts import TailorResponse, TailoredBullet

client = TestClient(app)


def test_health_endpoint():
    """Simulates GET /api/health asserting status 200 and expected health metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok", "version": "1.0.0"}


def test_tailor_endpoint_happy_path():
    """Simulates POST /api/tailor with valid payload, mocking Gemini AI with deterministic output."""
    mock_tailor_response = TailorResponse(
        role_title_detected="Senior Staff Distributed Systems Engineer",
        bullets=[
            TailoredBullet(
                bullet="Architected Go-based event streaming pipeline processing 15,000 RPS with 99.99% reliability.",
                skill_tag="Distributed Systems & Go",
                original_reference="Built backend notifications microservice",
            ),
            TailoredBullet(
                bullet="Spearheaded cloud migration from on-prem to AWS, slashing p99 query latency by 42%.",
                skill_tag="AWS Cloud Modernization",
                original_reference="Led cloud migration to AWS",
            ),
            TailoredBullet(
                bullet="Partnered with product stakeholders to deliver 12 core platform features across bi-weekly sprints.",
                skill_tag="Cross-Functional Leadership",
                original_reference="Collaborated with product managers",
            ),
        ],
        key_keywords_aligned=["Go", "Kafka", "AWS", "High-Throughput", "Distributed Systems"],
    )

    with patch("main.tailor_resume", new_callable=AsyncMock) as mock_tailor:
        mock_tailor.return_value = mock_tailor_response

        payload = {
            "resume_text": "• Built backend notifications microservice using Go and Kafka.\n• Led cloud migration to AWS, cutting latency.\n• Collaborated with product managers.",
            "job_description": "Seeking a Senior Staff Distributed Systems Engineer with Go, Kafka, and AWS cloud expertise.",
        }

        response = client.post("/api/tailor", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["role_title_detected"] == "Senior Staff Distributed Systems Engineer"
        assert len(data["bullets"]) == 3
        assert data["bullets"][0]["skill_tag"] == "Distributed Systems & Go"
        assert "Go" in data["key_keywords_aligned"]
        mock_tailor.assert_called_once()


def test_tailor_endpoint_validation_error():
    """Simulates POST /api/tailor with invalid/short payload asserting HTTP 422."""
    payload = {
        "resume_text": "Short",
        "job_description": "Also short",
    }
    response = client.post("/api/tailor", json=payload)
    assert response.status_code == 422


def test_tailor_endpoint_gemini_error_handling():
    """Simulates POST /api/tailor when Gemini client raises an inference failure, asserting HTTP 500."""
    with patch("main.tailor_resume", new_callable=AsyncMock) as mock_tailor:
        mock_tailor.side_effect = RuntimeError("ResourceExhausted: 429 Rate limit exceeded")

        payload = {
            "resume_text": "• Built backend notifications microservice using Go and Kafka.\n• Led cloud migration to AWS.",
            "job_description": "Seeking a Senior Staff Distributed Systems Engineer with Go, Kafka, and AWS cloud expertise.",
        }

        response = client.post("/api/tailor", json=payload)
        assert response.status_code == 500
        data = response.json()
        assert "AI inference error" in data["detail"]
        assert "ResourceExhausted" in data["detail"]


def test_tailor_endpoint_missing_api_key_handling():
    """Simulates POST /api/tailor when GEMINI_API_KEY is not configured, asserting HTTP 503."""
    with patch("main.tailor_resume", new_callable=AsyncMock) as mock_tailor:
        mock_tailor.side_effect = ValueError(
            "GEMINI_API_KEY environment variable is not configured. Please set it in your .env file or environment."
        )

        payload = {
            "resume_text": "• Built backend notifications microservice using Go and Kafka.\n• Led cloud migration to AWS.",
            "job_description": "Seeking a Senior Staff Distributed Systems Engineer with Go, Kafka, and AWS cloud expertise.",
        }

        response = client.post("/api/tailor", json=payload)
        assert response.status_code == 503
        data = response.json()
        assert "GEMINI_API_KEY" in data["detail"]
