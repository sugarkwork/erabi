"""Sidecar manifest and cache management for ERABI raw logits (M3.7).

Guarantees:
- Saves raw logits alongside a cryptographic sidecar manifest (.manifest.json).
- Binds logits strictly to:
  1. Model checkpoint directory and constituent file SHA256 hashes.
  2. Input dataset JSONL SHA256 hash and exact case count.
  3. Formatter version and forward precision contract.
  4. Exact candidate ID order and target index integrity.
- Refuses to reuse stale or mismatched cache files without explicit verification.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from erabi.schema import (
    FORMATTER_VERSION,
    RUNTIME_PRECISION_CONTRACT,
    compute_file_sha256,
)

logger = logging.getLogger("erabi.cache")


def extract_alignment_signature(record: Dict[str, Any]) -> str:
    """Extract canonical alignment signature string for a single record.
    
    Format: "{id}|{ordered_choice_ids}|{target_choice_id}|{target_index}"
    """
    rec_id = str(record.get("id", ""))
    raw_choices = record.get("choices", [])
    choice_ids = [str(c["id"]) for c in raw_choices if isinstance(c, dict) and "id" in c]

    tgt_obj = record.get("target")
    if isinstance(tgt_obj, dict):
        tgt_id = str(tgt_obj.get("choice_id", ""))
    else:
        tgt_id = str(tgt_obj or "")

    tgt_idx = record.get("target_index")
    if tgt_idx is None and tgt_id in choice_ids:
        tgt_idx = choice_ids.index(tgt_id)
    tgt_idx_str = str(tgt_idx) if tgt_idx is not None else ""

    return f"{rec_id}|{','.join(choice_ids)}|{tgt_id}|{tgt_idx_str}"


def compute_records_alignment_sha256(records: List[Dict[str, Any]]) -> str:
    """Compute overall SHA256 digest of alignment signatures across all records."""
    hasher = hashlib.sha256()
    for r in records:
        sig = extract_alignment_signature(r)
        hasher.update((sig + "\n").encode("utf-8"))
    return hasher.hexdigest()


def compute_file_alignment_sha256(file_path: Path | str) -> str:
    """Compute overall alignment SHA256 from a JSONL dataset file."""
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line_s = line.strip()
            if line_s:
                records.append(json.loads(line_s))
    return compute_records_alignment_sha256(records)


def get_checkpoint_hashes(checkpoint_dir: Path | str) -> Dict[str, str]:
    """Compute sha256 hashes for all primary files in the checkpoint directory."""
    cp_path = Path(checkpoint_dir)
    if not cp_path.is_dir():
        raise FileNotFoundError(f"Checkpoint directory '{checkpoint_dir}' does not exist.")
    hashes = {}
    for fname in sorted(os.listdir(cp_path)):
        fpath = cp_path / fname
        if fpath.is_file():
            hashes[fname] = compute_file_sha256(fpath)
    return hashes


def save_logits_with_manifest(
    logits_path: Path | str,
    raw_records: List[Dict[str, Any]],
    model_dir: Path | str,
    data_path: Path | str,
    precision: str = RUNTIME_PRECISION_CONTRACT,
    formatter_version: str = FORMATTER_VERSION,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """Save raw logits to JSONL and write an associated cryptographic sidecar manifest."""
    l_path = Path(logits_path)
    l_path.parent.mkdir(parents=True, exist_ok=True)

    # 1. Verify alignment between dataset file and raw_records
    dataset_align_sha256 = compute_file_alignment_sha256(data_path)
    records_align_sha256 = compute_records_alignment_sha256(raw_records)
    if dataset_align_sha256 != records_align_sha256:
        raise ValueError(
            f"Dataset alignment mismatch: dataset '{Path(data_path).name}' digest is {dataset_align_sha256}, "
            f"but logits records digest is {records_align_sha256}. ID, choices, or target order do not match!"
        )

    # 2. Write logits JSONL
    with open(l_path, "w", encoding="utf-8") as f:
        for r in raw_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    logits_sha256 = compute_file_sha256(l_path)
    checkpoint_hashes = get_checkpoint_hashes(model_dir)
    data_sha256 = compute_file_sha256(data_path)

    # 3. Construct sidecar manifest
    manifest_path = l_path.with_suffix(".manifest.json")
    manifest = {
        "manifest_version": "1",
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "logits_file": l_path.name,
        "logits_sha256": logits_sha256,
        "records_count": len(raw_records),
        "alignment_sha256": records_align_sha256,
        "model": {
            "checkpoint_dir": str(Path(model_dir).resolve()),
            "files": checkpoint_hashes,
        },
        "dataset": {
            "path": str(Path(data_path).resolve()),
            "sha256": data_sha256,
            "records_count": len(raw_records),
            "alignment_sha256": dataset_align_sha256,
        },
        "contract": {
            "formatter_version": formatter_version,
            "precision": precision,
        },
        "extra_metadata": extra_metadata or {},
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved logits ({len(raw_records)} cases) to {l_path} with manifest {manifest_path.name}")
    return manifest_path


def load_logits_with_manifest(
    logits_path: Path | str,
    model_dir: Path | str,
    data_path: Path | str,
    precision: str = RUNTIME_PRECISION_CONTRACT,
    formatter_version: str = FORMATTER_VERSION,
) -> List[Dict[str, Any]]:
    """Load and strictly verify raw logits using sidecar manifest.
    
    Raises ValueError or FileNotFoundError if verification fails.
    """
    l_path = Path(logits_path)
    manifest_path = l_path.with_suffix(".manifest.json")

    if not l_path.is_file():
        raise FileNotFoundError(f"Logits file not found: {l_path}")
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Sidecar manifest not found: {manifest_path}")

    # Verify manifest
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Check logits SHA256
    actual_logits_sha256 = compute_file_sha256(l_path)
    expected_logits_sha256 = manifest.get("logits_sha256")
    if actual_logits_sha256 != expected_logits_sha256:
        raise ValueError(
            f"Logits file SHA256 mismatch for '{l_path.name}': "
            f"expected {expected_logits_sha256}, got {actual_logits_sha256}"
        )

    # Check dataset SHA256
    actual_data_sha256 = compute_file_sha256(data_path)
    expected_data_sha256 = manifest.get("dataset", {}).get("sha256")
    if actual_data_sha256 != expected_data_sha256:
        raise ValueError(
            f"Dataset SHA256 mismatch for '{Path(data_path).name}': "
            f"expected {expected_data_sha256}, got {actual_data_sha256}"
        )

    # Check model checkpoint hashes
    current_checkpoint_hashes = get_checkpoint_hashes(model_dir)
    expected_model_files = manifest.get("model", {}).get("files", {})
    if not expected_model_files:
        raise ValueError(f"Manifest missing model file hashes: {manifest_path}")

    for fname, exp_hash in expected_model_files.items():
        curr_hash = current_checkpoint_hashes.get(fname)
        if curr_hash != exp_hash:
            raise ValueError(
                f"Model file hash mismatch for '{fname}': expected {exp_hash}, got {curr_hash}"
            )

    # Check contract
    manifest_contract = manifest.get("contract", {})
    if manifest_contract.get("formatter_version") != formatter_version:
        raise ValueError(
            f"Formatter version mismatch: expected '{formatter_version}', "
            f"got '{manifest_contract.get('formatter_version')}'"
        )
    if manifest_contract.get("precision") != precision:
        raise ValueError(
            f"Precision mismatch: expected '{precision}', "
            f"got '{manifest_contract.get('precision')}'"
        )

    # Load records
    records = []
    with open(l_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    if len(records) != manifest.get("records_count"):
        raise ValueError(
            f"Record count mismatch in '{l_path.name}': "
            f"expected {manifest.get('records_count')}, got {len(records)}"
        )

    # Check alignment digest if present
    expected_align_sha256 = manifest.get("alignment_sha256")
    if expected_align_sha256:
        dataset_align_sha256 = compute_file_alignment_sha256(data_path)
        if dataset_align_sha256 != expected_align_sha256:
            raise ValueError(
                f"Dataset alignment mismatch: expected {expected_align_sha256}, got {dataset_align_sha256}"
            )
        records_align_sha256 = compute_records_alignment_sha256(records)
        if records_align_sha256 != expected_align_sha256:
            raise ValueError(
                f"Logits records alignment mismatch: expected {expected_align_sha256}, got {records_align_sha256}"
            )

    logger.info(f"Verified and loaded {len(records)} logits from {l_path} via sidecar manifest.")
    return records
