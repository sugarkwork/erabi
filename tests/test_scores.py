"""Unit tests for softmax, masked softmax, and evaluation metrics."""

import math
import pytest
from erabi.evaluate import compute_masked_softmax, compute_metrics, compute_softmax


def test_softmax_basic():
    logits = [1.0, 1.0, 1.0]
    probs = compute_softmax(logits)
    assert len(probs) == 3
    assert abs(sum(probs) - 1.0) < 1e-6
    for p in probs:
        assert abs(p - 1.0 / 3.0) < 1e-6


def test_softmax_temperature():
    logits = [2.0, 1.0]
    p_t1 = compute_softmax(logits, temperature=1.0)
    p_t2 = compute_softmax(logits, temperature=2.0)
    p_t05 = compute_softmax(logits, temperature=0.5)

    # Higher temperature -> more uniform (closer to 0.5)
    assert abs(p_t2[0] - 0.5) < abs(p_t1[0] - 0.5)
    # Lower temperature -> more peaked (closer to 1.0)
    assert p_t05[0] > p_t1[0]


def test_softmax_numerical_stability():
    # Large logits that would overflow exp() without max subtraction
    logits = [1000.0, 1001.0, 999.0]
    probs = compute_softmax(logits)
    assert abs(sum(probs) - 1.0) < 1e-6
    assert probs[1] > probs[0] > probs[2]
    for p in probs:
        assert math.isfinite(p)


def test_masked_softmax():
    logits = [2.0, 5.0, 10.0]
    mask = [True, True, False]  # 3rd is padding
    probs = compute_masked_softmax(logits, mask)
    assert len(probs) == 3
    assert probs[2] == 0.0
    assert abs(sum(probs) - 1.0) < 1e-6
    # Only logits[0] and logits[1] participate
    expected_p = compute_softmax([2.0, 5.0])
    assert abs(probs[0] - expected_p[0]) < 1e-6
    assert abs(probs[1] - expected_p[1]) < 1e-6


def test_compute_metrics_perfect_predictions():
    predictions = [
        {"choices": [{"id": "a", "probability": 0.9}, {"id": "b", "probability": 0.1}], "best_candidate_id": "a"},
        {"choices": [{"id": "a", "probability": 0.2}, {"id": "b", "probability": 0.8}], "best_candidate_id": "b"},
    ]
    targets = ["a", "b"]
    metrics = compute_metrics(predictions, targets)

    assert metrics["count"] == 2
    assert metrics["accuracy"] == 1.0
    # NLL = (-log(0.9) + -log(0.8)) / 2
    expected_nll = (-math.log(0.9) - math.log(0.8)) / 2.0
    assert abs(metrics["mean_nll"] - round(expected_nll, 4)) < 1e-3
    # Brier = ( ((0.9-1)^2 + (0.1-0)^2) + ((0.2-0)^2 + (0.8-1)^2) ) / 2
    #       = ( (0.01 + 0.01) + (0.04 + 0.04) ) / 2 = (0.02 + 0.08) / 2 = 0.05
    assert abs(metrics["mean_brier"] - 0.05) < 1e-3


def test_compute_metrics_all_wrong():
    predictions = [
        {"choices": [{"id": "a", "probability": 0.9}, {"id": "b", "probability": 0.1}], "best_candidate_id": "a"},
    ]
    targets = ["b"]
    metrics = compute_metrics(predictions, targets)

    assert metrics["count"] == 1
    assert metrics["accuracy"] == 0.0
    # NLL for target b with prob 0.1: -log(0.1) ~ 2.3026
    assert abs(metrics["mean_nll"] - round(-math.log(0.1), 4)) < 1e-3
    # Brier: (0.9-0)^2 + (0.1-1)^2 = 0.81 + 0.81 = 1.62
    assert abs(metrics["mean_brier"] - 1.62) < 1e-3


def test_compute_metrics_nan_prevention_on_zero_probability():
    predictions = [
        {"choices": [{"id": "a", "probability": 1.0}, {"id": "b", "probability": 0.0}], "best_candidate_id": "a"},
    ]
    targets = ["b"]  # target has 0.0 prob
    metrics = compute_metrics(predictions, targets)
    assert math.isfinite(metrics["mean_nll"])
    assert math.isfinite(metrics["mean_brier"])
