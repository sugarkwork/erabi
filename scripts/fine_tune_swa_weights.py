"""Fine search SWA weights between 0.42 and 0.54."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import torch
from gliclass import GLiClassModel
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from scripts.train_rc3 import evaluate_records, load_jsonl

EP1_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_1"
EP2_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_2"
TEMP_SWA_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "fine_swa"
BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"


def build_swa_state_dict(sd1, sd2, w1, w2):
    avg_sd = {}
    for k in sd1:
        if k in sd2:
            if sd1[k].is_floating_point():
                avg_sd[k] = w1 * sd1[k] + w2 * sd2[k]
            else:
                avg_sd[k] = sd2[k]
        else:
            avg_sd[k] = sd1[k]
    return avg_sd


def main():
    print("Loading state dicts of epochs 1 and 2...")
    m1 = GLiClassModel.from_pretrained(EP1_DIR)
    m2 = GLiClassModel.from_pretrained(EP2_DIR)
    tok = AutoTokenizer.from_pretrained(EP2_DIR)

    sd1 = m1.state_dict()
    sd2 = m2.state_dict()

    bridge_records = load_jsonl(BRIDGE_FILE)
    ev2_records = load_jsonl(EVAL_V2_FILE)

    weights_to_test = [
        0.44,
        0.46,
        0.48,
        0.50,
        0.52,
    ]

    TEMP_SWA_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for w1 in weights_to_test:
        w2 = round(1.0 - w1, 4)
        name = f"ep1_{w1:.2f}_ep2_{w2:.2f}"
        print(f"\nEvaluating {name}...")

        avg_sd = build_swa_state_dict(sd1, sd2, w1, w2)
        m2.load_state_dict(avg_sd)
        m2.save_pretrained(TEMP_SWA_DIR)
        tok.save_pretrained(TEMP_SWA_DIR)

        engine = GLiClassEngine(model_id=str(TEMP_SWA_DIR), device="cuda:0")
        res_b = evaluate_records(engine, bridge_records, test_permutation=False)
        res_e = evaluate_records(engine, ev2_records, test_permutation=False)

        b_acc = res_b["accuracy"]
        e_acc = res_e["accuracy"]
        paired = res_b["paired_both_rate"]
        print(f"  --> Bridge Acc: {b_acc*100:.2f}% ({res_b['correct']}/{res_b['total_cases']}), Paired: {paired*100:.2f}%, eval_v2: {e_acc*100:.2f}%")

        results.append({
            "name": name,
            "w1": w1,
            "w2": w2,
            "bridge_acc": b_acc,
            "bridge_correct": res_b["correct"],
            "bridge_paired": paired,
            "eval_v2_acc": e_acc,
            "families": {f: s["accuracy"] for f, s in res_b["by_family"].items()},
        })

    print("\n=== FINE GRID RESULTS ===")
    for r in results:
        print(f"{r['name']:25s} | Bridge: {r['bridge_acc']*100:5.2f}% ({r['bridge_correct']}/480) | Paired: {r['bridge_paired']*100:5.2f}% | eval_v2: {r['eval_v2_acc']*100:5.2f}%")


if __name__ == "__main__":
    main()
