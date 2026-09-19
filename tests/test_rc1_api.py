"""Integration and contract tests for ERABI Release Candidate 1 API."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from erabi.api import create_app
from erabi.schema import MAX_REQUEST_BYTES

ROOT = Path(__file__).resolve().parent.parent
RC_MODEL_DIR = ROOT / "release/rc1/model"
RC_CALIB_PATH = ROOT / "release/rc1/calibration.json"


@pytest.fixture(scope="module")
def rc1_client():
    app = create_app(
        model_id=str(RC_MODEL_DIR),
        calibration_path=str(RC_CALIB_PATH),
        device="cpu",
        require_calibration=True,
    )
    with TestClient(app) as client:
        yield client


def test_rc1_health(rc1_client: TestClient):
    resp = rc1_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["calibration"]["status"] == "applied"
    assert data["calibration"]["artifact_id"] == "calib-rc1-prod"
    assert abs(data["temperature"] - 0.256) < 1e-3
    assert data["decision_policy"] == "review_default"


def test_rc1_predict_contract_and_ordering(rc1_client: TestClient):
    payload = {
        "context": "お客様より『先月の請求書に誤請求があります。返金手続きをお願いします』との連絡。",
        "question": "担当窓口を選択してください。",
        "choices": [
            {"id": "c_billing", "text": "請求・経理窓口"},
            {"id": "c_tech", "text": "技術サポート窓口"},
            {"id": "c_sales", "text": "法人営業窓口"},
        ],
    }
    resp = rc1_client.post("/v1/choice", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    # Best candidate
    assert data["best_candidate_id"] == "c_billing"

    # Review default policy
    assert data["decision"]["status"] == "review"

    # Raw order preservation
    choice_ids = [c["id"] for c in data["choices"]]
    assert choice_ids == ["c_billing", "c_tech", "c_sales"]

    # Probability sum == 1.0
    p_sum = sum(c["probability"] for c in data["choices"])
    assert abs(p_sum - 1.0) < 1e-4

    # Calibration output
    assert data["calibration"]["status"] == "applied"
    assert data["calibration"]["artifact_id"] == "calib-rc1-prod"


def test_rc1_request_too_large(rc1_client: TestClient):
    large_context = "A" * (MAX_REQUEST_BYTES + 100)
    payload = {
        "context": large_context,
        "question": "選択してください。",
        "choices": [
            {"id": "c1", "text": "選択肢1"},
            {"id": "c2", "text": "選択肢2"},
        ],
    }
    resp = rc1_client.post("/v1/choice", json=payload)
    assert resp.status_code == 413


def test_rc1_validation_error(rc1_client: TestClient):
    # Missing choices
    payload = {
        "context": "テストコンテキスト",
        "question": "質問文",
        "choices": [{"id": "c1", "text": "選択肢1"}],  # < 2 choices
    }
    resp = rc1_client.post("/v1/choice", json=payload)
    assert resp.status_code == 422
