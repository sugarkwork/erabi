import pytest
from collections import Counter

from scripts.build_exam_qa_weakness_v1 import TARGET_COUNTS, journal_cost, specs, validate_generated


def generated(spec):
    return {
        "id": spec["id"],
        "context": "架空の実験では、条件Aの値が10、条件Bの値が15だった。追加条件では差が5だった。",
        "question": "記述された結果から最も適切に導ける結論はどれですか。",
        "choices": [{"id": f"c{i}", "text": f"結論{i}"} for i in range(1, spec["choice_count"] + 1)],
        "correct_choice_id": "c1",
        "answer_explanation": "本文の値と差に一致するため。",
    }


def test_specs_are_deterministic_balanced_and_complete():
    first = specs(7)
    assert first == specs(7)
    assert len(first) == sum(TARGET_COUNTS.values()) == 600
    assert {row["choice_count"] for row in first} == {4, 6, 8}
    assert {row["length_tier"] for row in first} == {"short", "medium", "long"}
    assert len({row["id"] for row in first}) == 600
    for choice_count in (4, 6, 8):
        positions = Counter(row["target_choice_id"] for row in first if row["choice_count"] == choice_count)
        assert set(positions) == {f"c{i}" for i in range(1, choice_count + 1)}
        assert max(positions.values()) - min(positions.values()) <= 1


def test_generated_validation_enforces_shape_and_target():
    spec = next(row for row in specs(7) if row["language"] == "ja")
    row = validate_generated(generated(spec), spec, set())
    assert row["target"]["choice_id"] == spec["target_choice_id"]
    broken = generated(spec)
    broken["correct_choice_id"] = "c99"
    with pytest.raises(ValueError, match="correct_choice_id"):
        validate_generated(broken, spec, set())


def test_generated_validation_normalizes_string_choices():
    spec = next(row for row in specs(7) if row["language"] == "ja")
    raw = generated(spec)
    raw["choices"] = [choice["text"] for choice in raw["choices"]]
    row = validate_generated(raw, spec, set())
    assert [choice["id"] for choice in row["choices"]] == [
        f"c{i}" for i in range(1, spec["choice_count"] + 1)
    ]
    target = next(choice for choice in row["choices"] if choice["id"] == spec["target_choice_id"])
    assert target["text"] == "結論1"


def test_journal_cost_reserves_only_unresolved_requests():
    journal = [
        {"event": "pending", "batch_key": "done", "reserve_usd": 0.5},
        {"event": "response", "batch_key": "done", "estimated_usd": 0.2},
        {"event": "pending", "batch_key": "unknown", "reserve_usd": 0.7},
    ]
    spent, reserved, responses, unresolved = journal_cost(journal)
    assert spent == pytest.approx(0.2)
    assert reserved == pytest.approx(0.7)
    assert responses == {"done"}
    assert unresolved == {"unknown"}
