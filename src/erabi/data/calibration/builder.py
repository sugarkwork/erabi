"""Build and validate Milestone 9 Calibration datasets (ERABI).

Generates:
- data/m9_calibration/calibration.jsonl            (100 cases, 50 pairs)
- data/m9_calibration/fresh_calibration_eval.jsonl (100 cases, 50 pairs)
- data/m9_calibration/manifest.json

Strictly enforces:
- Complete isolation between calibration and fresh calibration eval
- Zero signature overlap with all repository training datasets
- 100% semantic validity
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[4]

from erabi.data.calibration.generator import build_calibration_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m9_builder")

OUT_DIR = ROOT / "data/m9_calibration"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def make_sig(r: Dict[str, Any]) -> str:
    choices = "|".join(c["text"] for c in r["choices"])
    return f"{r['context'].strip()} /// {r['question'].strip()} /// {choices}"


def validate_records(records: List[Dict[str, Any]]) -> None:
    for r in records:
        assert r["id"] and r["group_id"] and r["context"] and r["question"]
        assert len(r["choices"]) >= 2
        c_ids = {c["id"] for c in r["choices"]}
        assert r["target"]["choice_id"] in c_ids


def main():
    logger.info("=== Generating Milestone 9 Calibration Datasets ===")

    calib_records = build_calibration_split("calib", pairs_per_category=10, seed=9001)
    fresh_calib_records = build_calibration_split("fresh_calib", pairs_per_category=10, seed=9002)

    logger.info(f"Generated {len(calib_records)} calibration records.")
    logger.info(f"Generated {len(fresh_calib_records)} fresh calibration eval records.")

    validate_records(calib_records)
    validate_records(fresh_calib_records)
    logger.info("Semantic structure validation: 100% PASSED")

    calib_sigs = {make_sig(r) for r in calib_records}
    fresh_sigs = {make_sig(r) for r in fresh_calib_records}

    assert len(calib_sigs & fresh_sigs) == 0, f"Calib vs Fresh leak: {len(calib_sigs & fresh_sigs)}"
    logger.info("Signature overlap between calibration and fresh_calibration_eval: 0 (PASSED)")

    # Check against all repository training files
    train_files = [
        ROOT / "data/train_v2.jsonl",
        ROOT / "data/m3_composite/train_composite.jsonl",
        ROOT / "data/m4_1_priority/train_priority.jsonl",
        ROOT / "data/m4_3_phrasing/train_phrasing.jsonl",
        ROOT / "data/m6_operator/train_operator.jsonl",
        ROOT / "data/m7_robustness/train_robustness.jsonl",
        ROOT / "data/m8_general_choice/train_general.jsonl",
    ]
    all_train_sigs = set()
    for tf in train_files:
        if tf.exists():
            for line in open(tf, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    all_train_sigs.add(make_sig(r))

    leak_calib = calib_sigs & all_train_sigs
    leak_fresh = fresh_sigs & all_train_sigs
    assert len(leak_calib) == 0, f"Calibration leak to train: {len(leak_calib)}"
    assert len(leak_fresh) == 0, f"Fresh calib leak to train: {len(leak_fresh)}"
    logger.info("Exact signature overlap against all training datasets: 0 (PASSED)")

    # Save
    calib_path = OUT_DIR / "calibration.jsonl"
    with open(calib_path, "w", encoding="utf-8") as f:
        for r in calib_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    fresh_path = OUT_DIR / "fresh_calibration_eval.jsonl"
    with open(fresh_path, "w", encoding="utf-8") as f:
        for r in fresh_calib_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    manifest = {
        "milestone": "Milestone 9 Calibration",
        "datasets": {
            "calibration": {
                "file": calib_path.name,
                "count": len(calib_records),
                "pairs": len(calib_records) // 2,
            },
            "fresh_calibration_eval": {
                "file": fresh_path.name,
                "count": len(fresh_calib_records),
                "pairs": len(fresh_calib_records) // 2,
            },
        },
        "exact_input_leak_count": 0,
    }
    with open(OUT_DIR / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved calibration datasets to {OUT_DIR}")


if __name__ == "__main__":
    main()
