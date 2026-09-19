"""Evaluate baseline models (W_v2_ce10 and W_m4_1) on fresh_phrasing_eval.jsonl."""

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

OUT_DIR = ROOT / "runs/m4_3_phrasing/pre_training_eval"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EVAL_PATH = ROOT / "data/m4_3_phrasing/fresh_phrasing_eval.jsonl"
MODELS = {
    "W_v2_ce10": str(ROOT / "runs/m3_5_ce10/trained/checkpoint"),
    "W_m4_1": str(ROOT / "runs/m4_1_exception/trained/checkpoint"),
}


def evaluate(engine: GLiClassEngine, dataset_path: Path):
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
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

        results.append({
            "id": row["id"],
            "group_id": row["group_id"],
            "phrasing_family": row["phrasing_family"],
            "template_family": row["template_family"],
            "conflict": row["conflict"],
            "priority_order": row["priority_order"],
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "probabilities": probs,
            "nll": nll_val,
        })

    n = len(records)
    groups = {}
    for i, r in enumerate(results):
        groups.setdefault(r["group_id"], []).append(r)

    both_correct = 0
    diff_pairs = 0
    diff_both = 0
    diff_unswitched = 0
    diff_switched_wrong = 0
    same_pairs = 0
    same_both = 0

    for gid, pair in groups.items():
        if len(pair) == 2:
            r1, r2 = pair[0], pair[1]
            is_both = r1["is_correct"] and r2["is_correct"]
            if is_both:
                both_correct += 1

            if r1["target"] != r2["target"]:
                diff_pairs += 1
                if is_both:
                    diff_both += 1
                else:
                    if r1["predicted"] == r2["predicted"]:
                        diff_unswitched += 1
                    else:
                        diff_switched_wrong += 1
            else:
                same_pairs += 1
                if is_both:
                    same_both += 1

    metrics = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
        "mean_brier": total_brier / n,
        "total_pairs": len(groups),
        "both_correct": both_correct,
        "both_rate": both_correct / len(groups),
        "diff_pairs": diff_pairs,
        "diff_both": diff_both,
        "diff_both_rate": diff_both / diff_pairs if diff_pairs > 0 else 0.0,
        "diff_unswitched": diff_unswitched,
        "diff_unswitched_rate": diff_unswitched / diff_pairs if diff_pairs > 0 else 0.0,
        "same_pairs": same_pairs,
        "same_both": same_both,
        "same_both_rate": same_both / same_pairs if same_pairs > 0 else 0.0,
    }
    return results, metrics


def main():
    print("Evaluating Baseline Models on Fresh Phrasing Eval (Families M~P)...")
    summary = {}
    for name, model_path in MODELS.items():
        engine = GLiClassEngine(model_id=model_path, device="cuda" if torch.cuda.is_available() else "cpu")
        preds, m = evaluate(engine, EVAL_PATH)
        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        summary[name] = m
        with open(OUT_DIR / f"{name}_predictions.jsonl", "w", encoding="utf-8") as f:
            for p in preds:
                f.write(json.dumps(p, ensure_ascii=False) + "\n")
        print(f"  {name:<12}: Acc={m['accuracy']*100:5.1f}% | DiffBoth={m['diff_both']:2d}/{m['diff_pairs']:2d} ({m['diff_both_rate']*100:5.1f}%) | Unswitched={m['diff_unswitched']:2d}/{m['diff_pairs']:2d} ({m['diff_unswitched_rate']*100:5.1f}%) | NLL={m['mean_nll']:.4f}")

    with open(OUT_DIR / "pre_training_baseline_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
