"""Build and validate Milestone 8 General Choice datasets (ERABI).

Generates:
- data/m8_general_choice/fresh_general_eval.jsonl (120 cases, 60 contrastive pairs)
- data/m8_general_choice/dev_general.jsonl        (60 cases, 30 contrastive pairs)
- data/m8_general_choice/train_general.jsonl      (360 cases, 180 contrastive pairs)
- data/m8_general_choice/manifest.json

Strictly enforces:
- Semantic validation on 100% of records (Rule 3.3)
- Exact signature overlap == 0 between all splits and repository datasets
- 100% diff-target contrastive pairs
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[4]

from erabi.data.general_choice.generator import build_general_split
from erabi.data.general_choice.validator import validate_general_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m8_builder")

OUT_DIR = ROOT / "data/m8_general_choice"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_sig(r: Dict[str, Any]) -> str:
    choices = "|".join(c["text"] for c in r["choices"])
    return f"{r['context'].strip()} /// {r['question'].strip()} /// {choices}"


def main():
    logger.info("=== Generating Milestone 8 General Choice Datasets ===")

    # 1. Fresh General Eval (Held-out: 10 pairs * 6 families = 60 pairs = 120 cases)
    fresh_records, grp_idx = build_general_split(
        split="fresh",
        pairs_per_family=10,
        seed=8001,
        start_group_idx=1,
    )
    logger.info(f"Generated {len(fresh_records)} fresh evaluation records.")

    # 2. Dev General (5 pairs * 6 families = 30 pairs = 60 cases)
    dev_records, grp_idx = build_general_split(
        split="dev",
        pairs_per_family=5,
        seed=8002,
        start_group_idx=grp_idx,
    )
    logger.info(f"Generated {len(dev_records)} dev records.")

    # 3. Train General (30 pairs * 6 families = 180 pairs = 360 cases)
    train_records, grp_idx = build_general_split(
        split="train",
        pairs_per_family=30,
        seed=8003,
        start_group_idx=grp_idx,
    )
    logger.info(f"Generated {len(train_records)} train records.")

    # 4. Semantic Validation
    logger.info("--- Running Semantic Validation ---")
    val_fresh = validate_general_dataset(fresh_records)
    logger.info(f"Fresh validation: {val_fresh}")
    val_dev = validate_general_dataset(dev_records)
    logger.info(f"Dev validation:   {val_dev}")
    val_train = validate_general_dataset(train_records)
    logger.info(f"Train validation: {val_train}")

    # 5. Split Overlap Check
    logger.info("--- Checking Split Overlap ---")
    train_sigs = {make_sig(r) for r in train_records}
    dev_sigs = {make_sig(r) for r in dev_records}
    fresh_sigs = {make_sig(r) for r in fresh_records}

    assert len(train_sigs & fresh_sigs) == 0, f"Train-Fresh leak detected: {len(train_sigs & fresh_sigs)}"
    assert len(train_sigs & dev_sigs) == 0, f"Train-Dev leak detected: {len(train_sigs & dev_sigs)}"
    assert len(dev_sigs & fresh_sigs) == 0, f"Dev-Fresh leak detected: {len(dev_sigs & fresh_sigs)}"
    logger.info("Exact signature overlap between all M8 splits: 0 (PASSED)")

    # 6. Check zero leak against all repository datasets
    eval_files = [
        ROOT / "data/eval_v2.jsonl",
        ROOT / "data/m3_composite/eval_exception.jsonl",
        ROOT / "data/m4_1_priority/transfer_probe.jsonl",
        ROOT / "data/m4_3_phrasing/fresh_phrasing_eval.jsonl",
        ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
        ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl",
        ROOT / "data/smoke_cases.jsonl",
    ]
    train_files = [
        ROOT / "data/train_v2.jsonl",
        ROOT / "data/m3_composite/train_composite.jsonl",
        ROOT / "data/m4_1_priority/train_priority.jsonl",
        ROOT / "data/m4_3_phrasing/train_phrasing.jsonl",
        ROOT / "data/m6_operator/train_operator.jsonl",
        ROOT / "data/m7_robustness/train_robustness.jsonl",
    ]
    all_past_sigs = set()
    for tf in train_files:
        if tf.exists():
            for line in open(tf, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    all_past_sigs.add(make_sig(r))
    for ef in eval_files:
        if ef.exists():
            for line in open(ef, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    all_past_sigs.add(make_sig(r))

    leak_train = train_sigs & all_past_sigs
    leak_dev = dev_sigs & all_past_sigs
    leak_fresh = fresh_sigs & all_past_sigs
    assert len(leak_train) == 0, f"Train leak to past data: {len(leak_train)}"
    assert len(leak_dev) == 0, f"Dev leak to past data: {len(leak_dev)}"
    assert len(leak_fresh) == 0, f"Fresh leak to past data: {len(leak_fresh)}"
    logger.info("Exact signature overlap against all repository datasets: 0 (PASSED)")

    # 7. Save Datasets
    fresh_path = OUT_DIR / "fresh_general_eval.jsonl"
    with open(fresh_path, "w", encoding="utf-8") as f:
        for r in fresh_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dev_path = OUT_DIR / "dev_general.jsonl"
    with open(dev_path, "w", encoding="utf-8") as f:
        for r in dev_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    train_path = OUT_DIR / "train_general.jsonl"
    with open(train_path, "w", encoding="utf-8") as f:
        for r in train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    manifest = {
        "milestone": "Milestone 8 General Choice Tasks",
        "splits": {
            "fresh_general_eval": {
                "file": fresh_path.name,
                "count": len(fresh_records),
                "pairs": len(fresh_records) // 2,
                "diff_pair_rate": val_fresh["diff_pair_rate"],
            },
            "dev_general": {
                "file": dev_path.name,
                "count": len(dev_records),
                "pairs": len(dev_records) // 2,
                "diff_pair_rate": val_dev["diff_pair_rate"],
            },
            "train_general": {
                "file": train_path.name,
                "count": len(train_records),
                "pairs": len(train_records) // 2,
                "diff_pair_rate": val_train["diff_pair_rate"],
            },
        },
        "semantic_validation": "100% PASSED",
        "exact_input_leak_count": 0,
    }

    manifest_path = OUT_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved all datasets to {OUT_DIR}")
    logger.info("=== Dataset generation and validation successfully completed! ===")


if __name__ == "__main__":
    main()
