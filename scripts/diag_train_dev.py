"""Evaluate model on train and dev splits with detailed pair breakdown.

Specifically computes:
- Overall accuracy, mean NLL, mean Brier
- Diff-target pairs: total, both_correct, pred_same, pred_diff
- Same-target pairs: total, both_correct, pred_same, pred_diff
- Task family breakdown on diff-target pairs (especially goal_following)
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from erabi.evaluate import compute_metrics
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest


def load_jsonl(filepath: Path) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate_split(engine: GLiClassEngine, filepath: Path) -> Dict[str, Any]:
    records = load_jsonl(filepath)
    predictions = []
    for rec in records:
        req = ChoiceRequest.from_dict(rec)
        resp = engine.predict(req, return_logits=True)
        predictions.append({
            "id": rec["id"],
            "group_id": rec.get("group_id", ""),
            "task_family": rec.get("task_family", ""),
            "rule_kind": rec.get("rule_kind", ""),
            "choices": [{"id": co.id, "probability": co.probability} for co in resp.choices],
            "best_candidate_id": resp.best_candidate_id,
            "target": rec["target"]["choice_id"],
            "raw_logits": resp.raw_logits,
            "is_correct": (resp.best_candidate_id == rec["target"]["choice_id"]),
        })

    targets = [p["target"] for p in predictions]
    metrics = compute_metrics(predictions, targets, temperature=1.0)

    # Pair analysis
    groups = defaultdict(list)
    for p in predictions:
        groups[p["group_id"]].append(p)

    diff_pairs = {}
    same_pairs = {}
    for gid, plist in groups.items():
        if len(plist) == 2:
            if plist[0]["target"] != plist[1]["target"]:
                diff_pairs[gid] = plist
            else:
                same_pairs[gid] = plist

    def analyze_pair_group(pair_dict):
        total = len(pair_dict)
        both = 0
        one = 0
        neither = 0
        pred_same = 0
        pred_diff = 0
        for gid, plist in pair_dict.items():
            c1 = plist[0]["is_correct"]
            c2 = plist[1]["is_correct"]
            if c1 and c2:
                both += 1
            elif c1 or c2:
                one += 1
            else:
                neither += 1
            if plist[0]["best_candidate_id"] == plist[1]["best_candidate_id"]:
                pred_same += 1
            else:
                pred_diff += 1
        return {
            "total_pairs": total,
            "both_correct": both,
            "one_correct": one,
            "neither_correct": neither,
            "pred_same": pred_same,
            "pred_diff": pred_diff,
        }

    diff_stats = analyze_pair_group(diff_pairs)
    same_stats = analyze_pair_group(same_pairs)

    # Family breakdown for diff pairs
    fam_diff_stats = defaultdict(lambda: {"total": 0, "both": 0, "pred_same": 0, "pred_diff": 0})
    for gid, plist in diff_pairs.items():
        fam = plist[0]["task_family"]
        if fam == "explicit_rule":
            fam = f"explicit_rule:{plist[0].get('rule_kind', '')}"
        fam_diff_stats[fam]["total"] += 1
        c1 = plist[0]["is_correct"]
        c2 = plist[1]["is_correct"]
        if c1 and c2:
            fam_diff_stats[fam]["both"] += 1
        if plist[0]["best_candidate_id"] == plist[1]["best_candidate_id"]:
            fam_diff_stats[fam]["pred_same"] += 1
        else:
            fam_diff_stats[fam]["pred_diff"] += 1

    return {
        "count": metrics["count"],
        "correct_count": metrics["correct_count"],
        "accuracy": metrics["accuracy"],
        "mean_nll": metrics["mean_nll"],
        "mean_brier": metrics["mean_brier"],
        "diff_target_pairs": diff_stats,
        "same_target_pairs": same_stats,
        "diff_pairs_by_family": dict(fam_diff_stats),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", type=str, required=True)
    parser.add_argument("--output-json", type=str, required=True)
    args = parser.parse_args()

    print(f"Loading engine from {args.model_id}...")
    engine = GLiClassEngine(model_id=args.model_id)

    train_path = ROOT_DIR / "data" / "m3_3_v2" / "train.jsonl"
    dev_path = ROOT_DIR / "data" / "m3_3_v2" / "dev.jsonl"

    print("Evaluating train split (600 cases)...")
    train_diag = evaluate_split(engine, train_path)

    print("Evaluating dev split (100 cases)...")
    dev_diag = evaluate_split(engine, dev_path)

    out = {
        "model_id": args.model_id,
        "train": train_diag,
        "dev": dev_diag,
    }

    out_path = Path(args.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Saved diagnostic to {out_path}")
    print("\n--- Summary ---")
    print(f"Train: Acc {train_diag['accuracy']*100:.1f}%, NLL {train_diag['mean_nll']:.4f}, Diff Both {train_diag['diff_target_pairs']['both_correct']}/{train_diag['diff_target_pairs']['total_pairs']}")
    print(f"  Goal Following Diff Both: {train_diag['diff_pairs_by_family'].get('goal_following', {}).get('both', 0)}/{train_diag['diff_pairs_by_family'].get('goal_following', {}).get('total', 0)}")
    print(f"Dev:   Acc {dev_diag['accuracy']*100:.1f}%, NLL {dev_diag['mean_nll']:.4f}, Diff Both {dev_diag['diff_target_pairs']['both_correct']}/{dev_diag['diff_target_pairs']['total_pairs']}")
    print(f"  Goal Following Diff Both: {dev_diag['diff_pairs_by_family'].get('goal_following', {}).get('both', 0)}/{dev_diag['diff_pairs_by_family'].get('goal_following', {}).get('total', 0)}")


if __name__ == "__main__":
    main()
