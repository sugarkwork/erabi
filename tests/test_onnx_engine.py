"""Unit tests for ERABI ONNX Engine (tests/test_onnx_engine.py)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.onnx_engine import ERABIONNXEngine
from erabi.schema import ChoiceRequest, ValidationError

ONNX_FP16_DIR = ROOT / "release/erabi-rc1-onnx-fp16"
ONNX_FP32_DIR = ROOT / "release/rc1_onnx"


@pytest.fixture(scope="module")
def onnx_engine():
    # Use GPU if available, else CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    target_dir = ONNX_FP16_DIR if (torch.cuda.is_available() and ONNX_FP16_DIR.exists()) else ONNX_FP32_DIR
    return ERABIONNXEngine(str(target_dir), device=device)


def test_onnx_engine_initialization(onnx_engine):
    assert onnx_engine.session is not None
    assert len(onnx_engine.active_providers) > 0


def test_onnx_engine_inference_contracts(onnx_engine):
    req = ChoiceRequest.from_dict({
        "context": "物流拠点SEALED：製品『SEALED-ITEM-001』の保管在庫数はちょうど110個です。出荷検査証を受領済みです。",
        "question": "数量が110を下回らない（110を含む）場合は出荷する、欠落していれば保留するを適用してください。",
        "choices": [
            {"id": "ship", "text": "出荷する"},
            {"id": "hold", "text": "保留する"},
        ]
    })

    resp = onnx_engine.predict(req, temperature=0.256, return_logits=True)

    # 1. Output order matches request order
    assert [c.id for c in resp.choices] == ["ship", "hold"]

    # 2. Probabilities sum to 1.0
    prob_sum = sum(c.probability for c in resp.choices)
    assert abs(prob_sum - 1.0) < 1e-6

    # 3. Decision status is review
    assert resp.decision.status == "review"

    # 4. Top-1 decision is ship
    assert resp.best_candidate_id == "ship"

    # 5. Raw logits returned
    assert resp.raw_logits is not None
    assert len(resp.raw_logits) == 2
    assert resp.raw_logits[0] > resp.raw_logits[1]


def test_onnx_engine_permutation_invariance(onnx_engine):
    req_orig = ChoiceRequest.from_dict({
        "context": "物流拠点SEALED：製品『SEALED-ITEM-001』の保管在庫数はちょうど110個です。出荷検査証を受領済みです。",
        "question": "数量が110を下回らない（110を含む）場合は出荷する、欠落していれば保留するを適用してください。",
        "choices": [
            {"id": "ship", "text": "出荷する"},
            {"id": "hold", "text": "保留する"},
        ]
    })
    req_rev = ChoiceRequest.from_dict({
        "context": "物流拠点SEALED：製品『SEALED-ITEM-001』の保管在庫数はちょうど110個です。出荷検査証を受領済みです。",
        "question": "数量が110を下回らない（110を含む）場合は出荷する、欠落していれば保留するを適用してください。",
        "choices": [
            {"id": "hold", "text": "保留する"},
            {"id": "ship", "text": "出荷する"},
        ]
    })

    resp_orig = onnx_engine.predict(req_orig, temperature=0.256)
    resp_rev = onnx_engine.predict(req_rev, temperature=0.256)

    assert resp_orig.best_candidate_id == resp_rev.best_candidate_id == "ship"
    assert [c.id for c in resp_rev.choices] == ["hold", "ship"]


def test_onnx_engine_token_limit_validation(onnx_engine):
    # Context exceeding 512 tokens must fail closed with ValidationError
    huge_context = "これは非常に長いテキストです。" * 300
    req = ChoiceRequest.from_dict({
        "context": huge_context,
        "question": "質問です。",
        "choices": [
            {"id": "c1", "text": "選択肢1"},
            {"id": "c2", "text": "選択肢2"},
        ]
    })

    with pytest.raises(ValidationError) as excinfo:
        onnx_engine.predict(req)

    assert excinfo.value.code == "input_too_long"
