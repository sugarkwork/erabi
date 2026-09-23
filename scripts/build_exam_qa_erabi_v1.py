"""Curate the private Exam-QA corpus into ERABI choice records with DeepSeek.

The source and generated datasets stay local and are git-ignored.  The paid
path is deliberately resumable and fail-closed: every request is journaled
before sending, raw responses are saved before validation, and an unresolved
request is never retried automatically.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
import random
import re
import sys
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "exam-qa" / "data" / "exam_qa.jsonl"
OUTPUT = ROOT / "data" / "exam_qa_erabi_v1"
KEY_FILE = ROOT / ".env.orcarouter.local"
TOKENIZER_DIR = ROOT / "runs" / "practical_v1_finetune_20260922" / "checkpoint"
MODEL = "deepseek/deepseek-v4.1-flash"
PREVIOUS_ESTIMATED_USD = 1.1460837
GLOBAL_BUDGET_USD = 10.0
PROMPT_USD_PER_TOKEN = 0.30 / 1_000_000
COMPLETION_USD_PER_TOKEN = 1.20 / 1_000_000
MAX_COMPLETION_TOKENS_V1 = 1200
MAX_COMPLETION_TOKENS_V2 = 2400
MAX_COMPLETION_TOKENS_V3 = 4096
MAX_INPUT_TOKENS = 1024
PILOT_SEED = 20260923

SYSTEM_PROMPT_V1 = """You are DeepSeek acting as a conservative dataset curator for a local single-label choice classifier. You receive one official exam record, including its official answer. Return one JSON object only.

Decide whether the record can become a self-contained, unambiguous, single-correct-answer choice task. Never rewrite, summarize, translate, or add facts to the supplied question/context. Never expose reasoning. Skip records that require a missing image, chart, map, audio, external passage, subjective rubric, partial credit, multiple valid answers, or information not present in the record.

For a normal existing choice question whose official answer matches exactly one source choice label, do not generate or edit choices. Set generated_choices to []. The caller will map source labels to the exact source choice texts.

For a free-response, numeric, or ordering record, you may propose 2 to 6 candidate texts only when exactly one is defensibly correct from the official material. Exactly one item must have is_correct=true, and its text must be exactly the source field `answer` (same Unicode text after surrounding whitespace is stripped). Distractors must be plausible but unambiguously wrong; do not introduce an alternative correct spelling, rounding, unit, ordering, or interpretation. If that is not possible, skip.

Required schema:
{"source_id":"same id","decision":"use|skip","reason_code":"short_snake_case","reason":"brief factual reason","self_contained":true|false,"single_answer":true|false,"generated_choices":[{"text":"...","is_correct":true|false}]}
"""

SYSTEM_PROMPT_V2 = """You are DeepSeek acting as a conservative dataset curator for a local single-label choice classifier. You receive one official exam record and its official answer. Return one compact JSON object only; do not provide analysis outside JSON.

Decide whether the record is self-contained, unambiguous, and has exactly one defensible answer. Never rewrite, summarize, translate, or add facts to the supplied question. Skip missing-image/chart/map/audio/external-passage tasks, subjective rubrics, partial-credit tasks, multiple accepted answers, incomplete answer keys, and multi-blank records whose official answer does not answer every blank.

For a normal existing choice question whose answer matches exactly one source label, set generated_choices to [] and only judge usability. Do not edit its choices.

For free-response, numeric, or ordering records, propose 2 to 6 candidates only if exactly one can be correct. The one correct candidate text must exactly equal source `answer` after surrounding whitespace is stripped. Every distractor must be the same grammatical and semantic type as the correct answer (person vs person, event vs event, number-with-unit vs number-with-unit, full ordering vs full ordering), plausible, and unambiguously wrong under the supplied material. Do not use a synonymous answer, accepted rounding, equivalent unit, alternative spelling, or broader/narrower correct concept as a distractor. Otherwise skip.

Use this exact schema and keep reason under 30 words:
{"source_id":"same id","decision":"use|skip","reason_code":"short_snake_case","reason":"brief factual reason","self_contained":true|false,"single_answer":true|false,"generated_choices":[{"text":"...","is_correct":true|false}]}
"""

SYSTEM_PROMPT_V3 = SYSTEM_PROMPT_V2 + "\nDecide early. If any requirement is uncertain, return skip instead of spending tokens exploring alternatives."

PROMPTS = {"v1": SYSTEM_PROMPT_V1, "v2": SYSTEM_PROMPT_V2, "v3": SYSTEM_PROMPT_V3}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl_durable(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_key() -> str:
    if not KEY_FILE.is_file():
        raise FileNotFoundError(f"Missing ignored key file: {KEY_FILE}")
    lines = [line.strip() for line in KEY_FILE.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    values: list[str] = []
    for line in lines:
        name, separator, value = line.partition("=")
        if separator and name.strip() == "ORCAROUTER_API_KEY" and value.strip():
            values.append(value.strip())
    if len(values) != 1:
        raise ValueError("Expected exactly one nonempty ORCAROUTER_API_KEY in ignored key file")
    return values[0]


def is_sequence_record(row: dict[str, Any]) -> bool:
    answer = str(row.get("answer", ""))
    labels = {str(choice.get("label", "")).strip() for choice in (row.get("choices") or [])}
    return ("→" in answer or "->" in answer) or bool(labels and answer.strip() not in labels)


def is_english_record(row: dict[str, Any]) -> bool:
    exam = str(row.get("exam", "")).lower()
    if any(marker in exam for marker in ("sat", "act", "ap ")):
        return True
    text = str(row.get("question", ""))
    latin = sum(char.isascii() and char.isalpha() for char in text)
    return latin > max(30, len(text) * 0.55)


def pilot_bucket(row: dict[str, Any]) -> str:
    if len(str(row.get("question", ""))) >= 5000:
        return "long_or_rubric"
    if is_sequence_record(row):
        return "sequence"
    answer_type = row.get("answer_type")
    lang = "en" if is_english_record(row) else "ja"
    if answer_type == "choice":
        return f"choice_{lang}"
    if answer_type == "numeric":
        return f"numeric_{lang}"
    return f"text_{lang}"


def select_pilot(rows: list[dict[str, Any]], count: int, seed: int = PILOT_SEED) -> list[dict[str, Any]]:
    if count < 1 or count > len(rows):
        raise ValueError("pilot count must be between 1 and source size")
    rng = random.Random(seed)
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        buckets.setdefault(pilot_bucket(row), []).append(row)
    priority = ["choice_ja", "choice_en", "sequence", "numeric_ja", "numeric_en", "text_ja", "text_en", "long_or_rubric"]
    selected: list[dict[str, Any]] = []
    used: set[str] = set()
    for name in priority:
        candidates = buckets.get(name, [])
        if candidates and len(selected) < count:
            row = rng.choice(candidates)
            selected.append(row)
            used.add(row["id"])
    remaining = [row for row in rows if row["id"] not in used]
    rng.shuffle(remaining)
    selected.extend(remaining[: count - len(selected)])
    rng.shuffle(selected)
    return selected


def split_context(full_question: str, prompt: str) -> tuple[str, str]:
    full_question = full_question.strip()
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("empty_prompt")
    occurrences = full_question.count(prompt)
    if occurrences == 0:
        return full_question, prompt
    if occurrences > 1:
        raise ValueError("prompt_occurs_multiple_times")
    before, after = full_question.split(prompt, 1)
    context = (before.rstrip() + ("\n" if before.rstrip() and after.lstrip() else "") + after.lstrip()).strip()
    return context, prompt


def group_id(row: dict[str, Any]) -> str:
    material = "\x1f".join(str(row.get(key, "")).strip() for key in ("exam", "subject", "section"))
    return "examqa_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def normal_choice_mapping(row: dict[str, Any]) -> tuple[list[dict[str, str]], str] | None:
    source_choices = row.get("choices") or []
    answer = str(row.get("answer", "")).strip()
    matches = [index for index, choice in enumerate(source_choices) if str(choice.get("label", "")).strip() == answer]
    if row.get("answer_type") != "choice" or len(matches) != 1 or is_sequence_record(row):
        return None
    choices = []
    for index, source_choice in enumerate(source_choices):
        text = str(source_choice.get("text", "")).strip()
        if not text:
            raise ValueError("empty_source_choice")
        choices.append({"id": f"c{index + 1}", "text": text})
    return choices, choices[matches[0]]["id"]


def build_user_prompt(row: dict[str, Any], prompt_version: str) -> str:
    payload = {
        "id": row.get("id"),
        "exam": row.get("exam"),
        "subject": row.get("subject"),
        "section": row.get("section"),
        "question": row.get("question"),
        "prompt": row.get("prompt"),
        "answer": row.get("answer"),
        "answer_text": row.get("answer_text"),
        "answer_type": row.get("answer_type"),
        "choices": row.get("choices", []),
        "context_note": row.get("context_note"),
        "figure_dependent": row.get("figure_dependent"),
    }
    if prompt_version == "v1":
        payload["notes"] = row.get("notes")
    return "Curate this record:\n" + json.dumps(payload, ensure_ascii=False, sort_keys=True)


def prompt_hash(version: str) -> str:
    return sha256_text(version + "\n" + PROMPTS[version])


def max_completion_tokens(version: str) -> int:
    return {"v1": MAX_COMPLETION_TOKENS_V1, "v2": MAX_COMPLETION_TOKENS_V2, "v3": MAX_COMPLETION_TOKENS_V3}[version]


def conservative_reserve_usd(system_prompt: str, user_prompt: str, max_completion_tokens: int) -> tuple[int, float]:
    # UTF-8 bytes / 2 intentionally overestimates typical Japanese/English token counts.
    estimated_prompt_tokens = max(256, math.ceil(len((system_prompt + user_prompt).encode("utf-8")) / 2))
    reserve = estimated_prompt_tokens * PROMPT_USD_PER_TOKEN + max_completion_tokens * COMPLETION_USD_PER_TOKEN
    return estimated_prompt_tokens, reserve


def request_key(source_id: str, p_hash: str) -> str:
    return f"{source_id}:{p_hash}"


def journal_state(events: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}
    for event in events:
        key = event.get("request_key")
        if not key:
            continue
        item = state.setdefault(key, {"pending": None, "response": None, "ambiguous": None})
        kind = event.get("event")
        if kind in item:
            item[kind] = event
    return state


def committed_spend(events: Iterable[dict[str, Any]]) -> float:
    state = journal_state(events)
    total = PREVIOUS_ESTIMATED_USD
    for item in state.values():
        if item["response"] is not None:
            total += float(item["response"].get("estimated_usd", 0.0))
        elif item["pending"] is not None:
            total += float(item["pending"].get("reserve_usd", 0.0))
    return total


def validate_teacher_output(raw: Any, row: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("response_not_object")
    required = {"source_id", "decision", "reason_code", "reason", "self_contained", "single_answer", "generated_choices"}
    if not required.issubset(raw):
        raise ValueError("response_missing_fields")
    if raw["source_id"] != row["id"]:
        raise ValueError("source_id_mismatch")
    if raw["decision"] not in {"use", "skip"}:
        raise ValueError("invalid_decision")
    if not isinstance(raw["self_contained"], bool) or not isinstance(raw["single_answer"], bool):
        raise ValueError("invalid_boolean_fields")
    if not isinstance(raw["generated_choices"], list):
        raise ValueError("generated_choices_not_list")
    if raw["decision"] == "use" and (not raw["self_contained"] or not raw["single_answer"]):
        raise ValueError("use_without_contract")
    mapping = normal_choice_mapping(row)
    generated = raw["generated_choices"]
    if mapping is not None and generated:
        raise ValueError("normal_choice_was_rewritten")
    if raw["decision"] == "use" and mapping is None:
        if not 2 <= len(generated) <= 6:
            raise ValueError("generated_choice_count")
        if any(not isinstance(item, dict) or set(item) != {"text", "is_correct"} for item in generated):
            raise ValueError("generated_choice_schema")
        texts = [str(item["text"]).strip() for item in generated]
        if any(not text for text in texts) or len(set(texts)) != len(texts):
            raise ValueError("generated_choices_empty_or_duplicate")
        correct = [item for item in generated if item["is_correct"] is True]
        if len(correct) != 1 or any(not isinstance(item["is_correct"], bool) for item in generated):
            raise ValueError("generated_correct_count")
        if str(correct[0]["text"]).strip() != str(row.get("answer", "")).strip():
            raise ValueError("generated_correct_not_exact_official_answer")
    return raw


def make_erabi_record(row: dict[str, Any], teacher: dict[str, Any]) -> dict[str, Any]:
    if teacher["decision"] != "use":
        raise ValueError("teacher_skipped")
    context, question = split_context(str(row.get("question", "")), str(row.get("prompt", "")))
    mapping = normal_choice_mapping(row)
    if mapping is not None:
        choices, target_id = mapping
        transform_kind = "official_choices_label_to_text"
    else:
        choices = [{"id": f"c{index + 1}", "text": str(item["text"]).strip()} for index, item in enumerate(teacher["generated_choices"])]
        correct_index = next(index for index, item in enumerate(teacher["generated_choices"]) if item["is_correct"])
        target_id = choices[correct_index]["id"]
        transform_kind = "deepseek_distractors_official_target"
    record = {
        "id": "examqa_" + row["id"],
        "group_id": group_id(row),
        "task_family": "exam_qa",
        "domain": str(row.get("subject", "exam")),
        "language": "en" if is_english_record(row) else "ja",
        "context": context,
        "question": question,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": target_id},
        "source": {
            "dataset": "exam-qa-local",
            "source_id": row["id"],
            "exam": row.get("exam"),
            "subject": row.get("subject"),
            "source_url": row.get("source_url"),
        },
        "provenance": {
            "review_status": "deepseek_curated_unreviewed",
            "transform_kind": transform_kind,
            "teacher_model_requested": MODEL,
            "reason_code": teacher["reason_code"],
        },
    }
    validate_erabi_record(record)
    return record


def validate_erabi_record(record: dict[str, Any]) -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from erabi.schema import ChoiceRequest

    request = ChoiceRequest.from_dict(record)
    if not 2 <= len(request.choices) <= 16:
        raise ValueError("choice_count_out_of_range")
    ids = [choice.id for choice in request.choices]
    texts = [choice.text.strip() for choice in request.choices]
    if len(ids) != len(set(ids)) or len(texts) != len(set(texts)) or any(not text for text in texts):
        raise ValueError("duplicate_or_empty_choices")
    if record["target"]["choice_id"] not in ids:
        raise ValueError("target_missing")


class TokenCounter:
    def __init__(self, tokenizer_dir: Path = TOKENIZER_DIR):
        from transformers import AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_dir), local_files_only=True)

    @staticmethod
    def format_input(context: str, question: str, labels: list[str]) -> str:
        return question + context + "<<SEP>>" + "".join(label + "<<LABEL>>" for label in labels) + "<<SEP>>"

    def count(self, record: dict[str, Any]) -> int:
        labels = [choice["text"] for choice in record["choices"]]
        raw = self.format_input(record["context"], record["question"], labels)
        return len(self.tokenizer(raw, truncation=False)["input_ids"])

    def count_parts(self, context: str, question: str, labels: list[str]) -> int:
        raw = self.format_input(context, question, labels)
        return len(self.tokenizer(raw, truncation=False)["input_ids"])


def pre_api_skip(row: dict[str, Any], token_counter: Any) -> dict[str, Any] | None:
    if bool(row.get("figure_dependent")):
        return {"source_id": row["id"], "reason_code": "figure_dependent", "detail": "Source marks the item as figure-dependent"}
    try:
        context, question = split_context(str(row.get("question", "")), str(row.get("prompt", "")))
        mapping = normal_choice_mapping(row)
        if mapping is not None:
            labels = [choice["text"] for choice in mapping[0]]
        else:
            answer = str(row.get("answer", "")).strip()
            if not answer:
                return {"source_id": row["id"], "reason_code": "empty_official_answer"}
            labels = [answer, "__minimal_distractor__"]
        count = int(token_counter.count_parts(context, question, labels))
        if count > MAX_INPUT_TOKENS:
            return {"source_id": row["id"], "reason_code": "over_1024_tokens_pre_api", "input_tokens": count}
    except Exception as exc:
        return {"source_id": row["id"], "reason_code": "pre_api_validation_failed", "detail": f"{type(exc).__name__}: {str(exc)[:300]}"}
    return None


def choose_rows(rows: list[dict[str, Any]], mode: str, count: int, seed: int) -> list[dict[str, Any]]:
    if mode == "full":
        return list(rows)
    return select_pilot(rows, count=count, seed=seed)


def package_splits(
    records: list[dict[str, Any]],
    *,
    pilot_source_ids: set[str],
    valid_fraction: float = 0.20,
    seed: int = PILOT_SEED,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if not 0 < valid_fraction < 0.5:
        raise ValueError("valid_fraction must be between 0 and 0.5")
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(record["group_id"], []).append(record)
    pilot_groups = {
        record["group_id"]
        for record in records
        if record["source"]["source_id"] in pilot_source_ids
    }
    official_kind = "official_choices_label_to_text"
    official_by_language = Counter(
        record["language"]
        for record in records
        if record["provenance"]["transform_kind"] == official_kind
    )
    targets = {language: max(1, round(count * valid_fraction)) for language, count in official_by_language.items()}
    candidates = []
    for gid, items in grouped.items():
        official = [item for item in items if item["provenance"]["transform_kind"] == official_kind]
        if official and gid not in pilot_groups:
            score = hashlib.sha256(f"{seed}:{gid}".encode("utf-8")).hexdigest()
            candidates.append((score, gid, official))
    candidates.sort()
    valid_groups: set[str] = set()
    valid_counts: Counter[str] = Counter()
    for _, gid, official in candidates:
        if all(valid_counts[language] >= target for language, target in targets.items()):
            break
        contribution = Counter(item["language"] for item in official)
        if any(valid_counts[language] < targets[language] and contribution[language] for language in targets):
            valid_groups.add(gid)
            valid_counts.update(contribution)

    train: list[dict[str, Any]] = []
    valid: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    for record in records:
        copy = json.loads(json.dumps(record, ensure_ascii=False))
        if record["group_id"] in valid_groups:
            if record["provenance"]["transform_kind"] != official_kind:
                excluded.append({"source_id": record["source"]["source_id"], "group_id": record["group_id"], "reason_code": "synthetic_choices_in_valid_group"})
                continue
            copy["split"] = "valid"
            valid.append(copy)
        else:
            copy["split"] = "train"
            train.append(copy)
    train_groups = {record["group_id"] for record in train}
    valid_group_ids = {record["group_id"] for record in valid}
    if train_groups & valid_group_ids:
        raise AssertionError("train/valid group overlap")
    if any(record["provenance"]["transform_kind"] != official_kind for record in valid):
        raise AssertionError("validation contains synthetic distractors")
    manifest = {
        "seed": seed,
        "valid_fraction_target": valid_fraction,
        "counts": {"source_accepted": len(records), "train": len(train), "valid": len(valid), "excluded_from_splits": len(excluded)},
        "groups": {"all": len(grouped), "train": len(train_groups), "valid": len(valid_group_ids), "pilot_forced_train": len(pilot_groups)},
        "transform_kind": {
            "train": dict(sorted(Counter(record["provenance"]["transform_kind"] for record in train).items())),
            "valid": dict(sorted(Counter(record["provenance"]["transform_kind"] for record in valid).items())),
        },
        "language": {
            "train": dict(sorted(Counter(record["language"] for record in train).items())),
            "valid": dict(sorted(Counter(record["language"] for record in valid).items())),
        },
        "valid_group_ids": sorted(valid_group_ids),
        "policy": "Group-disjoint split; prompt-pilot groups forced to train; validation uses official source choices only; generated distractors are train-only.",
    }
    return train, valid, excluded, manifest


def write_packaged_splits(output_dir: Path, prompt_version: str) -> dict[str, Any]:
    results_path = output_dir / f"results_full_{prompt_version}.jsonl"
    pilot_path = output_dir / f"selection_pilot_{prompt_version}.json"
    records = read_jsonl(results_path)
    pilot_source_ids = {
        item["id"] for item in json.loads(pilot_path.read_text(encoding="utf-8"))["records"]
    }
    train, valid, excluded, manifest = package_splits(records, pilot_source_ids=pilot_source_ids)
    paths = {
        "train": output_dir / "train.jsonl",
        "valid": output_dir / "valid.jsonl",
        "excluded": output_dir / "split_excluded.jsonl",
    }
    for name, path in paths.items():
        values = {"train": train, "valid": valid, "excluded": excluded}[name]
        path.write_text("".join(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n" for value in values), encoding="utf-8")
    manifest["sha256"] = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
    manifest["prompt_version"] = prompt_version
    manifest["status"] = "private_unpublished_deepseek_curated_unreviewed"
    (output_dir / "split_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def call_teacher(client: Any, row: dict[str, Any], system_prompt: str, user_prompt: str, completion_limit: int) -> Any:
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=completion_limit,
    )


def process(
    rows: list[dict[str, Any]],
    *,
    mode: str,
    prompt_version: str,
    dry_run: bool,
    output_dir: Path,
    client_factory: Callable[[], Any] | None = None,
    token_counter: Any | None = None,
    seed: int = PILOT_SEED,
) -> dict[str, Any]:
    selected = choose_rows(rows, mode, len(rows) if mode == "full" else min(len(rows), 10), seed)
    selection_path = output_dir / f"selection_{mode}_{prompt_version}.json"
    journal_path = output_dir / "journal.jsonl"
    output_dir.mkdir(parents=True, exist_ok=True)
    selection_payload = {
        "mode": mode,
        "prompt_version": prompt_version,
        "seed": seed,
        "count": len(selected),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest() if SOURCE.is_file() else None,
        "records": [{"id": row["id"], "bucket": pilot_bucket(row)} for row in selected],
    }
    selection_path.write_text(json.dumps(selection_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if dry_run:
        return {"dry_run": True, "selection": selection_payload}

    p_hash = prompt_hash(prompt_version)
    system_prompt = PROMPTS[prompt_version]
    completion_limit = max_completion_tokens(prompt_version)
    events = read_jsonl(journal_path) if journal_path.is_file() else []
    state = journal_state(events)
    token_counter = token_counter or TokenCounter()
    client = (client_factory or _default_client_factory)()
    accepted: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for position, row in enumerate(selected, start=1):
        local_skip = pre_api_skip(row, token_counter)
        if local_skip is not None:
            skipped.append(local_skip)
            print(f"[{position}/{len(selected)}] {row['id']} pre-skip={local_skip['reason_code']}", flush=True)
            continue
        key = request_key(row["id"], p_hash)
        item = state.get(key, {})
        response_event = item.get("response")
        if response_event is None and item.get("pending") is not None:
            skipped.append({"source_id": row["id"], "reason_code": "unresolved_prior_request", "detail": "Not retried automatically"})
            print(f"[{position}/{len(selected)}] {row['id']} unresolved-prior-request", flush=True)
            continue
        if response_event is None:
            user_prompt = build_user_prompt(row, prompt_version)
            estimated_prompt_tokens, reserve = conservative_reserve_usd(system_prompt, user_prompt, completion_limit)
            if committed_spend(events) + reserve > GLOBAL_BUDGET_USD:
                raise RuntimeError("Global $10 estimated budget would be exceeded")
            pending = {
                "event": "pending",
                "timestamp": utc_now(),
                "attempt_id": str(uuid.uuid4()),
                "request_key": key,
                "source_id": row["id"],
                "source_input_sha256": sha256_text(canonical_json(row)),
                "prompt_version": prompt_version,
                "prompt_sha256": p_hash,
                "requested_model": MODEL,
                "estimated_prompt_tokens": estimated_prompt_tokens,
                "max_completion_tokens": completion_limit,
                "reserve_usd": reserve,
            }
            append_jsonl_durable(journal_path, pending)
            events.append(pending)
            try:
                response = call_teacher(client, row, system_prompt, user_prompt, completion_limit)
                usage = response.usage
                prompt_tokens = int(usage.prompt_tokens)
                completion_tokens = int(usage.completion_tokens)
                estimated_usd = prompt_tokens * PROMPT_USD_PER_TOKEN + completion_tokens * COMPLETION_USD_PER_TOKEN
                response_event = {
                    "event": "response",
                    "timestamp": utc_now(),
                    "attempt_id": pending["attempt_id"],
                    "request_key": key,
                    "source_id": row["id"],
                    "prompt_version": prompt_version,
                    "prompt_sha256": p_hash,
                    "requested_model": MODEL,
                    "response_model": response.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "estimated_usd": estimated_usd,
                    "raw_response": response.choices[0].message.content,
                }
                append_jsonl_durable(journal_path, response_event)
                events.append(response_event)
                print(f"[{position}/{len(selected)}] {row['id']} api finish={response_event['finish_reason']} cumulative=${committed_spend(events):.4f}", flush=True)
            except Exception as exc:
                ambiguous = {
                    "event": "ambiguous",
                    "timestamp": utc_now(),
                    "attempt_id": pending["attempt_id"],
                    "request_key": key,
                    "source_id": row["id"],
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:500],
                    "reserve_usd": reserve,
                    "note": "No automatic retry; billing state may be unknown",
                }
                append_jsonl_durable(journal_path, ambiguous)
                raise

        try:
            if response_event.get("finish_reason") != "stop":
                raise ValueError("finish_reason_not_stop")
            teacher = validate_teacher_output(json.loads(response_event["raw_response"]), row)
            if teacher["decision"] == "skip":
                skipped.append({"source_id": row["id"], "reason_code": teacher["reason_code"], "detail": teacher["reason"]})
                print(f"[{position}/{len(selected)}] {row['id']} teacher-skip={teacher['reason_code']}", flush=True)
                continue
            record = make_erabi_record(row, teacher)
            count = int(token_counter.count(record))
            if count > MAX_INPUT_TOKENS:
                skipped.append({"source_id": row["id"], "reason_code": "over_1024_tokens", "input_tokens": count})
                continue
            record["input_tokens"] = count
            accepted.append(record)
            print(f"[{position}/{len(selected)}] {row['id']} accepted tokens={count}", flush=True)
        except Exception as exc:
            skipped.append({"source_id": row["id"], "reason_code": "local_validation_failed", "detail": f"{type(exc).__name__}: {str(exc)[:300]}"})
            print(f"[{position}/{len(selected)}] {row['id']} validation-skip={type(exc).__name__}", flush=True)

    results_path = output_dir / f"results_{mode}_{prompt_version}.jsonl"
    skips_path = output_dir / f"skips_{mode}_{prompt_version}.jsonl"
    results_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in accepted), encoding="utf-8")
    skips_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in skipped), encoding="utf-8")
    manifest = {
        "mode": mode,
        "prompt_version": prompt_version,
        "prompt_sha256": p_hash,
        "selected": len(selected),
        "accepted": len(accepted),
        "skipped": len(skipped),
        "skip_reasons": dict(sorted(Counter(item["reason_code"] for item in skipped).items())),
        "estimated_cumulative_usd": committed_spend(events),
        "previous_estimated_usd": PREVIOUS_ESTIMATED_USD,
        "global_budget_usd": GLOBAL_BUDGET_USD,
        "results_sha256": hashlib.sha256(results_path.read_bytes()).hexdigest(),
        "skips_sha256": hashlib.sha256(skips_path.read_bytes()).hexdigest(),
        "status": "deepseek_curated_unreviewed_not_gold",
    }
    (output_dir / f"manifest_{mode}_{prompt_version}.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def _default_client_factory() -> Any:
    from openai import OpenAI

    return OpenAI(base_url="https://api.orcarouter.ai/v1", api_key=load_key(), timeout=120, max_retries=0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["pilot", "full"], default="pilot")
    parser.add_argument("--pilot-count", type=int, default=10)
    parser.add_argument("--prompt-version", default="v1")
    parser.add_argument("--seed", type=int, default=PILOT_SEED)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.prompt_version not in PROMPTS:
        raise ValueError(f"Unknown prompt version: {args.prompt_version}")
    if args.package_only:
        print(json.dumps(write_packaged_splits(args.output_dir, args.prompt_version), ensure_ascii=False, indent=2), flush=True)
        return
    rows = read_jsonl(SOURCE)
    if args.mode == "pilot":
        selected = select_pilot(rows, args.pilot_count, args.seed)
        # process() deliberately uses ten by default; preserve an explicit caller count.
        if args.pilot_count != 10:
            result = process_selected(selected, prompt_version=args.prompt_version, dry_run=args.dry_run, output_dir=args.output_dir, seed=args.seed)
        else:
            result = process(rows, mode="pilot", prompt_version=args.prompt_version, dry_run=args.dry_run, output_dir=args.output_dir, seed=args.seed)
    else:
        result = process(rows, mode="full", prompt_version=args.prompt_version, dry_run=args.dry_run, output_dir=args.output_dir, seed=args.seed)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


def process_selected(selected: list[dict[str, Any]], *, prompt_version: str, dry_run: bool, output_dir: Path, seed: int) -> dict[str, Any]:
    """Run a non-default-size pilot without changing the deterministic selector."""
    # `process` full mode preserves the supplied list exactly; filenames remain pilot.
    result = process(selected, mode="full", prompt_version=prompt_version, dry_run=dry_run, output_dir=output_dir, seed=seed)
    return result


if __name__ == "__main__":
    main()
