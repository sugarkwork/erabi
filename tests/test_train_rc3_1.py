"""CPU-only contracts for the RC3.1 Run 1 driver."""

from __future__ import annotations

import copy
import random
from pathlib import Path

import pytest

from scripts.train_rc3_1 import (
    LOGIC_GATE,
    NEGATION_OPERATORS,
    RC3_GATE,
    RETENTION_GATE,
    deduplicate_group_replay,
    logic_gate_passed,
    prepare_mixture,
    rc3_gate_passed,
    retention_gate_passed,
    select_checkpoint_epoch,
    shuffle_choices,
    shuffle_groups,
    validate_output_path,
)


def _record(group_id: str, record_id: str, target: str = "a") -> dict:
    return {
        "id": record_id,
        "group_id": group_id,
        "context": "同じモデル可視コンテキスト",
        "question": "どちらを選ぶか",
        "choices": [
            {"id": "a", "text": "処理A"},
            {"id": "b", "text": "処理B"},
        ],
        "target": {"choice_id": target},
    }


def _passing_logic(accuracy: float = 0.95, paired: float = 0.90, nll: float = 0.20) -> dict:
    operators = {name: {"accuracy": 1.0, "total": 2} for name in ("xor", "nand", "nor")}
    operators.update({name: {"accuracy": 1.0, "total": 2} for name in NEGATION_OPERATORS})
    return {
        "accuracy": accuracy,
        "mean_nll": nll,
        "paired_both_rate": paired,
        "by_operator": operators,
        "negation": {"accuracy": 1.0, "total": 10},
        "nested": {"accuracy": 1.0, "total": 10},
    }


def _passing_rc3(accuracy: float = 0.90, paired: float = 0.90, permutation: float = 0.96) -> dict:
    families = {
        name: {"accuracy": 1.0, "total": 2}
        for name in (
            "logical_operators",
            "general_choice",
            "priority_exception",
            "variable_choice",
            "perturbation_invariance",
            "natural_japanese",
        )
    }
    return {
        "accuracy": accuracy,
        "paired_both_rate": paired,
        "permutation_consistency": permutation,
        "by_family": families,
    }


def _passing_epoch(
    *, logic_accuracy: float = 0.95, rc3_accuracy: float = 0.90,
    paired: float = 0.90, nll: float = 0.20, retention: float = 0.97,
) -> dict:
    return {
        "logic_bridge": _passing_logic(logic_accuracy, paired, nll),
        "existing_rc3_bridge": _passing_rc3(rc3_accuracy, paired),
        "retention": {"mean_accuracy": retention},
    }


def test_replay_dedup_keeps_one_complete_model_visible_pair() -> None:
    first = [_record("g1", "g1-a", "a"), _record("g1", "g1-b", "b")]
    duplicate = [
        {**_record("g2", "g2-a", "a"), "id": "other-a"},
        {**_record("g2", "g2-b", "b"), "id": "other-b"},
    ]
    unique = [_record("g3", "g3-a", "b"), _record("g3", "g3-b", "a")]

    result = deduplicate_group_replay(first + duplicate + unique)

    assert len(result) == 4
    assert [record["group_id"] for record in result] == ["g1", "g1", "g3", "g3"]
    assert {record["target"]["choice_id"] for record in result[:2]} == {"a", "b"}


def test_mixture_contract_has_expected_dedup_and_no_group_overlap() -> None:
    mixture = prepare_mixture()

    assert mixture["old_source_count"] == 8_650
    assert mixture["old_replay_groups"] == 1_383
    assert mixture["old_replay_count"] == 2_766
    assert mixture["new_train_count"] == 1_920
    assert mixture["new_train_groups"] == 960
    assert mixture["mixed_count"] == 4_686
    assert mixture["mixed_groups"] == 2_343


def test_group_and_choice_shuffle_are_seeded_and_preserve_targets() -> None:
    records = [_record("g1", "g1-a", "a"), _record("g1", "g1-b", "b")]
    records += [_record("g2", "g2-a", "a"), _record("g2", "g2-b", "b")]

    first = shuffle_groups(records, seed=17)
    second = shuffle_groups(records, seed=17)
    assert first == second
    assert [record["group_id"] for record in first] in (
        ["g1", "g1", "g2", "g2"],
        ["g2", "g2", "g1", "g1"],
    )

    shuffled = shuffle_choices(records[0], random.Random(19))
    assert {choice["id"] for choice in shuffled["choices"]} == {"a", "b"}
    assert shuffled["target"] == records[0]["target"]
    assert records[0]["choices"][0]["id"] == "a"


def test_gate_contracts_include_all_required_buckets() -> None:
    assert LOGIC_GATE == {
        "overall": 0.90,
        "xor": 0.85,
        "nand": 0.85,
        "nor": 0.85,
        "negation": 0.90,
        "nested": 0.85,
        "paired_both": 0.85,
    }
    assert RC3_GATE["overall"] == 0.88
    assert RC3_GATE["permutation"] == 0.95
    assert RETENTION_GATE == 0.96

    logic = _passing_logic()
    rc3 = _passing_rc3()
    retention = {"mean_accuracy": 0.96}
    assert logic_gate_passed(logic)
    assert rc3_gate_passed(rc3)
    assert retention_gate_passed(retention)

    logic["by_operator"]["xor"]["accuracy"] = 0.849999
    rc3["by_family"]["natural_japanese"]["accuracy"] = 0.899999
    retention["mean_accuracy"] = 0.959999
    assert not logic_gate_passed(logic)
    assert not rc3_gate_passed(rc3)
    assert not retention_gate_passed(retention)


def test_selection_filters_retention_then_uses_fixed_tiebreak_order() -> None:
    results = {
        1: _passing_epoch(retention=0.95),  # filtered first
        2: _passing_epoch(logic_accuracy=0.94, rc3_accuracy=0.99, nll=0.01),
        3: _passing_epoch(logic_accuracy=0.95, rc3_accuracy=0.89, nll=0.90),
        4: _passing_epoch(logic_accuracy=0.95, rc3_accuracy=0.90, paired=0.89, nll=0.50),
        5: _passing_epoch(logic_accuracy=0.95, rc3_accuracy=0.90, paired=0.90, nll=0.30),
        6: _passing_epoch(logic_accuracy=0.95, rc3_accuracy=0.90, paired=0.90, nll=0.10),
    }

    assert select_checkpoint_epoch(results) == 6
    assert select_checkpoint_epoch({1: _passing_epoch(retention=0.959)}) is None


def test_output_guard_rejects_existing_path(tmp_path: Path) -> None:
    existing = tmp_path / "existing-run"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        validate_output_path(existing)

    validate_output_path(tmp_path / "new-run")


def test_driver_does_not_reference_retired_benchmark_paths_or_strings() -> None:
    source = (Path(__file__).parents[1] / "scripts" / "train_rc3_1.py").read_text(encoding="utf-8").lower()
    assert "blind_v5" not in source
    assert "sealed_acceptance_rc3" not in source
