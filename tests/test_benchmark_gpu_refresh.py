import json

import pytest

from scripts.benchmark_gpu_refresh import read_cases
from scripts.summarize_gpu_refresh import metrics


def test_public_gold_id_and_order_survive_normalization_and_limit(tmp_path):
    rows = [{"id": str(i), "suite": "intent", "gold_choice_id": "second",
             "choices": [{"id": "second", "text": "B"}, {"id": "first", "text": "A"}]} for i in range(3)]
    path = tmp_path / "cases.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    selected, sources = read_cases([path], 2)
    assert len(selected) == 2
    assert selected[0]["target"]["choice_id"] == "second"
    assert [c["id"] for c in selected[0]["choices"]] == ["second", "first"]
    assert selected[0]["domain"] == "public/intent"
    assert len(sources[0]["sha256"]) == 64
    rows[0]["gold_choice_id"] = "missing"
    path.write_text(json.dumps(rows[0]), encoding="utf-8")
    with pytest.raises(ValueError, match="hard target"):
        read_cases([path], None)


def test_summary_case_identity_is_order_independent_but_not_subset_independent():
    rows = [{"id": "one", "correct": True, "elapsed_ms": 10},
            {"id": "two", "correct": False, "elapsed_ms": 20}]
    result = metrics(rows)
    assert result["correct"] == 1 and result["accuracy"] == .5
    assert result["id_sha256"] == metrics(rows[::-1])["id_sha256"]
    assert result["id_sha256"] != metrics(rows[:1])["id_sha256"]


def test_seeded_public_subset_retains_entire_private_test(tmp_path):
    public = [{"id": f"p{i}", "suite": "intent", "gold_choice_id": "yes",
               "choices": [{"id": "yes", "text": "yes"}, {"id": "no", "text": "no"}]} for i in range(10)]
    private = [{"id": f"d{i}", "domain": "npc_goal", "target": {"kind": "hard", "choice_id": "yes"},
                "choices": public[0]["choices"]} for i in range(5)]
    path = tmp_path / "cases.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in public + private), encoding="utf-8")
    selected, _ = read_cases([path], None, 3, 42)
    assert len(selected) == 8
    assert sum(row["domain"].startswith("decision/") for row in selected) == 5
    assert [r["id"] for r in selected] == [r["id"] for r in read_cases([path], None, 3, 42)[0]]
