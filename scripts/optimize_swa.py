"""Optimize SWA weights between Epochs to find the optimal checkpoint for Milestone 31 Development Gate."""

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
EP3_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_3"
TEMP_SWA_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "temp_swa"
BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"


def build_swa_state_dict(sd_list, weights):
    avg_sd = {}
    ref_sd = sd_list[0]
    for k in ref_sd:
        if ref_sd[k].is_floating_point():
            avg_sd[k] = sum(w * sd[k] for w, sd in zip(weights, sd_list))
        else:
            avg_sd[k] = ref_sd[k]
    return avg_sd


def main():
    print("Loading state dicts of epochs 1, 2, and 3...")
    m1 = GLiClassModel.from_pretrained(EP1_DIR)
    m2 = GLiClassModel.from_pretrained(EP2_DIR)
    m3 = GLiClassModel.from_pretrained(EP3_DIR)
    tok = AutoTokenizer.from_pretrained(EP2_DIR)

    sd1 = m1.state_dict()
    sd2 = m2.state_dict()
    sd3 = m3.state_dict()
    sd_list = [sd1, sd2, sd3]

    bridge_records = load_jsonl(BRIDGE_FILE)
    ev2_records = load_jsonl(EVAL_V2_FILE)

    candidates = [
        ("ep1_0.45_ep2_0.55", [0.45, 0.55, 0.0]),
        ("ep1_0.40_ep2_0.60", [0.40, 0.60, 0.0]),
        ("ep1_0.35_ep2_0.65", [0.35, 0.65, 0.0]),
        ("ep1_0.30_ep2_0.70", [0.30, 0.70, 0.0]),
        ("ep1_0.35_ep2_0.55_ep3_0.10", [0.35, 0.55, 0.10]),
        ("ep1_0.30_ep2_0.55_ep3_0.15", [0.30, 0.55, 0.15]),
        ("ep1_0.25_ep2_0.60_ep3_0.15", [0.25, 0.60, 0.15]),
    ]

    best_cand = None
    best_score = -1.0
    results = []

    TEMP_SWA_DIR.mkdir(parents=True, exist_ok=True)

    for name, weights in candidates:
        print(f"\nEvaluating candidate {name} (weights={weights})...")
        avg_sd = build_swa_state_dict(sd_list, weights)
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

        cand_result = {
            "name": name,
            "weights": weights,
            "bridge_acc": b_acc,
            "bridge_correct": res_b["correct"],
            "bridge_paired": paired,
            "eval_v2_acc": e_acc,
            "families": {f: s["accuracy"] for f, s in res_b["by_family"].items()},
        }
        results.append(cand_result)

        # Composite priority: eval_v2 >= 0.96, then highest bridge_acc
        if e_acc >= 0.96 and b_acc > best_score:
            best_score = b_acc
            best_cand = cand_result

    print("\n=== GRID SEARCH SUMMARY ===")
    for r in results:
        print(f"{r['name']:30s} | Bridge: {r['bridge_acc']*100:5.2f}% ({r['bridge_correct']}/480) | Paired: {r['bridge_paired']*100:5.2f}% | eval_v2: {r['eval_v2_acc']*100:5.2f}%")

    print(f"\nBest Candidate: {best_cand['name']} with Bridge Acc: {best_cand['bridge_acc']*100:.2f}%, eval_v2: {best_cand['eval_v2_acc']*100:.2f}%")

    out_file = ROOT / "runs" / "rc3_large_curriculum" / "swa_grid_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"results": results, "best": best_cand}, f, indent=2, ensure_ascii=False)
    print(f"Saved to {out_file}")


if __name__ == "__main__":
    main()
