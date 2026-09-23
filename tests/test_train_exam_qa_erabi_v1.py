from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("train_examqa", ROOT / "scripts" / "train_exam_qa_erabi_v1.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_replay_selection_is_deterministic_and_does_not_mutate():
    records = [{"id": f"id-{i}", "group_id": f"g-{i}"} for i in range(20)]
    before = json.loads(json.dumps(records))
    one = MODULE.select_replay(records, 5, 7)
    two = MODULE.select_replay(records, 5, 7)
    assert [r["id"] for r in one] == [r["id"] for r in two]
    assert records == before


def test_selection_requires_improvement_and_bounded_retention():
    baseline = {"exam_valid": {"accuracy": 0.5}, "practical_dev": {"accuracy": 0.8}, "bridge": {"accuracy": 0.9}}
    assert MODULE.selection_pass(baseline, {"exam_valid": {"accuracy": 0.6}, "practical_dev": {"accuracy": 0.79}, "bridge": {"accuracy": 0.89}})
    assert not MODULE.selection_pass(baseline, {"exam_valid": {"accuracy": 0.5}, "practical_dev": {"accuracy": 0.8}, "bridge": {"accuracy": 0.9}})
    assert not MODULE.selection_pass(baseline, {"exam_valid": {"accuracy": 0.6}, "practical_dev": {"accuracy": 0.77}, "bridge": {"accuracy": 0.9}})
