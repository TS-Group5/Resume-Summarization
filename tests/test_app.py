import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_docs_endpoint():
    """Test that the OpenAPI docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_metrics_endpoint():
    """Test that the metrics endpoint returns Prometheus metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert (
        response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
    )


def test_generate_script_validation():
    """Test that the generate-script endpoint validates input."""
    response = client.post("/generate-script")
    assert (
        response.status_code == 422
    )  # Unprocessable Entity due to missing required fields
