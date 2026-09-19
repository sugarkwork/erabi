"""Unit tests for M4.4-R Targeted Retention Replay data integrity and isolation."""

import hashlib
import json
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
M3_TRAIN = ROOT / "data/m3_3_v2/train.jsonl"
M3_DEV = ROOT / "data/m3_3_v2/dev.jsonl"
EVAL_V2 = ROOT / "data/m3_3_v2/eval_v2.jsonl"
TRANSFER_PROBE = ROOT / "data/m3_1/transfer_probe.jsonl"
SMOKE_CASES = ROOT / "examples/smoke_cases.jsonl"
FRESH_EVAL = ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl"

RETENTION_DIR = ROOT / "data/m4_4_retention"
COMBINED_TRAIN = RETENTION_DIR / "combined_train_retention.jsonl"
MANIFEST = RETENTION_DIR / "retention_manifest.json"


def test_retention_replay_data_isolation():
    """Verify that replayed records are drawn exclusively from M3 train with 0 overlap to eval/dev sets."""
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    replayed_ids = set(manifest["replayed_ids"])

    m3_train_ids = set(json.loads(l)["id"] for l in open(M3_TRAIN, encoding="utf-8") if l.strip())
    dev_ids = set(json.loads(l)["id"] for l in open(M3_DEV, encoding="utf-8") if l.strip())
    eval_v2_ids = set(json.loads(l)["id"] for l in open(EVAL_V2, encoding="utf-8") if l.strip())
    tp_ids = set(json.loads(l)["id"] for l in open(TRANSFER_PROBE, encoding="utf-8") if l.strip())
    smoke_ids = set(json.loads(l)["id"] for l in open(SMOKE_CASES, encoding="utf-8") if l.strip())
    fresh_ids = set(json.loads(l)["id"] for l in open(FRESH_EVAL, encoding="utf-8") if l.strip())

    # All replayed IDs must belong to M3 train
    assert replayed_ids.issubset(m3_train_ids), "Replayed IDs must strictly be a subset of M3 train"

    # Zero overlap with evaluation or dev datasets
    assert len(replayed_ids & dev_ids) == 0, "Contamination: replayed records overlap with dev"
    assert len(replayed_ids & eval_v2_ids) == 0, "Contamination: replayed records overlap with eval_v2"
    assert len(replayed_ids & tp_ids) == 0, "Contamination: replayed records overlap with transfer_probe"
    assert len(replayed_ids & smoke_ids) == 0, "Contamination: replayed records overlap with smoke_cases"
    assert len(replayed_ids & fresh_ids) == 0, "Contamination: replayed records overlap with fresh_phrasing_eval"


def test_r1_equality_boundary():
    """Verify that all R1 candidates have actual == threshold and intact pairs."""
    m3_train = {json.loads(l)["id"]: json.loads(l) for l in open(M3_TRAIN, encoding="utf-8") if l.strip()}
    audit = json.load(open(ROOT / "runs/m4_4_retention/retention_source_audit.json", encoding="utf-8"))
    r1_gids = audit["r1_equality_boundary"]["group_ids"]

    assert len(r1_gids) == 24, "R1 must have exactly 24 groups"
    assert audit["r1_equality_boundary"]["total_cases"] == 48

    for gid in r1_gids:
        c1 = m3_train[f"{gid}-c1"]
        c2 = m3_train[f"{gid}-c2"]

        assert c1["rule_kind"] == "boundary"
        assert c2["rule_kind"] == "boundary"

        # Check equality condition
        nums_ctx = [int(x) for x in re.findall(r"\d+", c1["context"])]
        nums_q = [int(x) for x in re.findall(r"\d+", c1["question"])]
        assert nums_ctx and nums_q and nums_ctx[0] == nums_q[0], f"Group {gid} must have actual == threshold"


def test_r2_composite_logic_4_states():
    """Verify that R2 composite logic is balanced across 4 states with 7 groups each."""
    m3_train = {json.loads(l)["id"]: json.loads(l) for l in open(M3_TRAIN, encoding="utf-8") if l.strip()}
    audit = json.load(open(ROOT / "runs/m4_4_retention/retention_source_audit.json", encoding="utf-8"))
    states = audit["r2_composite_logic"]["states"]

    assert len(states) == 4
    for st_name, st_info in states.items():
        assert st_info["selected_groups"] == 7, f"State {st_name} must have 7 selected groups"
        assert st_info["selected_cases"] == 14, f"State {st_name} must have 14 selected cases"

        for gid in st_info["selected_group_ids"]:
            c1 = m3_train[f"{gid}-c1"]
            c2 = m3_train[f"{gid}-c2"]
            assert c1["rule_kind"] == "composite_logic"
            assert c2["rule_kind"] == "composite_logic"


def test_replay_cap_compliance():
    """Verify total replay cases <= 160 and total combined train <= 1240."""
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    assert manifest["base_components"]["retention_replay"]["count"] <= 160
    assert manifest["base_components"]["retention_replay"]["count"] == 104
    assert manifest["total_records"] <= 1240
    assert manifest["total_records"] == 1184


def test_manifest_integrity():
    """Verify manifest SHA-256 and record count."""
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    lines = [json.loads(l) for l in open(COMBINED_TRAIN, encoding="utf-8") if l.strip()]

    assert len(lines) == manifest["total_records"]
    assert manifest["replayed_records_count"] == 104

    h = hashlib.sha256()
    with open(COMBINED_TRAIN, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    assert h.hexdigest() == manifest["combined_train_sha256"]
