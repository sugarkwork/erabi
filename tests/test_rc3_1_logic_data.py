"""Small CPU-only contracts for the RC3.1 logic-recovery data build."""

from __future__ import annotations

import copy
import hashlib
import json

from scripts.rc3_1_logic_data.audit import audit_balance, audit_historical_overlap, audit_split_isolation
from scripts.rc3_1_logic_data.generator import OPERATOR_FAMILIES, generate_bridge_records, generate_train_records
from scripts.rc3_1_logic_data.validator import derive_record, validate_records


def _stable_hash(records: list[dict]) -> str:
    payload = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in records)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def test_rc3_1_generator_shapes_and_split_counts() -> None:
    train = generate_train_records(seed=3102)
    bridge = generate_bridge_records(seed=3101)

    assert len(train) == 2_400
    assert len(bridge) == 480
    assert {item["split"] for item in train} == {"train", "dev", "calibration"}
    assert {split: sum(item["split"] == split for item in train) for split in ("train", "dev", "calibration")} == {
        "train": 1_920,
        "dev": 240,
        "calibration": 240,
    }
    assert {len(item["choices"]) for item in train + bridge} == {2, 3, 4, 6}
    assert {item["domain"] for item in train}.isdisjoint({item["domain"] for item in bridge})
    assert {item["mapping_style"] for item in bridge} == {"normal", "reordered", "implicit_fallback"}
    assert {item["condition_order"] for item in bridge} == {"ABC", "ACB", "BAC", "BCA", "CAB", "CBA"}


def test_rc3_1_independent_semantic_validation_and_balance() -> None:
    train = generate_train_records()
    bridge = generate_bridge_records()
    for records in (train, bridge):
        report = validate_records(records)
        assert report["is_valid"]
        assert report["semantic_mismatch_count"] == 0
        assert report["diff_target_pairs"] == len(records) // 2
        assert set(report["by_operator"]) == set(OPERATOR_FAMILIES)
        assert audit_balance(records, [derive_record(item) for item in records])["is_balanced"]

    train_splits = {
        split: [item for item in train if item["split"] == split]
        for split in ("train", "dev", "calibration")
    }
    assert audit_split_isolation(train_splits)["is_clean"]
    assert audit_split_isolation({"train": train, "bridge": bridge})["is_clean"]


def test_rc3_1_validator_does_not_trust_stored_target() -> None:
    record = copy.deepcopy(generate_bridge_records()[0])
    first_choice = record["choices"][0]["id"]
    expected = record["target"]["choice_id"]
    alternate = next(choice["id"] for choice in record["choices"] if choice["id"] != expected)
    record["target"]["choice_id"] = alternate
    report = validate_records([record])
    assert not report["is_valid"]
    assert report["semantic_mismatch_count"] == 1
    assert first_choice in {choice["id"] for choice in record["choices"]}


def test_rc3_1_generation_is_deterministic() -> None:
    assert _stable_hash(generate_train_records(seed=3102)) == _stable_hash(generate_train_records(seed=3102))
    assert _stable_hash(generate_bridge_records(seed=3101)) == _stable_hash(generate_bridge_records(seed=3101))
    assert _stable_hash(generate_bridge_records(seed=3101)) != _stable_hash(generate_bridge_records(seed=3102))


def test_rc3_1_validator_rejects_adversarial_renderings() -> None:
    record = copy.deepcopy(generate_bridge_records(seed=3101)[4])

    duplicate_condition = copy.deepcopy(record)
    duplicate_condition["context"] = duplicate_condition["context"][:-1] + "、条件A「重複信号」は成立。"
    assert not validate_records([duplicate_condition])["is_valid"]

    extra_question = copy.deepcopy(record)
    extra_question["question"] = extra_question["question"][:-1] + "余分な未解析文。"
    assert not validate_records([extra_question])["is_valid"]

    duplicate_expression = copy.deepcopy(record)
    duplicate_expression["question"] = duplicate_expression["question"][:-1] + "、式「A AND B」。"
    assert not validate_records([duplicate_expression])["is_valid"]

    duplicate_choice_text = copy.deepcopy(record)
    duplicate_choice_text["choices"][1]["text"] = duplicate_choice_text["choices"][0]["text"]
    assert not validate_records([duplicate_choice_text])["is_valid"]

    leaked_marker_choice = copy.deepcopy(record)
    leaked_marker_choice["choices"][0]["text"] = "expected_target"
    assert not validate_records([leaked_marker_choice])["is_valid"]


def test_rc3_1_fuzzy_historical_candidate_is_detected() -> None:
    historical = copy.deepcopy(generate_bridge_records(seed=3101)[0])
    candidate = copy.deepcopy(historical)
    historical["id"] = "historical-case"
    candidate["id"] = "new-case"
    candidate["context"] = candidate["context"].replace("Alpha", "Alphb", 1)
    report = audit_historical_overlap(
        [candidate],
        [historical],
        ["data/example.jsonl"],
        blind_v5_records=[],
        blind_v5_paths=[],
    )
    assert not report["is_clean"]
    assert report["fuzzy_near_copy_candidates"]
