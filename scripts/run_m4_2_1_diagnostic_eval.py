"""Run M4.2.1 Factorial Diagnostic (Domain x Phrasing 2x2).

Evaluates:
1. Baseline: W_v2_ce10 (runs/m3_5_ce10/trained/checkpoint)
2. Experiment: W_m4_1 (runs/m4_1_exception/trained/checkpoint)

Across 4 factorial cells at strictly T=1.0:
- Cell A: OLD Domain + OLD Phrasing (data/m4_2_1_diagnostic/cell_a_old_domain_old_phrasing.jsonl)
- Cell B: OLD Domain + NEW Phrasing (data/m4_2_1_diagnostic/cell_b_old_domain_new_phrasing.jsonl)
- Cell C: NEW Domain + OLD Phrasing (data/m4_2_1_diagnostic/cell_c_new_domain_old_phrasing.jsonl)
- Cell D: NEW Domain + NEW Phrasing (data/m4_2_robustness/novel_priority_eval.jsonl)

Outputs to runs/m4_2_1_diagnostic/:
- Individual predictions for each cell and model
- diagnostic_summary.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

OUT_DIR = ROOT / "runs/m4_2_1_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_MODEL = str(ROOT / "runs/m3_5_ce10/trained/checkpoint")
EXPERIMENT_MODEL = str(ROOT / "runs/m4_1_exception/trained/checkpoint")

CELL_DATASETS = {
    "cell_a": ROOT / "data/m4_2_1_diagnostic/cell_a_old_domain_old_phrasing.jsonl",
    "cell_b": ROOT / "data/m4_2_1_diagnostic/cell_b_old_domain_new_phrasing.jsonl",
    "cell_c": ROOT / "data/m4_2_1_diagnostic/cell_c_new_domain_old_phrasing.jsonl",
    "cell_d": ROOT / "data/m4_2_robustness/novel_priority_eval.jsonl",
}


def evaluate_records(
    engine: GLiClassEngine, records: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

    for row in records:
        req = ChoiceRequest.from_dict(row)
        tgt_cid = row["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        resp = engine.predict(req, temperature=1.0, return_logits=True)
        raw_logits = resp.raw_logits
        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        probs = [c.probability for c in resp.choices]
        log_probs = F.log_softmax(torch.tensor(raw_logits, dtype=torch.float64), dim=-1)
        nll_val = -float(log_probs[tgt_idx].item())
        total_nll += nll_val

        brier_val = sum((p - (1.0 if i == tgt_idx else 0.0)) ** 2 for i, p in enumerate(probs))
        total_brier += brier_val

        res_item = {
            "id": row.get("id"),
            "group_id": row.get("group_id"),
            "cell": row.get("cell"),
            "template_family": row.get("template_family"),
            "phrasing_family": row.get("phrasing_family"),
            "stratum": row.get("stratum"),
            "conflict": row.get("conflict"),
            "priority_order": row.get("priority_order"),
            "target": tgt_cid,
            "target_index": tgt_idx,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "probabilities": probs,
            "raw_logits": raw_logits,
            "nll": nll_val,
            "brier": brier_val,
        }
        results.append(res_item)

    n = len(records)
    metrics: Dict[str, Any] = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
        "mean_brier": total_brier / n,
    }

    # Pair metrics
    groups: Dict[str, List[int]] = {}
    for i, r in enumerate(results):
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(i)

    paired_groups = {k: v for k, v in groups.items() if len(v) == 2}
    both_correct = 0
    diff_pairs = 0
    diff_both = 0
    diff_unswitched = 0
    diff_switched_wrong = 0
    same_pairs = 0
    same_both = 0

    for gid, indices in paired_groups.items():
        r1, r2 = results[indices[0]], results[indices[1]]
        is_both = r1["is_correct"] and r2["is_correct"]
        if is_both:
            both_correct += 1

        is_diff = (r1["target"] != r2["target"])
        if is_diff:
            diff_pairs += 1
            if is_both:
                diff_both += 1
            else:
                p1, p2 = r1["predicted"], r2["predicted"]
                if p1 == p2:
                    diff_unswitched += 1
                else:
                    diff_switched_wrong += 1
        else:
            same_pairs += 1
            if is_both:
                same_both += 1

    metrics["pair_stats"] = {
        "total_pairs": len(paired_groups),
        "both_correct": both_correct,
        "both_rate": both_correct / len(paired_groups) if len(paired_groups) > 0 else 0.0,
        "diff_target_pairs": diff_pairs,
        "diff_target_both": diff_both,
        "diff_target_rate": (diff_both / diff_pairs) if diff_pairs > 0 else 0.0,
        "diff_unswitched": diff_unswitched,
        "diff_unswitched_rate": (diff_unswitched / diff_pairs) if diff_pairs > 0 else 0.0,
        "diff_switched_wrong": diff_switched_wrong,
        "diff_switched_wrong_rate": (diff_switched_wrong / diff_pairs) if diff_pairs > 0 else 0.0,
        "same_target_pairs": same_pairs,
        "same_target_both": same_both,
        "same_target_rate": (same_both / same_pairs) if same_pairs > 0 else 0.0,
    }

    return results, metrics


def main():
    print("=" * 75)
    print("ERABI M4.2.1 Factorial Diagnostic: Domain x Phrasing 2x2 Evaluation")
    print("=" * 75)
    print(f"Baseline: {BASELINE_MODEL}")
    print(f"Experiment: {EXPERIMENT_MODEL}")

    # Load records for all cells
    datasets_records: Dict[str, List[Dict[str, Any]]] = {}
    for cell_key, path in CELL_DATASETS.items():
        recs = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
        datasets_records[cell_key] = recs

    # Also make a matched 20-pair slice for Cell D (first 12 conflict, 8 same)
    d_recs = datasets_records["cell_d"]
    d_pairs = {}
    for r in d_recs:
        d_pairs.setdefault(r["group_id"], []).append(r)
    d_conflict_pairs = [p for p in d_pairs.values() if p[0]["conflict"]][:12]
    d_same_pairs = [p for p in d_pairs.values() if not p[0]["conflict"]][:8]
    matched_cell_d_records = []
    for p in d_conflict_pairs + d_same_pairs:
        matched_cell_d_records.extend(p)
    datasets_records["cell_d_matched20"] = matched_cell_d_records

    all_eval_keys = ["cell_a", "cell_b", "cell_c", "cell_d", "cell_d_matched20"]

    # 1. Run Baseline (W_v2_ce10)
    print("\n--- Evaluating Baseline (W_v2_ce10) ---")
    base_engine = GLiClassEngine(model_id=BASELINE_MODEL, device="cuda" if torch.cuda.is_available() else "cpu")
    baseline_cell_results = {}
    for key in all_eval_keys:
        t0 = time.time()
        res_items, metrics = evaluate_records(base_engine, datasets_records[key])
        baseline_cell_results[key] = {"metrics": metrics, "predictions": res_items}
        print(f"  {key:<18}: Acc={metrics['accuracy']*100:5.1f}% | DiffBoth={metrics['pair_stats']['diff_target_both']:2d}/{metrics['pair_stats']['diff_target_pairs']:2d} ({metrics['pair_stats']['diff_target_rate']*100:5.1f}%) | NLL={metrics['mean_nll']:.4f} ({time.time()-t0:.1f}s)")
        # Save predictions
        with open(OUT_DIR / f"baseline_{key}_predictions.jsonl", "w", encoding="utf-8") as f:
            for item in res_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    del base_engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # 2. Run Experiment (W_m4_1)
    print("\n--- Evaluating Experiment (W_m4_1) ---")
    exp_engine = GLiClassEngine(model_id=EXPERIMENT_MODEL, device="cuda" if torch.cuda.is_available() else "cpu")
    experiment_cell_results = {}
    for key in all_eval_keys:
        t0 = time.time()
        res_items, metrics = evaluate_records(exp_engine, datasets_records[key])
        experiment_cell_results[key] = {"metrics": metrics, "predictions": res_items}
        print(f"  {key:<18}: Acc={metrics['accuracy']*100:5.1f}% | DiffBoth={metrics['pair_stats']['diff_target_both']:2d}/{metrics['pair_stats']['diff_target_pairs']:2d} ({metrics['pair_stats']['diff_target_rate']*100:5.1f}%) | NLL={metrics['mean_nll']:.4f} ({time.time()-t0:.1f}s)")
        # Save predictions
        with open(OUT_DIR / f"experiment_{key}_predictions.jsonl", "w", encoding="utf-8") as f:
            for item in res_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    del exp_engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # 3. Compile Diagnostic Summary
    summary = {
        "description": "M4.2.1 Factorial Diagnostic 2x2: Domain x Phrasing",
        "baseline_model": BASELINE_MODEL,
        "experiment_model": EXPERIMENT_MODEL,
        "cells": {
            "cell_a": {"domain": "OLD", "phrasing": "OLD", "description": "Control (Old Domain + Old Phrasing)"},
            "cell_b": {"domain": "OLD", "phrasing": "NEW", "description": "Phrasing Shift Only (Old Domain + New Phrasing)"},
            "cell_c": {"domain": "NEW", "phrasing": "OLD", "description": "Domain Shift Only (New Domain + Old Phrasing)"},
            "cell_d": {"domain": "NEW", "phrasing": "NEW", "description": "Compound Shift (New Domain + New Phrasing)"},
            "cell_d_matched20": {"domain": "NEW", "phrasing": "NEW", "description": "Compound Shift matched 20-pair slice"},
        },
        "baseline_metrics": {k: v["metrics"] for k, v in baseline_cell_results.items()},
        "experiment_metrics": {k: v["metrics"] for k, v in experiment_cell_results.items()},
    }

    # Factorial Analysis of W_m4_1
    exp_a_diff = experiment_cell_results["cell_a"]["metrics"]["pair_stats"]["diff_target_rate"]
    exp_b_diff = experiment_cell_results["cell_b"]["metrics"]["pair_stats"]["diff_target_rate"]
    exp_c_diff = experiment_cell_results["cell_c"]["metrics"]["pair_stats"]["diff_target_rate"]
    exp_d_diff = experiment_cell_results["cell_d_matched20"]["metrics"]["pair_stats"]["diff_target_rate"]

    summary["analysis"] = {
        "diff_target_both_rates": {
            "cell_a (OLD x OLD)": exp_a_diff,
            "cell_b (OLD x NEW)": exp_b_diff,
            "cell_c (NEW x OLD)": exp_c_diff,
            "cell_d_matched20 (NEW x NEW)": exp_d_diff,
        }
    }

    with open(OUT_DIR / "diagnostic_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 75)
    print("M4.2.1 FACTORIAL 2x2 RESULTS TABLE (W_m4_1 Diff-Target Both)")
    print("=" * 75)
    print(f"| {'Cell':<18} | {'Domain':<8} | {'Phrasing':<8} | {'W_v2_ce10':<12} | {'W_m4_1':<12} | {'Unswitched (W_m4_1)':<20} |")
    print("|" + "-" * 20 + "|" + "-" * 10 + "|" + "-" * 10 + "|" + "-" * 14 + "|" + "-" * 14 + "|" + "-" * 22 + "|")
    for k in ["cell_a", "cell_b", "cell_c", "cell_d_matched20"]:
        b_m = baseline_cell_results[k]["metrics"]["pair_stats"]
        e_m = experiment_cell_results[k]["metrics"]["pair_stats"]
        c_info = summary["cells"][k]
        print(f"| {k:<18} | {c_info['domain']:<8} | {c_info['phrasing']:<8} | {b_m['diff_target_both']:2d}/{b_m['diff_target_pairs']:2d} ({b_m['diff_target_rate']*100:4.1f}%) | {e_m['diff_target_both']:2d}/{e_m['diff_target_pairs']:2d} ({e_m['diff_target_rate']*100:4.1f}%) | {e_m['diff_unswitched']:2d}/{e_m['diff_target_pairs']:2d} ({e_m['diff_unswitched_rate']*100:4.1f}%)         |")
    print("=" * 75)


if __name__ == "__main__":
    main()
