"""Freeze Milestone 6 Passing Checkpoint as W_operator_v1 (ERABI).

Preserves:
- Model weights and tokenizer in runs/m6_operator/checkpoint/
- Metadata manifest with SHA256 hashes
- Full benchmark report and audit report
- Review bundle zip: runs/m6_operator/review_bundle.zip
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.freeze_m6_operator")

SRC_CKPT = ROOT / "runs/m6_e2_diversified/checkpoints/epoch_7"
DST_DIR = ROOT / "runs/m6_operator"
DST_CKPT = DST_DIR / "checkpoint"
AUDIT_SRC = ROOT / "runs/m6_e2_diversified/audit"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    logger.info("=== Freezing Milestone 6 W_operator_v1 ===")
    DST_DIR.mkdir(parents=True, exist_ok=True)
    DST_CKPT.mkdir(parents=True, exist_ok=True)

    # 1. Copy checkpoint files
    for item in SRC_CKPT.iterdir():
        if item.is_file():
            shutil.copy2(item, DST_CKPT / item.name)
            logger.info(f"Copied {item.name} -> {DST_CKPT / item.name}")

    # 2. Copy audit files
    shutil.copy2(AUDIT_SRC / "m6_audit_summary.json", DST_DIR / "m6_audit_summary.json")
    shutil.copy2(ROOT / "runs/m6_e2_diversified/notes.md", DST_DIR / "training_notes.md")

    # 3. Calculate file hashes
    file_hashes = {}
    for f in sorted(DST_CKPT.iterdir()):
        if f.is_file():
            file_hashes[f.name] = {
                "size_bytes": f.stat().st_size,
                "sha256": sha256_file(f),
            }

    audit_data = json.load(open(DST_DIR / "m6_audit_summary.json", encoding="utf-8"))

    manifest = {
        "model_name": "W_operator_v1",
        "milestone": "Milestone 6 Operator Generalization",
        "source_run": "runs/m6_e2_diversified/checkpoints/epoch_7",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_model": "knowledgator/gliclass-instruct-base-v1.0",
        "checkpoint_files": file_hashes,
        "gate_status": "PASSED",
        "key_metrics": {
            "fresh_operator_eval_accuracy": audit_data["metrics"]["fresh_operator_eval"]["accuracy"],
            "fresh_operator_eval_pair_both": audit_data["metrics"]["fresh_operator_eval"]["diff_both_rate"],
            "dev_operator_accuracy": audit_data["metrics"]["dev_operator"]["accuracy"],
            "dev_operator_pair_both": audit_data["metrics"]["dev_operator"]["diff_both_rate"],
            "eval_v2_accuracy": audit_data["metrics"]["eval_v2"]["accuracy"],
            "eval_v2_diff_both": audit_data["metrics"]["eval_v2"]["diff_both_rate"],
            "fresh_phrasing_accuracy": audit_data["metrics"]["fresh_phrasing_eval"]["accuracy"],
            "eval_exception_accuracy": audit_data["metrics"]["eval_exception"]["accuracy"],
            "smoke_cases_accuracy": audit_data["metrics"]["smoke_cases"]["accuracy"],
            "transfer_probe_accuracy": audit_data["metrics"]["transfer_probe"]["accuracy"],
            "permutation_consistency": audit_data["permutation_report"]["consistency_rate"],
            "split_exact_overlap": audit_data["overlap_report"]["total_leaks"],
        },
        "per_family_fresh_accuracy": {
            fam: fm["accuracy"] for fam, fm in audit_data["metrics"]["fresh_operator_eval"]["per_family"].items()
        },
    }

    manifest_path = DST_DIR / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved manifest to {manifest_path}")

    # 4. Create review bundle zip
    bundle_zip = DST_DIR / "review_bundle.zip"
    with zipfile.ZipFile(bundle_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, arcname="manifest.json")
        zf.write(DST_DIR / "m6_audit_summary.json", arcname="m6_audit_summary.json")
        zf.write(DST_DIR / "training_notes.md", arcname="training_notes.md")
        zf.write(ROOT / "runs/m6_e2_diversified/evaluation_report.json", arcname="evaluation_report.json")
        zf.write(AUDIT_SRC / "saved_predictions.json", arcname="saved_predictions.json")

    logger.info(f"Created review bundle: {bundle_zip} ({bundle_zip.stat().st_size:,} bytes, SHA256: {sha256_file(bundle_zip)})")
    logger.info("=== Milestone 6 W_operator_v1 Successfully Frozen! ===")


if __name__ == "__main__":
    main()
