"""Run comprehensive head-to-head comparison between Baseline (W_v2_ce10) and Experiment (W_m4_1).

Both evaluated at strictly T=1.0.
Datasets:
1. data/m4_1_exception/eval_exception.jsonl (120 cases: new capability)
2. examples/smoke_cases.jsonl (12 cases: regression check + smoke-06 focus)
3. data/m3_3_v2/eval_v2.jsonl (200 cases: M3 synthetic rule regression check)
4. data/m3_1/transfer_probe.jsonl (32 cases: transfer/generalization regression check)

Outputs to runs/m4_1_exception/comparisons/:
- Baseline individual predictions
- Experiment individual predictions
- comparisons_summary.json
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

OUT_DIR = ROOT / "runs/m4_1_exception/comparisons"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_MODEL = str(ROOT / "runs/m3_5_ce10/trained/checkpoint")
EXPERIMENT_MODEL = str(ROOT / "runs/m4_1_exception/trained/checkpoint")

DATASETS = {
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
}


def evaluate_dataset(engine: GLiClassEngine, dataset_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

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
    if paired_groups and dataset_path.name != "smoke_cases.jsonl":
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
    print("=== ERABI M4.1 Comparative Evaluation (Baseline vs Experiment) ===")

    print(f"\n1. Loading Baseline model W_v2_ce10 ({BASELINE_MODEL})...")
    baseline_engine = GLiClassEngine(model_id=BASELINE_MODEL)

    print(f"\n2. Loading Experiment model W_m4_1 ({EXPERIMENT_MODEL})...")
    experiment_engine = GLiClassEngine(model_id=EXPERIMENT_MODEL)

    full_comparison = {
        "evaluation_temperature": 1.0,
        "models": {
            "baseline": BASELINE_MODEL,
            "experiment": EXPERIMENT_MODEL,
        },
        "datasets": {},
    }

    for dname, dpath in DATASETS.items():
        print(f"\n--- Evaluating dataset: {dname} ({dpath.name}) ---")
        base_res, base_m = evaluate_dataset(baseline_engine, dpath)
        exp_res, exp_m = evaluate_dataset(experiment_engine, dpath)

        # Save individual predictions
        with open(OUT_DIR / f"baseline_{dname}_predictions.jsonl", "w", encoding="utf-8") as f:
            for r in base_res:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        with open(OUT_DIR / f"experiment_{dname}_predictions.jsonl", "w", encoding="utf-8") as f:
            for r in exp_res:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"[{dname}] Baseline:   Acc = {base_m['accuracy']*100:.1f}% ({base_m['correct_count']}/{base_m['count']}) | NLL = {base_m['mean_nll']:.4f} | Brier = {base_m['mean_brier']:.4f}")
        print(f"[{dname}] Experiment: Acc = {exp_m['accuracy']*100:.1f}% ({exp_m['correct_count']}/{exp_m['count']}) | NLL = {exp_m['mean_nll']:.4f} | Brier = {exp_m['mean_brier']:.4f}")

        if base_m.get("pair_stats") and exp_m.get("pair_stats"):
            bps = base_m["pair_stats"]
            eps = exp_m["pair_stats"]
            print(f"       Pair Both: Baseline {bps['both_correct']}/{bps['total_pairs']} ({bps['both_rate']*100:.1f}%) -> Experiment {eps['both_correct']}/{eps['total_pairs']} ({eps['both_rate']*100:.1f}%)")
            print(f"       Diff Pair: Baseline {bps['diff_target_both']}/{bps['diff_target_pairs']} ({bps['diff_target_rate']*100:.1f}%) -> Experiment {eps['diff_target_both']}/{eps['diff_target_pairs']} ({eps['diff_target_rate']*100:.1f}%)")

        full_comparison["datasets"][dname] = {
            "baseline": base_m,
            "experiment": exp_m,
            "accuracy_diff": exp_m["accuracy"] - base_m["accuracy"],
            "nll_diff": exp_m["mean_nll"] - base_m["mean_nll"],
            "brier_diff": exp_m["mean_brier"] - base_m["mean_brier"],
        }

        # Track smoke individual transitions
        if dname == "smoke_cases":
            smoke_trans = []
            for b_item, e_item in zip(base_res, exp_res):
                cid = b_item["id"]
                tgt = b_item["target"]
                b_pred = b_item["predicted"]
                e_pred = e_item["predicted"]
                b_corr = b_item["is_correct"]
                e_corr = e_item["is_correct"]
                smoke_trans.append({
                    "id": cid,
                    "target": tgt,
                    "baseline_pred": b_pred,
                    "baseline_correct": b_corr,
                    "experiment_pred": e_pred,
                    "experiment_correct": e_corr,
                    "transition": "retained" if (b_corr and e_corr) else ("recovered" if (not b_corr and e_corr) else ("regressed" if (b_corr and not e_corr) else "persistently_incorrect")),
                })
            full_comparison["datasets"]["smoke_cases"]["individual_transitions"] = smoke_trans

            print("\nSmoke 12 Cases Individual Comparison:")
            for item in smoke_trans:
                print(f"  {item['id']}: target={item['target']:10s} | Base={item['baseline_pred']:10s} ({'O' if item['baseline_correct'] else 'X'}) -> Exp={item['experiment_pred']:10s} ({'O' if item['experiment_correct'] else 'X'}) | {item['transition']}")

    comp_summary_path = OUT_DIR / "comparisons_summary.json"
    with open(comp_summary_path, "w", encoding="utf-8") as f:
        json.dump(full_comparison, f, indent=2, ensure_ascii=False)

    print(f"\nSaved full comparison summary to {comp_summary_path}")


if __name__ == "__main__":
    main()
