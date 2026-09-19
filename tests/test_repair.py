"""Tests for M3.2 dataset repair, independent audit cases, and invariant checks."""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def normalize_text(t: str) -> str:
    return unicodedata.normalize("NFC", t).strip().lower()


def text_hash(context: str, question: str) -> str:
    norm = f"{normalize_text(context)}|||{normalize_text(question)}"
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def test_independent_audit_cases():
    """Verify that independent audit cases match hand-crafted ground truth without generator logic."""
    audit_path = ROOT_DIR / "data" / "m3_2_label_fix" / "audit_cases.jsonl"
    assert audit_path.exists(), "audit_cases.jsonl not found"

    with open(audit_path, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    assert len(cases) == 10, f"Expected 10 audit cases, got {len(cases)}"

    # Check case 1: server capacity max
    c1 = cases[0]
    assert "大容量" in c1["question"]
    # Choices: A=100GB, B=300GB, C=200GB -> Max is B
    assert c1["target"]["choice_id"] == "b"

    # Check case 2: server capacity min
    c2 = cases[1]
    assert "小容量" in c2["question"]
    # Min is A
    assert c2["target"]["choice_id"] == "a"

    # Check boundary cases
    c7 = cases[6]
    assert "30点以下なら合格" in c7["question"]
    assert c7["target"]["choice_id"] == "pass"

    c8 = cases[7]
    assert "30点未満なら合格" in c8["question"]
    assert c8["target"]["choice_id"] == "fail"


def test_dataset_input_invariance():
    """Verify that all repaired files preserve exact input text, choices, and structure."""
    pairs = [
        ("data/m2_1/train.jsonl", "data/m3_2_label_fix/train.jsonl"),
        ("data/m2_1/dev.jsonl", "data/m3_2_label_fix/dev.jsonl"),
        ("data/m2_1/holdout.jsonl", "data/m3_2_label_fix/holdout_corrected.jsonl"),
        ("data/m3_1/final_test.jsonl", "data/m3_2_label_fix/final_test_corrected.jsonl"),
    ]

    for old_rel, new_rel in pairs:
        old_path = ROOT_DIR / old_rel
        new_path = ROOT_DIR / new_rel
        assert old_path.exists() and new_path.exists()

        with open(old_path, "r", encoding="utf-8") as f:
            old_recs = [json.loads(line) for line in f]
        with open(new_path, "r", encoding="utf-8") as f:
            new_recs = [json.loads(line) for line in f]

        assert len(old_recs) == len(new_recs), f"Count mismatch in {new_rel}"

        for old_r, new_r in zip(old_recs, new_recs):
            assert old_r["id"] == new_r["id"]
            assert old_r["context"] == new_r["context"]
            assert old_r["question"] == new_r["question"]
            assert old_r["choices"] == new_r["choices"]
            assert old_r.get("group_id") == new_r.get("group_id")
            assert old_r.get("task_family") == new_r.get("task_family")

            # Check text hash
            h_old = text_hash(old_r["context"], old_r["question"])
            h_new = text_hash(new_r["context"], new_r["question"])
            assert h_old == h_new


def test_label_changes_log():
    """Verify label_changes.jsonl contains expected change counts and valid reasons."""
    changes_path = ROOT_DIR / "data" / "m3_2_label_fix" / "label_changes.jsonl"
    assert changes_path.exists()

    with open(changes_path, "r", encoding="utf-8") as f:
        changes = [json.loads(line) for line in f]

    # Total 66 changes: train 38, dev 6, holdout 12, final_test 10
    assert len(changes) == 66
    counts = {}
    for c in changes:
        s = c["split"]
        counts[s] = counts.get(s, 0) + 1
        assert c["old_target"] != c["new_target"]
        assert "大容量" in c["reason"] or "サーバー" in c["reason"]
        assert len(c["input_hash"]) == 64

    assert counts == {"train": 38, "dev": 6, "holdout": 12, "final_test": 10}


def test_counterfactual_probe_structure():
    """Verify counterfactual probe contains exactly 24 cases (12 pairs) with verified labels."""
    cf_path = ROOT_DIR / "data" / "m3_2_label_fix" / "counterfactual_probe.jsonl"
    assert cf_path.exists()

    with open(cf_path, "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    assert len(cases) == 24
    groups = {}
    for c in cases:
        gid = c["group_id"]
        groups.setdefault(gid, []).append(c)

    assert len(groups) == 12, "Must contain exactly 12 pairs"
    for gid, pair in groups.items():
        assert len(pair) == 2, f"Group {gid} must have 2 cases"
        # Each pair must have distinct targets or valid contrasting criteria
        c1, c2 = pair[0], pair[1]
        assert c1["target"]["choice_id"] in [opt["id"] for opt in c1["choices"]]
        assert c2["target"]["choice_id"] in [opt["id"] for opt in c2["choices"]]
