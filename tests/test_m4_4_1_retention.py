"""Unit tests for ERABI M4.4.1 Targeted Retention Replay data integrity and isolation."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
M3_TRAIN = ROOT / "data/m3_3_v2/train.jsonl"
M3_DEV = ROOT / "data/m3_3_v2/dev.jsonl"
EVAL_V2 = ROOT / "data/m3_3_v2/eval_v2.jsonl"
TRANSFER = ROOT / "data/m3_1/transfer_probe.jsonl"
SMOKE = ROOT / "examples/smoke_cases.jsonl"
FRESH_EVAL = ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl"

M4_4_1_DATA_DIR = ROOT / "data/m4_4_1_retention"
COMBINED_TRAIN = M4_4_1_DATA_DIR / "combined_train_retention.jsonl"
MANIFEST = M4_4_1_DATA_DIR / "retention_manifest.json"
AUDIT = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"


def test_m4_4_1_replay_isolation_and_no_contamination():
    """Verify replay cases are strictly from M3 train and have 0 overlap with evaluation sets."""
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    replayed_ids = set(manifest["replayed_ids"])
    assert len(replayed_ids) == 112, f"Expected 112 replayed IDs, got {len(replayed_ids)}"

    m3_train_ids = {json.loads(l)["id"] for l in open(M3_TRAIN, encoding="utf-8") if l.strip()}
    assert replayed_ids.issubset(m3_train_ids), "Replayed IDs must be a strict subset of M3 train"

    eval_v2_ids = {json.loads(l)["id"] for l in open(EVAL_V2, encoding="utf-8") if l.strip()}
    fresh_ids = {json.loads(l)["id"] for l in open(FRESH_EVAL, encoding="utf-8") if l.strip()}
    transfer_ids = {json.loads(l)["id"] for l in open(TRANSFER, encoding="utf-8") if l.strip()}
    smoke_ids = {json.loads(l)["id"] for l in open(SMOKE, encoding="utf-8") if l.strip()}

    assert len(replayed_ids & eval_v2_ids) == 0, "Contamination: replayed cases overlap with eval_v2"
    assert len(replayed_ids & fresh_ids) == 0, "Contamination: replayed cases overlap with fresh_phrasing_eval"
    assert len(replayed_ids & transfer_ids) == 0, "Contamination: replayed cases overlap with transfer_probe"
    assert len(replayed_ids & smoke_ids) == 0, "Contamination: replayed cases overlap with smoke_cases"


def test_m4_4_1_r1b_comparison_coverage():
    """Verify R1b comparison equality groups are properly captured."""
    audit = json.load(open(AUDIT, encoding="utf-8"))
    r1b_info = audit["r1b_equality_comparison"]
    expected_gids = ["train-er-0031", "train-er-0151", "train-er-0199", "train-er-0283"]
    assert sorted(r1b_info["group_ids"]) == sorted(expected_gids)
    assert r1b_info["total_groups"] == 4
    assert r1b_info["total_cases"] == 8

    # Verify targets
    m3_train = {json.loads(l)["id"]: json.loads(l) for l in open(M3_TRAIN, encoding="utf-8") if l.strip()}
    for gid in expected_gids:
        c1 = m3_train[f"{gid}-c1"]
        c2 = m3_train[f"{gid}-c2"]
        assert c1["target"]["choice_id"] == "ship", f"{gid}-c1 expected target 'ship', got {c1['target']['choice_id']}"
        assert c2["target"]["choice_id"] == "delay", f"{gid}-c2 expected target 'delay', got {c2['target']['choice_id']}"


def test_m4_4_1_r1_and_r2_integrity():
    """Verify R1 (boundary) and R2 (composite logic) remain intact."""
    audit = json.load(open(AUDIT, encoding="utf-8"))
    assert audit["r1_equality_boundary"]["total_groups"] == 24
    assert audit["r1_equality_boundary"]["total_cases"] == 48

    r2_states = audit["r2_composite_logic"]["states"]
    for st_name in ["HP_True_item_False", "HP_True_item_True", "HP_False_item_True", "HP_False_item_False"]:
        assert r2_states[st_name]["selected_groups"] == 7
        assert r2_states[st_name]["selected_cases"] == 14
    assert audit["r2_composite_logic"]["total_groups"] == 28
    assert audit["r2_composite_logic"]["total_cases"] == 56


def test_m4_4_1_budget_caps():
    """Verify total replay cases <= 160 and total combined train <= 1240."""
    audit = json.load(open(AUDIT, encoding="utf-8"))
    assert audit["total_replay_cases"] == 112
    assert audit["total_replay_cases"] <= 160
    assert audit["is_under_cap"] is True

    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    assert manifest["total_records"] == 1192
    assert manifest["total_records"] <= 1240


def test_m4_4_1_manifest_and_hash():
    """Verify SHA-256 in manifest matches actual file."""
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    h = hashlib.sha256()
    with open(COMBINED_TRAIN, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    assert h.hexdigest() == manifest["combined_train_sha256"]
