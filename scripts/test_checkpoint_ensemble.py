"""Test checkpoint averaging or logit ensembling between Epoch 1 and Epoch 2."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import torch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest
from scripts.train_rc3 import evaluate_records, load_jsonl

EP1_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_1"
EP2_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_2"
EP3_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_3"
BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"


def evaluate_ensemble(engine1: GLiClassEngine, engine2: GLiClassEngine, records: list, w1: float = 0.5, w2: float = 0.5):
    correct = 0
    total = len(records)
    by_family = {}
    groups = {}

    for r in records:
        req = ChoiceRequest.from_dict(r)
        tgt_cid = r["target"]["choice_id"]

        resp1 = engine1.predict(req, temperature=1.0, return_logits=True)
        resp2 = engine2.predict(req, temperature=1.0, return_logits=True)

        # Average probabilities or logits
        probs1 = [c.probability for c in resp1.choices]
        probs2 = [c.probability for c in resp2.choices]
        avg_probs = [w1 * p1 + w2 * p2 for p1, p2 in zip(probs1, probs2)]

        best_idx = max(range(len(avg_probs)), key=lambda i: avg_probs[i])
        pred_cid = req.choices[best_idx].id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct += 1

        fam = r.get("family", "unknown")
        if fam not in by_family:
            by_family[fam] = {"total": 0, "correct": 0}
        by_family[fam]["total"] += 1
        if is_corr:
            by_family[fam]["correct"] += 1

        gid = r.get("group_id", r.get("id"))
        if gid:
            groups.setdefault(gid, []).append(is_corr)

    paired_total = 0
    paired_both = 0
    for gid, pair in groups.items():
        if len(pair) == 2:
            paired_total += 1
            if pair[0] and pair[1]:
                paired_both += 1

    return {
        "accuracy": correct / total,
        "correct": correct,
        "total": total,
        "paired_both_rate": paired_both / paired_total if paired_total > 0 else 0.0,
        "by_family": {f: s["correct"] / s["total"] for f, s in by_family.items()},
    }


def main():
    records = load_jsonl(BRIDGE_FILE)
    ev2_records = load_jsonl(EVAL_V2_FILE)

    print("Loading engines...")
    e1 = GLiClassEngine(model_id=str(EP1_DIR), device="cuda:0")
    e2 = GLiClassEngine(model_id=str(EP2_DIR), device="cuda:0")

    print("\n--- Testing Logit Ensemble (Epoch 1 + Epoch 2, 50/50) on Bridge ---")
    res_ens = evaluate_ensemble(e1, e2, records, 0.4, 0.6)
    print(f"Ensemble Bridge Acc: {res_ens['accuracy']*100:.2f}% ({res_ens['correct']}/{res_ens['total']})")
    print(f"Ensemble Paired Both: {res_ens['paired_both_rate']*100:.2f}%")
    for fam, acc in res_ens["by_family"].items():
        print(f"  - {fam:25s}: {acc*100:.2f}%")

    res_ev2 = evaluate_ensemble(e1, e2, ev2_records, 0.4, 0.6)
    print(f"Ensemble eval_v2 Acc: {res_ev2['accuracy']*100:.2f}% ({res_ev2['correct']}/{res_ev2['total']})")


if __name__ == "__main__":
    main()
