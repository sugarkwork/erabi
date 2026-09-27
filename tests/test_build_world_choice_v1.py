import copy
import json
import asyncio
from collections import Counter

import pytest

from scripts.build_world_choice_v1 import BudgetClient, BudgetExhausted, group_specs, item_specs, validate


class CounterStub:
    def __init__(self, tokens=100):
        self.tokens = tokens

    def count(self, row):
        return self.tokens


def test_group_plan_is_disjoint_balanced_and_reproducible():
    groups = group_specs()
    assert groups == group_specs()
    assert len({g["group_id"] for g in groups}) == 500
    assert Counter(g["split"] for g in groups) == {"train": 350, "dev": 75, "calibration": 25, "final_test": 50}
    assert Counter(g["language"] for g in groups) == {"ja": 300, "en": 100, "zh-Hans": 100}
    assert set(Counter(g["category"] for g in groups).values()) == {50}
    assert not {g["group_id"] for g in groups} & {g["group_id"] for g in group_specs(True)}


def test_permutation_preserves_answer_and_rejects_overlong_input():
    # Wiring fixture only; this is never sent to the teacher or used as training data.
    group = next(g for g in group_specs() if g["language"] == "en" and g["category"] == "color_shape")
    spec = item_specs(group, 0, 1)[0]
    raw = {"id": spec["id"], "context": "A fixture.", "question": "Which fixture?", "answer_explanation": "Test fixture only.",
           "choices": [{"id": f"c{i+1}", "text": f"fixture-{i}"} for i in range(spec["choice_count"])], "correct_choice_id": "c1"}
    row = validate(copy.deepcopy(raw), spec, CounterStub())
    assert next(c["text"] for c in row["choices"] if c["id"] == row["target"]["choice_id"]) == "fixture-0"
    with pytest.raises(ValueError, match="token_range"):
        validate(copy.deepcopy(raw), spec, CounterStub(1025))
    raw["correct_choice_id"] = "c99"
    with pytest.raises(ValueError, match="invalid_target"):
        validate(raw, spec, CounterStub())


def test_conversation_cannot_silently_be_plain_prose():
    group = next(g for g in group_specs() if g["category"] == "tool_routing" and g["language"] == "en")
    spec = item_specs(group, 0, 1)[0]
    raw = {"id": spec["id"], "context": "Plain text without messages", "question": "Choose a fixture.",
           "answer_explanation": "Fixture.", "choices": [{"id": f"c{i+1}", "text": f"fixture-{i}"} for i in range(spec["choice_count"])], "correct_choice_id": "c1"}
    with pytest.raises(ValueError):
        validate(raw, spec, CounterStub())
    raw["context"] = {"messages": [{"role": role, "content": "Fixture."} for role in ("user", "assistant", "user")]}
    original = copy.deepcopy(raw)
    result = validate(raw, spec, CounterStub())
    assert json.loads(result["context"]) == original["context"]
    assert raw == original  # Permutation must not mutate cached teacher responses.


def test_exhausted_budget_blocks_before_any_network_request():
    client = object.__new__(BudgetClient)
    client.responses, client.pending = {}, set()
    client.spent, client.reserved, client.active, client.cap = 8, 0, 0, 10
    with pytest.raises(BudgetExhausted):
        asyncio.run(client.call("generate", ["fixture"], "system", "prompt", 100))
