"""Evaluate Stochastic Weight Averaging (SWA) between Epoch 1 and Epoch 2 checkpoints."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
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
from scripts.train_rc3 import evaluate_records, evaluate_development_gate, load_jsonl

EP1_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_1"
EP2_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_2"
EP3_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_3"
SWA_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "swa_ep1_ep2"
BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"


def create_averaged_checkpoint(ckpt1: Path, ckpt2: Path, out_dir: Path, w1: float = 0.5, w2: float = 0.5):
    out_dir.mkdir(parents=True, exist_ok=True)
    m1 = GLiClassModel.from_pretrained(ckpt1)
    m2 = GLiClassModel.from_pretrained(ckpt2)
    tok = AutoTokenizer.from_pretrained(ckpt2)

    sd1 = m1.state_dict()
    sd2 = m2.state_dict()
    avg_sd = {}
    for k in sd1:
        if k in sd2:
            if sd1[k].is_floating_point():
                avg_sd[k] = w1 * sd1[k] + w2 * sd2[k]
            else:
                avg_sd[k] = sd2[k]
        else:
            avg_sd[k] = sd1[k]

    m2.load_state_dict(avg_sd)
    m2.save_pretrained(out_dir)
    tok.save_pretrained(out_dir)
    del m1, m2
    print(f"Saved averaged checkpoint to {out_dir}")


def main():
    print("Creating SWA checkpoint (w1=0.4, w2=0.6)...")
    create_averaged_checkpoint(EP1_DIR, EP2_DIR, SWA_DIR, w1=0.4, w2=0.6)

    engine = GLiClassEngine(model_id=str(SWA_DIR), device="cuda:0")
    bridge_records = load_jsonl(BRIDGE_FILE)
    ev2_records = load_jsonl(EVAL_V2_FILE)

    res_bridge = evaluate_records(engine, bridge_records, test_permutation=True, seed=42)
    res_ev2 = evaluate_records(engine, ev2_records, test_permutation=False)

    print("\n=== SWA CHECKPOINT EVALUATION RESULTS ===")
    print(f"Bridge Overall Acc: {res_bridge['accuracy']*100:.2f}% ({res_bridge['correct']}/{res_bridge['total_cases']})")
    print(f"Paired Both Rate:   {res_bridge['paired_both_rate']*100:.2f}% ({res_bridge['paired_both']}/{res_bridge['paired_total']})")
    print(f"Permutation:        {res_bridge['permutation_consistency']*100:.2f}%")
    print(f"eval_v2 Core Acc:   {res_ev2['accuracy']*100:.2f}% ({res_ev2['correct']}/{res_ev2['total_cases']})")

    print("\nBy Family:")
    for fam, s in res_bridge["by_family"].items():
        print(f"  - {fam:25s}: {s['correct']:2d}/{s['total']:2d} ({s['accuracy']*100:5.2f}%)")


if __name__ == "__main__":
    main()
