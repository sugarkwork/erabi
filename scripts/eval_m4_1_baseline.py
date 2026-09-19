"""Evaluate baseline model W_v2_ce10 on M4.1 exception priority eval dataset at T=1.0.

Outputs to runs/m4_1_exception/baseline_eval/:
- eval_exception_predictions.jsonl
- smoke_cases_predictions.jsonl
- baseline_metrics.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

OUT_DIR = ROOT / "runs/m4_1_exception/baseline_eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = str(ROOT / "runs/m3_5_ce10/trained/checkpoint")
EVAL_FILE = ROOT / "data/m4_1_exception/eval_exception.jsonl"
SMOKE_FILE = ROOT / "examples/smoke_cases.jsonl"


def run_eval_dataset(engine: GLiClassEngine, dataset_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

    print(f"Evaluating {len(records)} cases from {dataset_path.name}...")
    for idx, row in enumerate(records):
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
            "task_family": row.get("task_family"),
            "template_family": row.get("template_family"),
            "rule_kind": row.get("rule_kind"),
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
    metrics = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
        "mean_brier": total_brier / n,
    }

    # Pair metrics if paired
    groups: Dict[str, List[int]] = {}
    for i, r in enumerate(results):
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(i)

    paired_groups = {k: v for k, v in groups.items() if len(v) == 2}
    if paired_groups:
        both_correct = 0
        diff_pairs = 0
        diff_both = 0
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
        }
    else:
        metrics["pair_stats"] = None

    return results, metrics


def main():
    print(f"Loading baseline model W_v2_ce10 from {MODEL_DIR}...")
    engine = GLiClassEngine(model_id=MODEL_DIR)

    # 1. Eval exception
    eval_res, eval_metrics = run_eval_dataset(engine, EVAL_FILE)
    with open(OUT_DIR / "eval_exception_predictions.jsonl", "w", encoding="utf-8") as f:
        for r in eval_res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 2. Smoke cases
    smoke_res, smoke_metrics = run_eval_dataset(engine, SMOKE_FILE)
    with open(OUT_DIR / "smoke_cases_predictions.jsonl", "w", encoding="utf-8") as f:
        for r in smoke_res:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    summary = {
        "model_id": MODEL_DIR,
        "temperature": 1.0,
        "eval_exception": eval_metrics,
        "smoke_cases": smoke_metrics,
    }

    with open(OUT_DIR / "baseline_metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n=== Baseline Results on M4.1 Exception Dataset ===")
    print(f"Eval Exception: Accuracy = {eval_metrics['accuracy']*100:.1f}% ({eval_metrics['correct_count']}/{eval_metrics['count']})")
    print(f"                Mean NLL = {eval_metrics['mean_nll']:.4f}, Mean Brier = {eval_metrics['mean_brier']:.4f}")
    if eval_metrics.get("pair_stats"):
        ps = eval_metrics["pair_stats"]
        print(f"                Both Correct Pairs = {ps['both_correct']}/{ps['total_pairs']} ({ps['both_rate']*100:.1f}%)")
        print(f"                Diff Target Pairs  = {ps['diff_target_both']}/{ps['diff_target_pairs']} ({ps['diff_target_rate']*100:.1f}%)")
        print(f"                Same Target Pairs  = {ps['same_target_both']}/{ps['same_target_pairs']} ({ps['same_target_rate']*100:.1f}%)")

    print("\n=== Baseline Smoke Cases ===")
    print(f"Smoke Accuracy: {smoke_metrics['accuracy']*100:.1f}% ({smoke_metrics['correct_count']}/{smoke_metrics['count']})")
    smoke_06 = next(r for r in smoke_res if r["id"] == "smoke-06")
    print(f"smoke-06 prediction: target={smoke_06['target']}, predicted={smoke_06['predicted']}, is_correct={smoke_06['is_correct']}")


if __name__ == "__main__":
    main()
