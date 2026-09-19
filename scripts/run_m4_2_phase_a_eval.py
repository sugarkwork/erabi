"""Run M4.2 Phase A Novel Priority Probe Evaluation.

Evaluates:
1. Baseline: W_v2_ce10 (runs/m3_5_ce10/trained/checkpoint)
2. Experiment: W_m4_1 (runs/m4_1_exception/trained/checkpoint)

Both at strictly T=1.0 on:
data/m4_2_robustness/novel_priority_eval.jsonl (120 cases / 60 pairs)

Outputs to runs/m4_2_robustness/phase_a/:
- baseline_predictions.jsonl
- experiment_predictions.jsonl
- phase_a_summary.json
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

OUT_DIR = ROOT / "runs/m4_2_robustness/phase_a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_MODEL = str(ROOT / "runs/m3_5_ce10/trained/checkpoint")
EXPERIMENT_MODEL = str(ROOT / "runs/m4_1_exception/trained/checkpoint")
EVAL_DATASET = ROOT / "data/m4_2_robustness/novel_priority_eval.jsonl"


def evaluate_model(engine: GLiClassEngine, dataset_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

    # Family & domain breakdowns
    domain_stats: Dict[str, Dict[str, int]] = {}
    family_stats: Dict[str, Dict[str, int]] = {}

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

        dom = row.get("template_family", "unknown")
        fam = row.get("phrasing_family", "unknown")

        domain_stats.setdefault(dom, {"total": 0, "correct": 0})
        domain_stats[dom]["total"] += 1
        if is_corr:
            domain_stats[dom]["correct"] += 1

        family_stats.setdefault(fam, {"total": 0, "correct": 0})
        family_stats[fam]["total"] += 1
        if is_corr:
            family_stats[fam]["correct"] += 1

        res_item = {
            "id": row.get("id"),
            "group_id": row.get("group_id"),
            "task_family": row.get("task_family"),
            "template_family": dom,
            "phrasing_family": fam,
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
        "domain_breakdown": {
            d: {
                "total": s["total"],
                "correct": s["correct"],
                "accuracy": s["correct"] / s["total"],
            }
            for d, s in domain_stats.items()
        },
        "family_breakdown": {
            f: {
                "total": s["total"],
                "correct": s["correct"],
                "accuracy": s["correct"] / s["total"],
            }
            for f, s in family_stats.items()
        },
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
    same_pairs = 0
    same_both = 0

    diff_by_family: Dict[str, Dict[str, int]] = {}
    diff_by_domain: Dict[str, Dict[str, int]] = {}

    for gid, indices in paired_groups.items():
        r1, r2 = results[indices[0]], results[indices[1]]
        is_both = r1["is_correct"] and r2["is_correct"]
        if is_both:
            both_correct += 1

        is_diff = (r1["target"] != r2["target"])
        fam = r1.get("phrasing_family", "unknown")
        dom = r1.get("template_family", "unknown")

        if is_diff:
            diff_pairs += 1
            diff_by_family.setdefault(fam, {"total": 0, "both": 0})
            diff_by_family[fam]["total"] += 1
            diff_by_domain.setdefault(dom, {"total": 0, "both": 0})
            diff_by_domain[dom]["total"] += 1

            if is_both:
                diff_both += 1
                diff_by_family[fam]["both"] += 1
                diff_by_domain[dom]["both"] += 1
        else:
            same_pairs += 1
            if is_both:
                same_both += 1

    metrics["pair_stats"] = {
        "total_pairs": len(paired_groups),
        "both_correct": both_correct,
        "both_rate": both_correct / len(paired_groups),
        "diff_target_pairs": diff_pairs,
        "diff_target_both": diff_both,
        "diff_target_rate": (diff_both / diff_pairs) if diff_pairs > 0 else 0.0,
        "same_target_pairs": same_pairs,
        "same_target_both": same_both,
        "same_target_rate": (same_both / same_pairs) if same_pairs > 0 else 0.0,
        "diff_by_family": {
            f: {
                "total": s["total"],
                "both": s["both"],
                "rate": s["both"] / s["total"] if s["total"] > 0 else 0.0,
            }
            for f, s in diff_by_family.items()
        },
        "diff_by_domain": {
            d: {
                "total": s["total"],
                "both": s["both"],
                "rate": s["both"] / s["total"] if s["total"] > 0 else 0.0,
            }
            for d, s in diff_by_domain.items()
        },
    }

    return results, metrics


def main():
    print("=" * 70)
    print("ERABI M4.2 Phase A: Novel Priority Probe Evaluation")
    print("=" * 70)
    print(f"Dataset: {EVAL_DATASET}")
    print(f"Baseline: {BASELINE_MODEL}")
    print(f"Experiment: {EXPERIMENT_MODEL}")

    # 1. Evaluate Baseline (W_v2_ce10)
    print("\n--- Evaluating Baseline (W_v2_ce10) ---")
    t0 = time.time()
    base_engine = GLiClassEngine(model_id=BASELINE_MODEL, device="cuda" if torch.cuda.is_available() else "cpu")
    base_preds, base_metrics = evaluate_model(base_engine, EVAL_DATASET)
    del base_engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print(f"Baseline evaluated in {time.time() - t0:.2f}s")
    print(f"Baseline Accuracy: {base_metrics['accuracy']:.4f} ({base_metrics['correct_count']}/{base_metrics['count']})")
    print(f"Baseline Diff Both: {base_metrics['pair_stats']['diff_target_both']}/{base_metrics['pair_stats']['diff_target_pairs']} ({base_metrics['pair_stats']['diff_target_rate']:.4f})")
    print(f"Baseline Mean NLL: {base_metrics['mean_nll']:.4f}, Mean Brier: {base_metrics['mean_brier']:.4f}")

    # Save baseline predictions
    base_pred_file = OUT_DIR / "baseline_predictions.jsonl"
    with open(base_pred_file, "w", encoding="utf-8") as f:
        for p in base_preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # 2. Evaluate Experiment (W_m4_1)
    print("\n--- Evaluating Experiment (W_m4_1) ---")
    t1 = time.time()
    exp_engine = GLiClassEngine(model_id=EXPERIMENT_MODEL, device="cuda" if torch.cuda.is_available() else "cpu")
    exp_preds, exp_metrics = evaluate_model(exp_engine, EVAL_DATASET)
    del exp_engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    print(f"Experiment evaluated in {time.time() - t1:.2f}s")
    print(f"Experiment Accuracy: {exp_metrics['accuracy']:.4f} ({exp_metrics['correct_count']}/{exp_metrics['count']})")
    print(f"Experiment Diff Both: {exp_metrics['pair_stats']['diff_target_both']}/{exp_metrics['pair_stats']['diff_target_pairs']} ({exp_metrics['pair_stats']['diff_target_rate']:.4f})")
    print(f"Experiment Mean NLL: {exp_metrics['mean_nll']:.4f}, Mean Brier: {exp_metrics['mean_brier']:.4f}")

    # Save experiment predictions
    exp_pred_file = OUT_DIR / "experiment_predictions.jsonl"
    with open(exp_pred_file, "w", encoding="utf-8") as f:
        for p in exp_preds:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    # 3. Save Summary
    summary = {
        "evaluation_dataset": str(EVAL_DATASET),
        "cases_count": len(base_preds),
        "pairs_count": len(base_preds) // 2,
        "baseline_model": BASELINE_MODEL,
        "experiment_model": EXPERIMENT_MODEL,
        "temperature": 1.0,
        "baseline_metrics": base_metrics,
        "experiment_metrics": exp_metrics,
        "diff_target_both_threshold": 0.60,
        "proceed_to_phase_b": exp_metrics["pair_stats"]["diff_target_rate"] >= 0.60,
    }

    summary_file = OUT_DIR / "phase_a_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("PHASE A SUMMARY & DECISION")
    print("=" * 70)
    diff_rate = exp_metrics["pair_stats"]["diff_target_rate"]
    print(f"W_m4_1 Novel Priority Diff-Target Both: {exp_metrics['pair_stats']['diff_target_both']}/{exp_metrics['pair_stats']['diff_target_pairs']} = {diff_rate*100:.1f}%")
    print(f"Threshold for Phase B: 60.0%")
    if diff_rate >= 0.60:
        print(">> RESULT: PASSED (>= 60.0%). Proceed to Phase B.")
    else:
        print(">> RESULT: FAILED (< 60.0%). STOP Phase A and report transfer deficiency.")
    print("=" * 70)


if __name__ == "__main__":
    main()
