"""Offline checks for practical synthetic-data generation invariants."""

import pytest

from scripts.build_practical_v1 import _choices, _language_ok, _spec, _validate


def test_arithmetic_choices_match_programmatic_answer():
    spec = _spec("everyday_arithmetic", "train", 8)
    choices, target = _choices("everyday_arithmetic", "ja", spec, {})
    answer = {"add": spec["a"] + spec["b"], "subtract": spec["a"] - spec["b"], "multiply": spec["a"] * spec["b"]}[spec["operation"]]
    assert len({choice["text"] for choice in choices}) == 4
    assert next(choice["text"] for choice in choices if choice["id"] == target) == str(answer)


def test_arithmetic_rejects_wrong_numbers():
    spec = _spec("everyday_arithmetic", "dev", 0)
    generated = {"context": f"There are {spec['a']} tickets and {spec['b'] + 1} guests.", "question": "How many?"}
    with pytest.raises(ValueError, match="numbers do not match"):
        _validate("everyday_arithmetic", "en", spec, generated, set())


def test_json_log_requires_messages():
    spec = _spec("json_log_routing", "train", 0)
    with pytest.raises(ValueError, match="invalid JSON conversation log"):
        _validate("json_log_routing", "en", spec, {"context": "{}", "question": "Which tool?"}, set())


def test_language_guard_rejects_english_only_japanese_example():
    assert not _language_ok("ja", "The answer is in the passage. Which one?")
    assert _language_ok("ja", "本文に答えがあります。どれですか？")
    assert _language_ok("zh-Hans", "根据短文，选择正确答案。")
