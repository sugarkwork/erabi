"""Evaluation metrics, dataset runner, and run artifact management."""

from __future__ import annotations

import json
import math
import os
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional


def compute_softmax(logits: List[float], temperature: float = 1.0) -> List[float]:
    """Compute softmax over logits with temperature scaling.

    Guarantees numerical stability and returns a proper probability distribution.
    """
    if not math.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("Temperature must be positive and finite.")

    scaled = [z / temperature for z in logits]
    max_val = max(scaled)
    # Prevent overflow
    exp_vals = [math.exp(z - max_val) for z in scaled]
    sum_exp = sum(exp_vals)
    if sum_exp == 0.0 or not math.isfinite(sum_exp):
        raise ValueError("Softmax denominator is non-finite or zero.")

    probs = [v / sum_exp for v in exp_vals]
    return probs


def compute_masked_softmax(
    logits: List[float], mask: List[bool], temperature: float = 1.0
) -> List[float]:
    """Compute softmax over masked positions, setting unmasked positions to 0.0."""
    if not math.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("Temperature must be positive and finite.")
    if len(logits) != len(mask):
        raise ValueError("Logits and mask lengths must match.")

    valid_indices = [i for i, m in enumerate(mask) if m]
    if not valid_indices:
        raise ValueError("At least one candidate must be valid in mask.")

    valid_logits = [logits[i] for i in valid_indices]
    valid_probs = compute_softmax(valid_logits, temperature)

    probs = [0.0] * len(logits)
    for idx, p in zip(valid_indices, valid_probs):
        probs[idx] = p
    return probs


def compute_metrics(
    predictions: List[Dict[str, Any]],
    targets: List[str],
    metadata: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 1.0,
) -> Dict[str, Any]:
    """Compute Accuracy, NLL, Brier score, reliability bins, pair accuracy, and breakdowns.

    Each prediction dict must contain:
      - 'choices': list of {'id': str, 'probability': float}
      - 'best_candidate_id': str
      - 'raw_logits': optional list of raw float logits
    Targets is a list of true choice_ids.
    Optional metadata can contain 'group_id', 'task_family', 'template_family'.
    """
    if len(predictions) != len(targets):
        raise ValueError("Number of predictions and targets must match.")
    if not predictions:
        return {
            "count": 0,
            "accuracy": 0.0,
            "mean_nll": 0.0,
            "mean_brier": 0.0,
            "reliability_bins": [],
        }

    correct_count = 0
    total_nll = 0.0
    total_brier = 0.0
    eps = 1e-12

    # Reliability bins: [0, 0.2), [0.2, 0.4), [0.4, 0.6), [0.6, 0.8), [0.8, 1.0]
    bins = [
        {"bin_range": "[0.0, 0.2)", "low": 0.0, "high": 0.2, "count": 0, "sum_conf": 0.0, "correct": 0},
        {"bin_range": "[0.2, 0.4)", "low": 0.2, "high": 0.4, "count": 0, "sum_conf": 0.0, "correct": 0},
        {"bin_range": "[0.4, 0.6)", "low": 0.4, "high": 0.6, "count": 0, "sum_conf": 0.0, "correct": 0},
        {"bin_range": "[0.6, 0.8)", "low": 0.6, "high": 0.8, "count": 0, "sum_conf": 0.0, "correct": 0},
        {"bin_range": "[0.8, 1.0]", "low": 0.8, "high": 1.0001, "count": 0, "sum_conf": 0.0, "correct": 0},
    ]

    # Tracking for pairs and categories
    group_correct = defaultdict(list)
    task_family_stats = defaultdict(lambda: {"count": 0, "correct": 0})
    template_family_stats = defaultdict(lambda: {"count": 0, "correct": 0})

    if not math.isfinite(temperature) or temperature <= 0.0:
        raise ValueError("Temperature must be positive and finite.")
    temp = temperature

    for idx, (pred, target) in enumerate(zip(predictions, targets)):
        choices = pred["choices"]
        prob_map = {c["id"]: c["probability"] for c in choices}
        best_id = pred["best_candidate_id"]

        is_correct = (best_id == target)
        if is_correct:
            correct_count += 1

        meta = metadata[idx] if metadata and idx < len(metadata) else {}
        gid = meta.get("group_id")
        if gid:
            group_correct[gid].append(is_correct)

        tf = meta.get("task_family")
        if tf:
            task_family_stats[tf]["count"] += 1
            if is_correct:
                task_family_stats[tf]["correct"] += 1

        tpl = meta.get("template_family")
        if tpl:
            template_family_stats[tpl]["count"] += 1
            if is_correct:
                template_family_stats[tpl]["correct"] += 1

        # NLL calculation
        if "raw_logits" in pred and pred["raw_logits"] is not None:
            raw_z = [v / temp for v in pred["raw_logits"]]
            max_z = max(raw_z)
            exp_z = [math.exp(v - max_z) for v in raw_z]
            sum_exp = sum(exp_z)
            choice_ids = [c["id"] for c in choices]
            if target in choice_ids:
                tgt_idx = choice_ids.index(target)
                log_prob = (raw_z[tgt_idx] - max_z) - math.log(sum_exp)
                nll = -log_prob
            else:
                nll = -math.log(eps)
        else:
            target_p = prob_map.get(target, 0.0)
            target_p = max(min(target_p, 1.0), eps)
            nll = -math.log(target_p)
        total_nll += nll

        # Brier score: sum_i (p_i - y_i)^2
        brier = 0.0
        for c in choices:
            y = 1.0 if c["id"] == target else 0.0
            brier += (c["probability"] - y) ** 2
        total_brier += brier

        # Binning by pmax
        pmax = prob_map.get(best_id, 0.0)
        for b in bins:
            if b["low"] <= pmax < b["high"] or (b["high"] > 1.0 and pmax >= 0.8):
                b["count"] += 1
                b["sum_conf"] += pmax
                if is_correct:
                    b["correct"] += 1
                break

    n = len(predictions)
    reliability_results = []
    for b in bins:
        count = b["count"]
        reliability_results.append({
            "bin": b["bin_range"],
            "count": count,
            "avg_confidence": round(b["sum_conf"] / count, 4) if count > 0 else None,
            "accuracy": round(b["correct"] / count, 4) if count > 0 else None,
        })

    # Selective prediction analysis at pre-fixed thresholds
    thresholds = [0.8, 0.9, 0.95]
    selective_metrics = {}
    for tau in thresholds:
        accepted = [
            (p, t) for p, t in zip(predictions, targets)
            if max(c["probability"] for c in p["choices"]) >= tau
        ]
        cov = len(accepted) / n if n > 0 else 0.0
        err_count = sum(1 for p, t in accepted if p["best_candidate_id"] != t)
        risk = (err_count / len(accepted)) if len(accepted) > 0 else None
        selective_metrics[f"tau_{tau}"] = {
            "threshold": tau,
            "accepted_count": len(accepted),
            "coverage": round(cov, 4),
            "error_count": err_count,
            "selective_risk": round(risk, 4) if risk is not None else None,
        }

    res: Dict[str, Any] = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": round(correct_count / n, 4),
        "mean_nll": round(total_nll / n, 4),
        "mean_nll_scientific": f"{total_nll / n:.6e}" if n > 0 else "0.000000e+00",
        "mean_brier": round(total_brier / n, 4),
        "reliability_bins": reliability_results,
        "selective_risk_analysis": selective_metrics,
    }

    # Pair metrics
    if group_correct:
        multi_item_groups = [v for v in group_correct.values() if len(v) > 1]
        if multi_item_groups:
            both_correct_pairs = sum(1 for v in multi_item_groups if all(v))
            res["pair_metrics"] = {
                "total_pairs": len(multi_item_groups),
                "both_correct_pairs": both_correct_pairs,
                "both_correct_rate": round(both_correct_pairs / len(multi_item_groups), 4),
            }

    if task_family_stats:
        res["task_family_breakdown"] = {
            k: {
                "count": v["count"],
                "correct": v["correct"],
                "accuracy": round(v["correct"] / v["count"], 4) if v["count"] > 0 else 0.0,
            }
            for k, v in task_family_stats.items()
        }

    if template_family_stats:
        res["template_family_breakdown"] = {
            k: {
                "count": v["count"],
                "correct": v["correct"],
                "accuracy": round(v["correct"] / v["count"], 4) if v["count"] > 0 else 0.0,
            }
            for k, v in template_family_stats.items()
        }

    return res
