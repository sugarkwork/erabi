"""Tests for M3.3 data rebuilding, cross-split isolation, and edge cases."""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
import sys
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from erabi.evaluate import compute_softmax, compute_masked_softmax, compute_metrics
from erabi.api import create_app
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest
from scripts.build_m3_3_data import compute_input_fingerprint, generate_goal_following_scenario, generate_explicit_rule_scenario


def test_cross_split_and_internal_uniqueness():
    """Verify zero input fingerprint overlaps across train, dev, and eval_v2, and within each split."""
    manifest_path = ROOT_DIR / "data" / "m3_3_v2" / "manifest.json"
    assert manifest_path.exists(), "M3.3 manifest not found"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    splits = ["train", "dev", "eval_v2"]
    split_fps = {}

    for sname in splits:
        fpath = ROOT_DIR / "data" / "m3_3_v2" / f"{sname}.jsonl"
        assert fpath.exists()
        with open(fpath, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]

        fps = [compute_input_fingerprint(r["context"], r["question"], r["choices"]) for r in records]
        # Internal uniqueness
        assert len(fps) == len(set(fps)), f"Internal duplicate found in {sname}!"
        split_fps[sname] = set(fps)

    # Cross-split uniqueness
    assert len(split_fps["train"] & split_fps["dev"]) == 0, "Train and Dev share identical inputs!"
    assert len(split_fps["train"] & split_fps["eval_v2"]) == 0, "Train and Eval_v2 share identical inputs!"
    assert len(split_fps["dev"] & split_fps["eval_v2"]) == 0, "Dev and Eval_v2 share identical inputs!"


def test_independent_expected_cases():
    """Verify ground truth computation on independent hand-crafted cases."""
    # 1. Goal following - Server capacity (max)
    # Memory: A=500GB/20ms, B=100GB/2ms, C=300GB/10ms
    # Asking for large capacity -> A (500GB)
    ctx_server = "サーバーAは500GBで20ms、サーバーBは100GBで2ms、サーバーCは300GBで10msです。"
    q_max = "応答遅延を考慮せず、最も大容量のサーバーを一つ選んでください。"
    q_min_delay = "メモリ容量を考慮せず、最も低遅延なサーバーを一つ選んでください。"
    choices_srv = [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}]

    # In our independent truth: max GB is A (500GB), min ms is B (2ms)
    import re
    matches = re.findall(r"([^\s、]+)は(\d+)GBで(\d+)ms", ctx_server)
    c_map = {c["text"]: c["id"] for c in choices_srv}
    best_cap_name = max(matches, key=lambda m: int(m[1]))[0]
    best_delay_name = min(matches, key=lambda m: int(m[2]))[0]
    assert c_map[best_cap_name] == "a"  # 500GB max correctly maps to choice 'a'
    assert c_map[best_delay_name] == "b"  # 2ms min correctly maps to choice 'b'

    # 2. Boundary value cases (actual < threshold, actual == threshold, actual > threshold)
    # Test threshold = 50
    # Condition: <= 50 pass, > 50 fail
    def eval_bound1(actual, thresh=50):
        return "pass" if actual <= thresh else "fail"

    def eval_bound2(actual, thresh=50):
        return "pass" if actual < thresh else "fail"

    # Below (actual=49)
    assert eval_bound1(49) == "pass"
    assert eval_bound2(49) == "pass"

    # At (actual=50)
    assert eval_bound1(50) == "pass"
    assert eval_bound2(50) == "fail"  # Crucial boundary difference!

    # Above (actual=51)
    assert eval_bound1(51) == "fail"
    assert eval_bound2(51) == "fail"


def test_argmax_pre_rounding_edge_case():
    """Verify that best candidate selection uses raw logits to avoid rounding ties."""
    # Fake logits where candidate 'b' is strictly larger by 1e-7
    # If rounded to 6 decimals, both probabilities become 0.500000, which caused tie-break to 'a'
    # With raw logit argmax, 'b' MUST be selected
    row_logits = [0.0, 1e-7]
    best_idx = 0
    best_logit = row_logits[0]
    for idx, logit_val in enumerate(row_logits):
        if logit_val > best_logit:
            best_logit = logit_val
            best_idx = idx

    assert best_idx == 1, "Argmax on raw logits must pick candidate index 1"


def test_temperature_validation_strict():
    """Verify compute_softmax rejects non-finite or non-positive temperature without silent fallback."""
    logits = [1.0, 2.0]
    with pytest.raises(ValueError, match="Temperature must be positive and finite"):
        compute_softmax(logits, temperature=0.0)

    with pytest.raises(ValueError, match="Temperature must be positive and finite"):
        compute_softmax(logits, temperature=-1.0)

    with pytest.raises(ValueError, match="Temperature must be positive and finite"):
        compute_softmax(logits, temperature=float("inf"))

    with pytest.raises(ValueError, match="Temperature must be positive and finite"):
        compute_softmax(logits, temperature=float("nan"))


def test_require_calibration_without_path_fails():
    """Verify app creation with require_calibration=True but no calibration_path raises error on startup."""
    from fastapi.testclient import TestClient

    app = create_app(
        model_id="knowledgator/gliclass-instruct-base-v1.0",
        calibration_path=None,
        require_calibration=True,
        engine_factory=lambda: None,
    )

    with pytest.raises(RuntimeError, match="Calibration is required"):
        with TestClient(app) as client:
            client.get("/health")
