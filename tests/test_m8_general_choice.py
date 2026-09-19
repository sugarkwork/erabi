"""Unit tests for Milestone 8 General Choice Tasks (ERABI)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from erabi.data.general_choice.generator import GENERAL_FAMILIES, build_general_split
from erabi.data.general_choice.validator import validate_general_dataset

ROOT = Path(__file__).resolve().parent.parent


def test_general_choice_families_count():
    assert len(GENERAL_FAMILIES) == 6
    assert "support_routing" in GENERAL_FAMILIES
    assert "short_nli" in GENERAL_FAMILIES
    assert "semantic_relation" in GENERAL_FAMILIES
    assert "intent_selection" in GENERAL_FAMILIES
    assert "instruction_separation" in GENERAL_FAMILIES
    assert "negative_goal" in GENERAL_FAMILIES


def test_general_generator_and_validator():
    for split in ["train", "dev", "fresh"]:
        records, _ = build_general_split(split, pairs_per_family=2, seed=42)
        assert len(records) == 24  # 6 families * 2 pairs * 2 cases = 24
        res = validate_general_dataset(records)
        assert res["validation_status"] == "ALL_PASSED"
        assert res["diff_target_pairs"] == 12
        assert res["diff_pair_rate"] == 1.0


def test_general_choice_datasets_integrity():
    m8_dir = ROOT / "data/m8_general_choice"
    assert (m8_dir / "fresh_general_eval.jsonl").exists()
    assert (m8_dir / "dev_general.jsonl").exists()
    assert (m8_dir / "train_general.jsonl").exists()

    fresh = [json.loads(l) for l in open(m8_dir / "fresh_general_eval.jsonl", encoding="utf-8") if l.strip()]
    dev = [json.loads(l) for l in open(m8_dir / "dev_general.jsonl", encoding="utf-8") if l.strip()]
    train = [json.loads(l) for l in open(m8_dir / "train_general.jsonl", encoding="utf-8") if l.strip()]

    assert len(fresh) == 120
    assert len(dev) == 60
    assert len(train) == 360

    def sig(r):
        return f"{r['context'].strip()} /// {r['question'].strip()} /// {'|'.join(c['text'] for c in r['choices'])}"

    train_sigs = {sig(r) for r in train}
    dev_sigs = {sig(r) for r in dev}
    fresh_sigs = {sig(r) for r in fresh}

    assert len(train_sigs & fresh_sigs) == 0, "Leak between train and fresh!"
    assert len(train_sigs & dev_sigs) == 0, "Leak between train and dev!"
    assert len(dev_sigs & fresh_sigs) == 0, "Leak between dev and fresh!"
