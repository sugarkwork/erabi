"""Unit tests for Milestone 7 Domain & Perturbation Robustness (ERABI)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from erabi.data.robustness.generator import ALL_DOMAINS, build_robustness_split
from erabi.data.robustness.validator import validate_robustness_dataset, rederive_robustness_choice_id

ROOT = Path(__file__).resolve().parent.parent


def test_robustness_domains_and_perturbations():
    assert len(ALL_DOMAINS) == 9
    assert "medical" in ALL_DOMAINS
    assert "finance" in ALL_DOMAINS
    assert "factory" in ALL_DOMAINS
    assert "smart_home" in ALL_DOMAINS


def test_robustness_generator_and_validator():
    for split in ["train", "dev", "fresh"]:
        records, _ = build_robustness_split(split, pairs_per_cell=1, seed=42)
        # 9 domains * 6 perturbations * 1 pair * 2 cases = 108 records
        assert len(records) == 108
        res = validate_robustness_dataset(records)
        assert res["validation_status"] == "ALL_PASSED"
        assert res["diff_target_pairs"] == 54
        assert res["diff_pair_rate"] == 1.0


def test_robustness_datasets_integrity():
    m7_dir = ROOT / "data/m7_robustness"
    assert (m7_dir / "fresh_robustness_eval.jsonl").exists()
    assert (m7_dir / "dev_robustness.jsonl").exists()
    assert (m7_dir / "train_robustness.jsonl").exists()

    fresh = [json.loads(l) for l in open(m7_dir / "fresh_robustness_eval.jsonl", encoding="utf-8") if l.strip()]
    dev = [json.loads(l) for l in open(m7_dir / "dev_robustness.jsonl", encoding="utf-8") if l.strip()]
    train = [json.loads(l) for l in open(m7_dir / "train_robustness.jsonl", encoding="utf-8") if l.strip()]

    assert len(fresh) == 108
    assert len(dev) == 108
    assert len(train) == 324

    def sig(r):
        return f"{r['context'].strip()} /// {r['question'].strip()} /// {'|'.join(c['text'] for c in r['choices'])}"

    train_sigs = {sig(r) for r in train}
    dev_sigs = {sig(r) for r in dev}
    fresh_sigs = {sig(r) for r in fresh}

    assert len(train_sigs & fresh_sigs) == 0, "Leak between train and fresh!"
    assert len(train_sigs & dev_sigs) == 0, "Leak between train and dev!"
    assert len(dev_sigs & fresh_sigs) == 0, "Leak between dev and fresh!"


def test_zero_leakage_against_all_eval_and_train():
    def get_sigs(path):
        sigs = set()
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                c = "|".join(x["text"] for x in r["choices"])
                sigs.add(f"{r['context'].strip()} /// {r['question'].strip()} /// {c}")
        return sigs

    eval_files = [
        ROOT / "data/eval_v2.jsonl",
        ROOT / "data/m3_composite/eval_exception.jsonl",
        ROOT / "data/m4_1_priority/transfer_probe.jsonl",
        ROOT / "data/m4_3_phrasing/fresh_phrasing_eval.jsonl",
        ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
        ROOT / "data/smoke_cases.jsonl",
        ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl",
    ]

    train_files = [
        ROOT / "data/train_v2.jsonl",
        ROOT / "data/m3_composite/train_composite.jsonl",
        ROOT / "data/m4_1_priority/train_priority.jsonl",
        ROOT / "data/m4_3_phrasing/train_phrasing.jsonl",
        ROOT / "data/m6_operator/train_operator.jsonl",
        ROOT / "data/m7_robustness/train_robustness.jsonl",
    ]

    all_train_sigs = set()
    for tf in train_files:
        if tf.exists():
            all_train_sigs.update(get_sigs(tf))

    for ef in eval_files:
        if ef.exists():
            esigs = get_sigs(ef)
            leak = esigs & all_train_sigs
            assert len(leak) == 0, f"LEAK FOUND in {ef.name}: {len(leak)} cases"
