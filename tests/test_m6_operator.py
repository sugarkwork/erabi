"""Unit tests for Milestone 6 Operator Generalization (ERABI)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from erabi.data.operators.generator import build_split, OPERATOR_FAMILIES
from erabi.data.operators.validator import validate_operator_dataset, rederive_expected_choice_id

ROOT = Path(__file__).resolve().parent.parent


def test_operator_families_count():
    assert len(OPERATOR_FAMILIES) == 10
    assert "ge_vs_gt" in OPERATOR_FAMILIES
    assert "le_vs_lt" in OPERATOR_FAMILIES
    assert "and_logic" in OPERATOR_FAMILIES
    assert "or_logic" in OPERATOR_FAMILIES
    assert "negation" in OPERATOR_FAMILIES
    assert "override" in OPERATOR_FAMILIES


def test_operator_generator_and_validator():
    # Generate 1 pair per operator across train, dev, fresh
    for split in ["train", "dev", "fresh"]:
        records, _ = build_split(split, pairs_per_op=1, seed=42)
        assert len(records) == 20  # 10 families * 1 pair * 2 cases = 20
        res = validate_operator_dataset(records)
        assert res["validation_status"] == "ALL_PASSED"
        assert res["diff_target_pairs"] == 10
        assert res["diff_pair_rate"] == 1.0


def test_operator_datasets_integrity():
    m6_dir = ROOT / "data/m6_operator"
    assert (m6_dir / "fresh_operator_eval.jsonl").exists()
    assert (m6_dir / "dev_operator.jsonl").exists()
    assert (m6_dir / "train_operator.jsonl").exists()

    fresh = [json.loads(l) for l in open(m6_dir / "fresh_operator_eval.jsonl", encoding="utf-8") if l.strip()]
    dev = [json.loads(l) for l in open(m6_dir / "dev_operator.jsonl", encoding="utf-8") if l.strip()]
    train = [json.loads(l) for l in open(m6_dir / "train_operator.jsonl", encoding="utf-8") if l.strip()]

    assert len(fresh) == 100
    assert len(dev) == 60
    assert len(train) == 400

    def sig(r):
        return f"{r['context']} /// {r['question']} /// {'|'.join(c['text'] for c in r['choices'])}"

    train_sigs = {sig(r) for r in train}
    dev_sigs = {sig(r) for r in dev}
    fresh_sigs = {sig(r) for r in fresh}

    assert len(train_sigs & fresh_sigs) == 0, "Leak between train and fresh!"
    assert len(train_sigs & dev_sigs) == 0, "Leak between train and dev!"
    assert len(dev_sigs & fresh_sigs) == 0, "Leak between dev and fresh!"
