"""Unit tests for ERABI local HTTP API server contracts (CPU only, offline)."""

import asyncio
import json
import pytest
from erabi.api import create_app
from erabi.schema import (
    ChoiceOutput,
    ChoiceRequest,
    ChoiceResponse,
    CalibrationOutput,
    DecisionOutput,
    UsageOutput,
)
from fastapi.testclient import TestClient


class FakeEngine:
    def __init__(self, model_id: str = "fake-model"):
        self.model_id = model_id

    def predict(self, req: ChoiceRequest, temperature: float = 1.0, return_logits: bool = False, calibration=None) -> ChoiceResponse:
        n = len(req.choices)
        prob = round(1.0 / n, 6)
        choice_outputs = [ChoiceOutput(id=c.id, probability=prob) for c in req.choices]
        return ChoiceResponse(
            schema_version="1",
            model_id=self.model_id,
            choices=choice_outputs,
            best_candidate_id=req.choices[0].id,
            decision=DecisionOutput(status="review", reason="policy_not_configured"),
            calibration=calibration or CalibrationOutput(status="none", artifact_id=None),
            usage=UsageOutput(input_tokens=42, truncated=False),
        )


@pytest.fixture
def client():
    app = create_app(
        model_id="fake-model",
        engine_factory=lambda: FakeEngine("fake-model"),
    )
    with TestClient(app) as test_client:
        yield test_client


def test_api_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_id"] == "fake-model"
    assert data["decision_policy"] == "review_default"


def test_api_predict_valid_request(client):
    payload = {
        "context": "プランAは100円、プランBは200円です。",
        "question": "安いプランを選んでください。",
        "choices": [
            {"id": "a", "text": "プランA"},
            {"id": "b", "text": "プランB"},
        ],
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["schema_version"] == "1"
    assert data["best_candidate_id"] == "a"
    assert len(data["choices"]) == 2
    assert data["choices"][0]["id"] == "a"
    assert data["choices"][1]["id"] == "b"

    # Strictly verify decision is review locked
    assert data["decision"]["status"] == "review"
    assert data["decision"]["reason"] == "policy_not_configured"


def test_api_validation_error_422(client):
    # Only 1 choice provided (violates min 2 choices)
    payload = {
        "context": "文脈",
        "question": "質問",
        "choices": [{"id": "single", "text": "一つだけ"}],
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"] == "invalid_choice_count"


def test_api_request_too_large_413(client):
    # Create request exceeding 65,536 bytes
    large_context = "A" * 70000
    payload = {
        "context": large_context,
        "question": "質問",
        "choices": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
    }
    raw_bytes = json.dumps(payload).encode("utf-8")
    response = client.post(
        "/predict",
        content=raw_bytes,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413


def test_api_concurrency_lock_503(client):
    app = client.app
    # Manually lock the async lock to simulate in-flight inference
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.state.lock.acquire())

    payload = {
        "context": "文脈",
        "question": "質問",
        "choices": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 503
    assert "Engine busy" in response.json()["detail"]

    # Release lock
    app.state.lock.release()
