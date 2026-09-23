from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_examqa", ROOT / "scripts" / "build_exam_qa_erabi_v1.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(**updates):
    base = {
        "id": "sample-1",
        "exam": "Sample Exam",
        "subject": "Science",
        "section": "Part A",
        "question": "Shared facts. Which gas?",
        "prompt": "Which gas?",
        "answer": "②",
        "answer_text": "carbon dioxide",
        "answer_type": "choice",
        "choices": [{"label": "①", "text": "oxygen"}, {"label": "②", "text": "carbon dioxide"}],
        "source_url": "https://example.invalid",
    }
    base.update(updates)
    return base


def teacher(**updates):
    base = {
        "source_id": "sample-1",
        "decision": "use",
        "reason_code": "usable",
        "reason": "Self-contained single answer.",
        "self_contained": True,
        "single_answer": True,
        "generated_choices": [],
    }
    base.update(updates)
    return base


def test_label_is_mapped_to_exact_choice_text():
    choices, target = MODULE.normal_choice_mapping(row())
    assert [item["text"] for item in choices] == ["oxygen", "carbon dioxide"]
    assert target == "c2"


def test_context_split_handles_zero_one_and_multiple_occurrences():
    assert MODULE.split_context("Facts only", "Question?") == ("Facts only", "Question?")
    assert MODULE.split_context("Facts. Question?", "Question?") == ("Facts.", "Question?")
    with pytest.raises(ValueError, match="multiple"):
        MODULE.split_context("Question? Facts. Question?", "Question?")


def test_sequence_detection_does_not_treat_atomic_choices_as_target():
    source = row(answer="ウ → イ → ア → エ", choices=[{"label": x, "text": x} for x in "アイウエ"])
    assert MODULE.is_sequence_record(source)
    assert MODULE.normal_choice_mapping(source) is None


def test_null_choices_are_treated_as_no_choices():
    source = row(answer_type="text", answer="応仁の乱", choices=None)
    assert not MODULE.is_sequence_record(source)
    assert MODULE.normal_choice_mapping(source) is None


def test_generated_target_must_equal_official_answer_exactly():
    source = row(answer_type="numeric", answer="2.778 acres", choices=[])
    valid = teacher(generated_choices=[{"text": "2.778 acres", "is_correct": True}, {"text": "2.877 acres", "is_correct": False}])
    MODULE.validate_teacher_output(valid, source)
    invalid = teacher(generated_choices=[{"text": "about 2.78 acres", "is_correct": True}, {"text": "2.877 acres", "is_correct": False}])
    with pytest.raises(ValueError, match="exact_official"):
        MODULE.validate_teacher_output(invalid, source)


def test_normal_choices_may_not_be_rewritten():
    with pytest.raises(ValueError, match="rewritten"):
        MODULE.validate_teacher_output(teacher(generated_choices=[{"text": "oxygen", "is_correct": False}, {"text": "carbon dioxide", "is_correct": True}]), row())


def test_group_id_keeps_same_exam_subject_section_together():
    first = row(id="a", question="one")
    second = row(id="b", question="two")
    assert MODULE.group_id(first) == MODULE.group_id(second)
    assert MODULE.group_id(first) != MODULE.group_id(row(section="Part B"))


class FixedCounter:
    def __init__(self, value):
        self.value = value

    def count(self, _record):
        return self.value

    def count_parts(self, context, question, labels):
        return 10


def test_token_over_limit_is_skipped(tmp_path, monkeypatch):
    source = row()
    p_hash = MODULE.prompt_hash("v1")
    raw = json.dumps(teacher(), ensure_ascii=False)
    event = {
        "event": "response",
        "request_key": MODULE.request_key(source["id"], p_hash),
        "source_id": source["id"],
        "finish_reason": "stop",
        "estimated_usd": 0.0,
        "raw_response": raw,
    }
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "journal.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    monkeypatch.setattr(MODULE, "SOURCE", tmp_path / "missing.jsonl")
    result = MODULE.process([source], mode="full", prompt_version="v1", dry_run=False, output_dir=tmp_path, client_factory=lambda: object(), token_counter=FixedCounter(1025))
    assert result["accepted"] == 0
    assert result["skip_reasons"] == {"over_1024_tokens": 1}


def test_pending_request_is_not_retried(tmp_path, monkeypatch):
    source = row()
    p_hash = MODULE.prompt_hash("v1")
    event = {"event": "pending", "request_key": MODULE.request_key(source["id"], p_hash), "source_id": source["id"], "reserve_usd": 0.01}
    (tmp_path / "journal.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    monkeypatch.setattr(MODULE, "SOURCE", tmp_path / "missing.jsonl")
    result = MODULE.process([source], mode="full", prompt_version="v1", dry_run=False, output_dir=tmp_path, client_factory=lambda: object(), token_counter=FixedCounter(10))
    assert result["skip_reasons"] == {"unresolved_prior_request": 1}


def test_reserve_and_committed_spend_are_conservative():
    estimated_tokens, reserve = MODULE.conservative_reserve_usd("日本語" * 100, "x" * 100, MODULE.MAX_COMPLETION_TOKENS_V2)
    assert estimated_tokens >= 256
    assert reserve > MODULE.MAX_COMPLETION_TOKENS_V2 * MODULE.COMPLETION_USD_PER_TOKEN
    events = [{"event": "pending", "request_key": "a", "reserve_usd": 0.2}]
    assert MODULE.committed_spend(events) == pytest.approx(MODULE.PREVIOUS_ESTIMATED_USD + 0.2)


def test_pilot_selection_is_deterministic_and_unique():
    rows = [row(id=f"id-{index}", answer_type="numeric" if index % 3 == 0 else "choice", answer="1" if index % 3 == 0 else "②", choices=[] if index % 3 == 0 else row()["choices"]) for index in range(20)]
    first = MODULE.select_pilot(rows, 10, seed=7)
    second = MODULE.select_pilot(rows, 10, seed=7)
    assert [item["id"] for item in first] == [item["id"] for item in second]
    assert len({item["id"] for item in first}) == 10


def test_pre_api_over_limit_skips_without_teacher_call():
    class PartsCounter:
        def count_parts(self, context, question, labels):
            return 1025

    skipped = MODULE.pre_api_skip(row(), PartsCounter())
    assert skipped["reason_code"] == "over_1024_tokens_pre_api"


def test_package_splits_are_group_disjoint_and_validation_is_official_only():
    records = []
    for index in range(12):
        source = row(id=f"id-{index}", section=f"section-{index // 2}")
        record = MODULE.make_erabi_record(source, teacher(source_id=source["id"]))
        record["input_tokens"] = 20
        records.append(record)
    generated_source = row(id="generated", section="generated-section", answer_type="numeric", answer="7", choices=[])
    generated_teacher = teacher(source_id="generated", generated_choices=[{"text": "7", "is_correct": True}, {"text": "8", "is_correct": False}])
    generated = MODULE.make_erabi_record(generated_source, generated_teacher)
    generated["input_tokens"] = 20
    records.append(generated)
    train, valid, excluded, manifest = MODULE.package_splits(records, pilot_source_ids={"id-0"}, valid_fraction=0.2, seed=3)
    assert {r["group_id"] for r in train}.isdisjoint({r["group_id"] for r in valid})
    assert all(r["provenance"]["transform_kind"] == "official_choices_label_to_text" for r in valid)
    assert any(r["source"]["source_id"] == "id-0" for r in train)
    assert manifest["counts"]["train"] + manifest["counts"]["valid"] + len(excluded) == len(records)
