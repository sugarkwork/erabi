"""Build, audit, and seal RC3.1 logic-recovery artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from .audit import (
    ROOT,
    audit_balance,
    audit_historical_overlap,
    audit_split_isolation,
    audit_token_contract,
    load_blind_v5_records,
    load_historical_records,
    sha256_file,
)
from .generator import CONDITION_ORDERS, MAPPING_STYLES, OPERATOR_FAMILIES, generate_bridge_records, generate_train_records
from .validator import validate_records


TRAIN_DIR = ROOT / "data" / "rc3_1_train"
BRIDGE_DIR = ROOT / "data" / "rc3_1_logic_bridge"
TOKENIZER_DIR = ROOT / "release" / "rc3" / "model"
BUILD_VERSION = "rc3.1-logic-recovery-v2"


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: Sequence[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _records_by_split(records: Sequence[Mapping[str, Any]]) -> Dict[str, List[Mapping[str, Any]]]:
    result: Dict[str, List[Mapping[str, Any]]] = {"train": [], "dev": [], "calibration": []}
    for record in records:
        split = str(record.get("split"))
        if split not in result:
            raise ValueError(f"Unexpected train split: {split}")
        result[split].append(record)
    return result


def _audit_dataset(
    records: Sequence[Mapping[str, Any]],
    historical: Sequence[Mapping[str, Any]],
    historical_paths: Sequence[str],
    blind_v5_records: Sequence[Mapping[str, Any]],
    blind_v5_paths: Sequence[str],
    label: str,
) -> Dict[str, Any]:
    semantic = validate_records(records)
    derived = []
    # Re-run through the independent derivation result only for balance counts.
    from .validator import derive_record

    for record in records:
        derived.append(derive_record(record))
    overlap = audit_historical_overlap(
        records,
        historical,
        historical_paths,
        blind_v5_records=blind_v5_records,
        blind_v5_paths=blind_v5_paths,
    )
    balance = audit_balance(records, derived)
    if not semantic["is_valid"]:
        raise ValueError(f"{label} semantic audit failed: {semantic['errors'][:5]}")
    if not overlap["is_clean"]:
        raise ValueError(f"{label} historical overlap audit failed: {overlap}")
    if not balance["is_balanced"]:
        raise ValueError(f"{label} balance audit failed: {balance}")
    return {"semantic": semantic, "historical_overlap": overlap, "balance": balance}


def build() -> Dict[str, Any]:
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)

    train_records = generate_train_records(seed=3102)
    bridge_records = generate_bridge_records(seed=3101)
    historical, historical_paths = load_historical_records(ROOT)
    blind_v5_records, blind_v5_paths = load_blind_v5_records(ROOT)

    train_splits = _records_by_split(train_records)
    train_audit = _audit_dataset(
        train_records,
        historical,
        historical_paths,
        blind_v5_records,
        blind_v5_paths,
        "train corpus",
    )
    bridge_audit = _audit_dataset(
        bridge_records,
        historical,
        historical_paths,
        blind_v5_records,
        blind_v5_paths,
        "logic bridge",
    )
    split_audit = audit_split_isolation(train_splits)
    if not split_audit["is_clean"]:
        raise ValueError(f"RC3.1 train/dev/calibration isolation failed: {split_audit}")

    # Bridge and training data must also be isolated from each other.
    cross_split_audit = audit_split_isolation({"train_corpus": train_records, "logic_bridge": bridge_records})
    if not cross_split_audit["is_clean"]:
        raise ValueError(f"RC3.1 train/bridge isolation failed: {cross_split_audit}")

    token_train = audit_token_contract(train_records, TOKENIZER_DIR)
    token_bridge = audit_token_contract(bridge_records, TOKENIZER_DIR)
    if not token_train["is_compliant"] or not token_bridge["is_compliant"]:
        raise ValueError("RC3.1 token contract failed")

    for split, records in train_splits.items():
        _write_jsonl(TRAIN_DIR / f"{split if split != 'calibration' else 'calibration'}.jsonl", records)
    bridge_path = BRIDGE_DIR / "benchmark.jsonl"
    _write_jsonl(bridge_path, bridge_records)

    # Audit files are deterministic: no wall-clock timestamps are embedded.
    train_split_counts = {split: len(records) for split, records in train_splits.items()}
    train_manifest = {
        "build_version": BUILD_VERSION,
        "seed": 3102,
        "total_records": len(train_records),
        "total_pairs": len(train_records) // 2,
        "operator_families": list(OPERATOR_FAMILIES),
        "mapping_styles": list(MAPPING_STYLES),
        "condition_orders": ["".join(order) for order in CONDITION_ORDERS],
        "split_counts": train_split_counts,
        "audits": {
            "semantic": train_audit["semantic"]["is_valid"],
            "historical_overlap": train_audit["historical_overlap"]["is_clean"],
            "balance": train_audit["balance"]["is_balanced"],
            "split_isolation": split_audit["is_clean"],
            "cross_bridge_isolation": cross_split_audit["is_clean"],
            "token_contract": token_train["is_compliant"],
        },
        "historical_files_audited": historical_paths,
        "blind_v5_files_audited": blind_v5_paths,
        "token_summary": {k: token_train[k] for k in ("max_tokens", "min_tokens", "avg_tokens")},
    }
    bridge_manifest = {
        "build_version": BUILD_VERSION,
        "seed": 3101,
        "total_records": len(bridge_records),
        "total_pairs": len(bridge_records) // 2,
        "operator_families": list(OPERATOR_FAMILIES),
        "mapping_styles": list(MAPPING_STYLES),
        "condition_orders": ["".join(order) for order in CONDITION_ORDERS],
        "audits": {
            "semantic": bridge_audit["semantic"]["is_valid"],
            "historical_overlap": bridge_audit["historical_overlap"]["is_clean"],
            "balance": bridge_audit["balance"]["is_balanced"],
            "train_isolation": cross_split_audit["is_clean"],
            "token_contract": token_bridge["is_compliant"],
        },
        "historical_files_audited": historical_paths,
        "blind_v5_files_audited": blind_v5_paths,
        "token_summary": {k: token_bridge[k] for k in ("max_tokens", "min_tokens", "avg_tokens")},
    }

    _write_json(TRAIN_DIR / "semantic_audit.json", train_audit["semantic"])
    _write_json(TRAIN_DIR / "overlap_audit.json", train_audit["historical_overlap"])
    _write_json(TRAIN_DIR / "balance_audit.json", train_audit["balance"])
    _write_json(TRAIN_DIR / "split_audit.json", split_audit)
    _write_json(TRAIN_DIR / "cross_bridge_audit.json", cross_split_audit)
    _write_json(TRAIN_DIR / "token_audit.json", token_train)
    _write_json(BRIDGE_DIR / "semantic_audit.json", bridge_audit["semantic"])
    _write_json(BRIDGE_DIR / "overlap_audit.json", bridge_audit["historical_overlap"])
    _write_json(BRIDGE_DIR / "balance_audit.json", bridge_audit["balance"])
    _write_json(BRIDGE_DIR / "train_isolation_audit.json", cross_split_audit)
    _write_json(BRIDGE_DIR / "token_audit.json", token_bridge)
    _write_json(TRAIN_DIR / "manifest.json", train_manifest)
    _write_json(BRIDGE_DIR / "manifest.json", bridge_manifest)

    train_files = [TRAIN_DIR / f"{split if split != 'calibration' else 'calibration'}.jsonl" for split in train_splits]
    train_hashes = {path.name: sha256_file(path) for path in train_files}
    bridge_hash = sha256_file(bridge_path)
    train_manifest["file_hashes"] = train_hashes
    bridge_manifest["file_hashes"] = {bridge_path.name: bridge_hash}
    _write_json(TRAIN_DIR / "manifest.json", train_manifest)
    _write_json(BRIDGE_DIR / "manifest.json", bridge_manifest)

    report = [
        "# ERABI RC3.1 Logic Recovery Data Report",
        "",
        f"Build: `{BUILD_VERSION}`",
        "",
        "Blind v5 was audited as historical data only; no Blind v5 generator, text, or numeric state was imported.",
        "",
        "## Train / dev / calibration",
        "",
        f"- Records: {len(train_records)} ({len(train_records) // 2} pairs)",
        f"- Split records: {train_split_counts}",
        f"- Token max/avg: {token_train['max_tokens']} / {token_train['avg_tokens']}",
        "- Semantic, exact/normalized/fuzzy historical-overlap, split-isolation, balance, and token audits: PASS",
        "",
        "## Logic Bridge",
        "",
        f"- Records: {len(bridge_records)} ({len(bridge_records) // 2} contrastive pairs)",
        f"- Token max/avg: {token_bridge['max_tokens']} / {token_bridge['avg_tokens']}",
        "- Semantic, exact/normalized/fuzzy historical-overlap, train-isolation, balance, and token audits: PASS",
        "",
        "## Frozen-boundary note",
        "",
        "Existing RC3 artifacts and Blind v5 were not modified. GPU training, calibration, ONNX export, and Blind v6 were not run.",
        "",
    ]
    (TRAIN_DIR / "RC3_1_TRAIN_DATA_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (BRIDGE_DIR / "RC3_1_LOGIC_BRIDGE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    return {
        "train_dir": str(TRAIN_DIR),
        "bridge_dir": str(BRIDGE_DIR),
        "train_records": len(train_records),
        "bridge_records": len(bridge_records),
        "train_hashes": train_hashes,
        "bridge_hash": bridge_hash,
        "train_token_audit": token_train,
        "bridge_token_audit": token_bridge,
    }


def main() -> None:
    result = build()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
