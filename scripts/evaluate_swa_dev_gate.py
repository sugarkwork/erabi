"""Build optimal SWA checkpoint (w1=0.44, w2=0.56) and run full Milestone 31 Development Gate evaluation."""

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

from scripts.train_rc3 import evaluate_development_gate

EP1_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_1"
EP2_DIR = ROOT / "runs" / "rc3_large_curriculum" / "checkpoints" / "epoch_2"
SWA_BEST_DIR = ROOT / "runs" / "rc3_large_curriculum" / "best_model_swa"
OUT_DIR = ROOT / "runs" / "rc3_large_curriculum" / "swa_gate_results"


def main():
    print("Building SWA checkpoint (w1=0.44, w2=0.56)...")
    SWA_BEST_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    m1 = GLiClassModel.from_pretrained(EP1_DIR)
    m2 = GLiClassModel.from_pretrained(EP2_DIR)
    tok = AutoTokenizer.from_pretrained(EP2_DIR)

    sd1 = m1.state_dict()
    sd2 = m2.state_dict()
    avg_sd = {}
    for k in sd1:
        if k in sd2:
            if sd1[k].is_floating_point():
                avg_sd[k] = 0.44 * sd1[k] + 0.56 * sd2[k]
            else:
                avg_sd[k] = sd2[k]
        else:
            avg_sd[k] = sd1[k]

    m2.load_state_dict(avg_sd)
    m2.save_pretrained(SWA_BEST_DIR)
    tok.save_pretrained(SWA_BEST_DIR)
    del m1, m2
    print(f"Saved SWA checkpoint to {SWA_BEST_DIR}")

    print("\nRunning Milestone 31 Development Gate Evaluation...")
    res = evaluate_development_gate(SWA_BEST_DIR, device="cuda:0", output_dir=OUT_DIR)
    print(f"\nGate Complete! Gate Passed: {res['milestone_31_gate_passed']}")


if __name__ == "__main__":
    main()
