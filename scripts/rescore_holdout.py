"""Rescore old model (W_bad) predictions on holdout with corrected labels.

This script:
1. Loads the checkpoint of W_bad: runs/m2_1/trained_instruct_base/checkpoint.
2. Runs inference on data/m3_2_label_fix/holdout_corrected.jsonl to obtain raw logits.
3. Computes:
   - Performance under old labels (verifying M2.1's 190/200)
   - Performance under repaired labels
   - Subset performance: repaired server cases (12 cases) vs unmodified cases (188 cases)
   - Transitions: old correct -> new incorrect, old incorrect -> new correct
   - Pair metrics: all 100 pairs vs pairs where targets genuinely differ
   - Accurate NLL and Brier from raw float logits (temperature = 1.0)
4. Saves artifacts to runs/m3_2_label_fix/rescoring/
"""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

# Ensure src/ is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

import torch
from erabi.evaluate import compute_metrics, compute_softmax
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest


def main():
    checkpoint_dir = str(root_dir / "runs" / "m2_1" / "trained_instruct_base" / "checkpoint")
    old_holdout_path = root_dir / "data" / "m2_1" / "holdout.jsonl"
    repaired_holdout_path = root_dir / "data" / "m3_2_label_fix" / "holdout_corrected.jsonl"
    changes_path = root_dir / "data" / "m3_2_label_fix" / "label_changes.jsonl"
    out_dir = root_dir / "runs" / "m3_2_label_fix" / "rescoring"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=== Rescoring W_bad on Repaired Holdout ===")
    print(f"Checkpoint: {checkpoint_dir}")
    print(f"Old holdout: {old_holdout_path}")
    print(f"Repaired holdout: {repaired_holdout_path}")

    # 1. Load data
    with open(old_holdout_path, "r", encoding="utf-8") as f:
        old_records = [json.loads(line) for line in f]
    with open(repaired_holdout_path, "r", encoding="utf-8") as f:
        new_records = [json.loads(line) for line in f]
    assert len(old_records) == len(new_records) == 200

    # Load changes in holdout
    changed_ids = set()
    with open(changes_path, "r", encoding="utf-8") as f:
        for line in f:
            ch = json.loads(line)
            if ch["split"] == "holdout":
                changed_ids.add(ch["id"])
    print(f"Repaired target cases in holdout: {len(changed_ids)} cases")

    # 2. Load engine
    engine = GLiClassEngine(model_id=checkpoint_dir)

    # 3. Run inference to get raw logits
    print("Running inference with W_bad...")
    predictions = []
    for rec in new_records:
        req = ChoiceRequest.from_dict(rec)
        resp = engine.predict(req, return_logits=True)
        pred_entry = {
            "id": rec["id"],
            "group_id": rec.get("group_id", ""),
            "task_family": rec.get("task_family", ""),
            "template_family": rec.get("template_family", ""),
            "choices": [
                {"id": co.id, "probability": co.probability}
                for co in resp.choices
            ],
            "best_candidate_id": resp.best_candidate_id,
            "raw_logits": resp.raw_logits,
            "old_target": None,
            "new_target": rec["target"]["choice_id"],
        }
        predictions.append(pred_entry)

    # Map old targets
    old_target_map = {r["id"]: r["target"]["choice_id"] for r in old_records}
    for p in predictions:
        p["old_target"] = old_target_map[p["id"]]

    # 4. Detailed scoring
    old_targets = [p["old_target"] for p in predictions]
    new_targets = [p["new_target"] for p in predictions]
    metadata = [
        {
            "group_id": p["group_id"],
            "task_family": p["task_family"],
            "template_family": p["template_family"],
        }
        for p in predictions
    ]

    # Metrics on old labels
    old_metrics = compute_metrics(predictions, old_targets, metadata, temperature=1.0)
    # Metrics on new labels
    new_metrics = compute_metrics(predictions, new_targets, metadata, temperature=1.0)

    # Breakdown by changed vs unchanged
    changed_preds = [p for p in predictions if p["id"] in changed_ids]
    unchanged_preds = [p for p in predictions if p["id"] not in changed_ids]

    changed_new_targets = [p["new_target"] for p in changed_preds]
    changed_old_targets = [p["old_target"] for p in changed_preds]
    unchanged_targets = [p["new_target"] for p in unchanged_preds]

    changed_new_metrics = compute_metrics(changed_preds, changed_new_targets, temperature=1.0)
    changed_old_metrics = compute_metrics(changed_preds, changed_old_targets, temperature=1.0)
    unchanged_metrics = compute_metrics(unchanged_preds, unchanged_targets, temperature=1.0)

    # Transition matrix
    transitions = {
        "correct_to_correct": 0,
        "correct_to_incorrect": 0,
        "incorrect_to_correct": 0,
        "incorrect_to_incorrect": 0,
    }
    changed_case_details = []
    for p in predictions:
        pred_id = p["best_candidate_id"]
        old_corr = (pred_id == p["old_target"])
        new_corr = (pred_id == p["new_target"])

        if old_corr and new_corr:
            transitions["correct_to_correct"] += 1
        elif old_corr and not new_corr:
            transitions["correct_to_incorrect"] += 1
        elif not old_corr and new_corr:
            transitions["incorrect_to_correct"] += 1
        else:
            transitions["incorrect_to_incorrect"] += 1

        if p["id"] in changed_ids:
            changed_case_details.append({
                "id": p["id"],
                "predicted": pred_id,
                "old_target": p["old_target"],
                "new_target": p["new_target"],
                "old_was_correct": old_corr,
                "new_is_correct": new_corr,
                "probabilities": {c["id"]: round(c["probability"], 4) for c in p["choices"]},
            })

    # Pair metrics breakdown
    groups = defaultdict(list)
    for p in predictions:
        groups[p["group_id"]].append(p)

    all_pairs = 0
    both_correct_new = 0
    diff_target_pairs = 0
    diff_target_both_correct = 0
    same_target_pairs = 0
    same_target_both_correct = 0

    for gid, plist in groups.items():
        if len(plist) == 2:
            all_pairs += 1
            corr1 = (plist[0]["best_candidate_id"] == plist[0]["new_target"])
            corr2 = (plist[1]["best_candidate_id"] == plist[1]["new_target"])
            both = (corr1 and corr2)
            if both:
                both_correct_new += 1

            if plist[0]["new_target"] != plist[1]["new_target"]:
                diff_target_pairs += 1
                if both:
                    diff_target_both_correct += 1
            else:
                same_target_pairs += 1
                if both:
                    same_target_both_correct += 1

    summary = {
        "model": "W_bad (runs/m2_1/trained_instruct_base/checkpoint)",
        "eval_dataset": "holdout (200 cases, 100 groups)",
        "overall_comparison": {
            "old_label_accuracy": f"{old_metrics['correct_count']}/{old_metrics['count']} ({old_metrics['accuracy'] * 100:.2f}%)",
            "new_label_accuracy": f"{new_metrics['correct_count']}/{new_metrics['count']} ({new_metrics['accuracy'] * 100:.2f}%)",
            "old_label_mean_nll": old_metrics["mean_nll"],
            "new_label_mean_nll": new_metrics["mean_nll"],
            "old_label_mean_brier": old_metrics["mean_brier"],
            "new_label_mean_brier": new_metrics["mean_brier"],
        },
        "breakdown": {
            "repaired_cases": {
                "count": len(changed_preds),
                "old_label_correct": f"{changed_old_metrics['correct_count']}/{changed_old_metrics['count']}",
                "new_label_correct": f"{changed_new_metrics['correct_count']}/{changed_new_metrics['count']}",
                "mean_nll_new": changed_new_metrics["mean_nll"],
                "mean_brier_new": changed_new_metrics["mean_brier"],
            },
            "unmodified_cases": {
                "count": len(unchanged_preds),
                "accuracy": f"{unchanged_metrics['correct_count']}/{unchanged_metrics['count']} ({unchanged_metrics['accuracy'] * 100:.2f}%)",
                "mean_nll": unchanged_metrics["mean_nll"],
                "mean_brier": unchanged_metrics["mean_brier"],
            },
        },
        "transitions": transitions,
        "pair_breakdown": {
            "all_pairs": {
                "total": all_pairs,
                "both_correct": both_correct_new,
                "rate": round(both_correct_new / all_pairs, 4) if all_pairs > 0 else 0,
            },
            "different_target_pairs": {
                "total": diff_target_pairs,
                "both_correct": diff_target_both_correct,
                "rate": round(diff_target_both_correct / diff_target_pairs, 4) if diff_target_pairs > 0 else 0,
            },
            "same_target_pairs": {
                "total": same_target_pairs,
                "both_correct": same_target_both_correct,
                "rate": round(same_target_both_correct / same_target_pairs, 4) if same_target_pairs > 0 else 0,
            },
        },
        "repaired_case_details": changed_case_details,
    }

    # Save summary
    summary_path = out_dir / "rescore_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Saved rescoring summary to {summary_path}")

    # Save predictions
    pred_path = out_dir / "rescore_predictions.jsonl"
    with open(pred_path, "w", encoding="utf-8") as f:
        for p in predictions:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"Saved detailed predictions to {pred_path}")

    print("\n--- Summary ---")
    print(f"Old label accuracy: {summary['overall_comparison']['old_label_accuracy']}")
    print(f"New label accuracy: {summary['overall_comparison']['new_label_accuracy']}")
    print(f"Repaired cases (12 cases): old={summary['breakdown']['repaired_cases']['old_label_correct']}, new={summary['breakdown']['repaired_cases']['new_label_correct']}")
    print(f"Unmodified cases (188 cases): {summary['breakdown']['unmodified_cases']['accuracy']}")
    print(f"Transitions: {transitions}")
    print(f"Both correct pairs (all 100): {both_correct_new}/100 ({both_correct_new}%)")
    print(f"Both correct pairs (different target {diff_target_pairs}): {diff_target_both_correct}/{diff_target_pairs}")


if __name__ == "__main__":
    main()
