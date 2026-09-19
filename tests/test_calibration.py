"""Unit tests for temperature calibration and numerical integrity (CPU only, offline)."""

import json
import math
import os
import tempfile
import pytest
import torch
from erabi.calibrate import (
    compute_file_sha256,
    compute_nll_objective,
    get_checkpoint_hashes,
    optimize_temperature,
)
from erabi.evaluate import compute_softmax
from erabi.__main__ import load_and_verify_calibration


def test_temperature_scaling_preserves_best():
    """Verify that any positive temperature preserves argmax for distinct logits."""
    logits = [2.5, 0.1, -1.2, 4.0]
    expected_best = 3

    for T in [0.1, 0.5, 1.0, 2.0, 5.0, 20.0]:
        probs = compute_softmax(logits, temperature=T)
        best_idx = probs.index(max(probs))
        assert best_idx == expected_best, f"Temperature {T} changed best candidate index!"


def test_temperature_scaling_invalid_values():
    """Verify that non-positive temperatures raise ValueError."""
    logits = [1.0, 2.0]
    with pytest.raises(ValueError):
        compute_softmax(logits, temperature=0.0)
    with pytest.raises(ValueError):
        compute_softmax(logits, temperature=-1.5)


def test_nll_objective_computation():
    """Test float64 log_softmax NLL computation on simple synthetic logits."""
    logits_list = [[10.0, 0.0], [0.0, 10.0]]
    targets = [0, 1]

    # At T=1.0, probability of target is ~1.0, NLL should be very close to 0
    nll_t1 = compute_nll_objective(logits_list, targets, 1.0)
    assert nll_t1 < 1e-3

    # At very high T, logits approach uniform (0.5), NLL should approach ln(2) = ~0.693
    nll_thigh = compute_nll_objective(logits_list, targets, 1000.0)
    assert math.isclose(nll_thigh, math.log(2.0), rel_tol=1e-2)


def test_optimize_temperature_basic():
    """Test temperature optimization on overconfident wrong predictions."""
    # Model is overconfident on wrong choice
    logits_list = [[10.0, 0.0], [10.0, 0.0]]
    targets = [1, 1]  # true target is index 1

    res = optimize_temperature(logits_list, targets, bounds=(0.05, 20.0))
    # Optimal T should be pushed high to flatten the severe penalty
    assert res["optimal_T"] > 1.0
    assert res["optimal_nll"] < res["initial_nll"]


def test_checkpoint_hash_verification():
    """Test checkpoint file hashing and mismatch detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, "config.json")
        f2 = os.path.join(tmpdir, "model.safetensors")
        f3 = os.path.join(tmpdir, "tokenizer.json")
        f4 = os.path.join(tmpdir, "tokenizer_config.json")
        with open(f1, "w", encoding="utf-8") as f:
            f.write('{"model": "test"}')
        with open(f2, "wb") as f:
            f.write(b"fake_weights_bytes_12345")
        with open(f3, "w", encoding="utf-8") as f:
            f.write('{"tokenizer": "test"}')
        with open(f4, "w", encoding="utf-8") as f:
            f.write('{"tokenizer_config": "test"}')

        hashes = get_checkpoint_hashes(tmpdir)
        assert "config.json" in hashes
        assert "model.safetensors" in hashes
        assert "tokenizer.json" in hashes
        assert "tokenizer_config.json" in hashes

        calib_data = {
            "artifact_id": "calib-test-001",
            "status": "applied",
            "temperature": 1.25,
            "target_model": {"files": hashes},
            "contract": {
                "schema_version": "1",
                "max_tokens": 512,
                "formatter_version": "m1_instruct_pipe_v1",
                "precision": "float32_forward_float64_nll",
            },
        }
        calib_file = os.path.join(tmpdir, "calibration.json")
        with open(calib_file, "w", encoding="utf-8") as f:
            json.dump(calib_data, f)

        # Successful load
        temp, calib_out, _ = load_and_verify_calibration(calib_file, tmpdir)
        assert temp == 1.25
        assert calib_out.status == "applied"

        # Tamper with file -> mismatch error
        with open(f1, "w", encoding="utf-8") as f:
            f.write('{"model": "tampered"}')

        with pytest.raises(ValueError, match="Calibration hash mismatch"):
            load_and_verify_calibration(calib_file, tmpdir)
