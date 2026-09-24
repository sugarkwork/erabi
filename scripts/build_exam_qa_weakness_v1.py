"""Generate private original training candidates for observed ERABI weaknesses.

Only aggregate weakness descriptions and synthetic generation specifications are
sent to DeepSeek. No source exam question or private evaluation text is sent.
Generation and answer-blind judging are journaled for safe resume.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "exam_qa_weakness_v1"
KEY_FILE = ROOT / ".env.orcarouter.local"
TOKENIZER_DIR = ROOT / "runs" / "exam_qa_erabi_v1_finetune_20260923" / "checkpoint"
MODEL = "deepseek/deepseek-v4.1-flash"
PREVIOUS_ESTIMATED_USD = 1.5851154
GLOBAL_CAP_USD = 10.0
PROMPT_USD_PER_TOKEN = 0.30 / 1_000_000
COMPLETION_USD_PER_TOKEN = 1.20 / 1_000_000
TARGET_COUNTS = {
    ("quantitative_multistep", "ja"): 60,
    ("quantitative_multistep", "en"): 60,
    ("chemistry_evidence", "ja"): 60,
    ("chemistry_evidence", "en"): 60,
    ("science_data_reasoning", "ja"): 50,
    ("science_data_reasoning", "en"): 50,
    ("reading_evidence", "ja"): 80,
    ("reading_evidence", "en"): 80,
    ("history_source_inference", "ja"): 50,
    ("history_source_inference", "en"): 50,
}
SUBSKILLS = {
    "quantitative_multistep": ("ratio and rate", "percent change", "two constraints", "probability", "table calculation"),
    "chemistry_evidence": ("controlled experiment", "reaction quantities", "concentration trend", "particle-model evidence", "measurement error"),
    "science_data_reasoning": ("control variables", "graph trend in prose", "competing hypotheses", "causal evidence", "multi-stage process"),
    "reading_evidence": ("main claim", "best textual evidence", "implicit inference", "sentence function", "logical transition"),
    "history_source_inference": ("compare two fictional sources", "chronology", "cause and consequence", "claim and evidence", "institutional change"),
}
LENGTH_GUIDANCE = {
    "short": "Aim for 120-250 model input tokens.",
    "medium": "Aim for 300-500 model input tokens and require combining at least two separated facts.",
    "long": "Aim for 550-850 model input tokens and require combining at least three separated facts; remain below 900 tokens.",
}
SYSTEM_GENERATE = """Return JSON only with an examples array. Create entirely original fictional assessment items for a local choice-ranking model. Never copy or paraphrase a real examination, benchmark, article, textbook passage, named historical document, or private conversation. Do not mention real exam brands, universities, copyrighted characters, real people, current events, URLs, or citations. Every item must be fully self-contained, have exactly one defensible answer, and rely only on supplied context. Use plausible distractors caused by specific reasoning mistakes, not absurd options. Do not reveal the correct answer in the question. Follow every supplied id, language, choice_count, length tier, category, and subskill exactly. First solve the item yourself, then independently re-solve it from scratch and verify the arithmetic, evidence chain, and uniqueness of the answer before reporting its natural correct_choice_id. Do not move or rewrite an answer merely to occupy a requested position. Output each object as {id, context, question, choices, correct_choice_id, answer_explanation}; choices must use ids c1..cN in order. Keep answer_explanation concise, grounded in the context, and do not refer to the answer by its letter or choice id."""
SYSTEM_JUDGE = """Act as an answer-blind quality judge. Return JSON only with a judgments array in the supplied order. For each original fictional item, independently solve it from context and choices without seeing any proposed answer. Output {id, valid, selected_choice_id, issue}. valid is true only when the item is self-contained, unambiguous, has exactly one correct choice, contains no missing figure or outside-knowledge dependency, and the selected choice follows from the context. Never rewrite the item."""


def load_key() -> str:
    values = []
    for line in KEY_FILE.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.strip().partition("=")
        if separator and name == "ORCAROUTER_API_KEY" and value:
            values.append(value)
    if len(values) != 1:
        raise ValueError("Expected one ORCAROUTER_API_KEY in ignored local file")
    return values[0]


def specs(seed: int = 20260924) -> list[dict[str, Any]]:
    rows = []
    serial = 0
    target_counters = Counter()
    for (category, language), count in TARGET_COUNTS.items():
        for index in range(count):
            choice_count = (4, 6, 8)[index % 3]
            target_number = target_counters[choice_count] % choice_count + 1
            target_counters[choice_count] += 1
            length_tier = ("short", "medium", "long")[index % 3]
            rows.append({
                "id": f"weakv1_{serial:04d}",
                "category": category,
                "language": language,
                "choice_count": choice_count,
                "target_choice_id": f"c{target_number}",
                "length_tier": length_tier,
                "subskill": SUBSKILLS[category][index % len(SUBSKILLS[category])],
            })
            serial += 1
    random.Random(seed).shuffle(rows)
    return rows


def generation_prompt(batch: list[dict[str, Any]]) -> str:
    guidance = {
        "quantitative_multistep": "Use invented everyday quantities. Require at least two operations and state every needed assumption. Check all arithmetic exactly.",
        "chemistry_evidence": "Use a fictional experiment or measurements. All chemical facts needed to answer must be explicitly stated; test evidence reasoning rather than memorized facts.",
        "science_data_reasoning": "Use a fictional experiment, observations, or a data table expressed in text. Ask about variables, evidence, causality, or competing explanations.",
        "reading_evidence": "Use an original prose passage. Ask for inference, evidence, structure, or transition; avoid trivia and mere word matching.",
        "history_source_inference": "Use fictional societies, policies, and source excerpts. Test chronology or source reasoning without requiring real historical knowledge.",
    }
    decorated = []
    for spec in batch:
        item = dict(spec)
        item.pop("target_choice_id")
        item["length_instruction"] = LENGTH_GUIDANCE[spec["length_tier"]]
        item["category_instruction"] = guidance[spec["category"]]
        decorated.append(item)
    return "Observed weak skills: multi-step quantitative reasoning, science/chemistry evidence, reading inference, longer evidence integration, and 4/6/8-choice discrimination. Generate these exact specifications: " + json.dumps(decorated, ensure_ascii=False)


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def language_ok(language: str, text: str) -> bool:
    has_kana = bool(re.search(r"[\u3040-\u30ff]", text))
    has_han = bool(re.search(r"[\u3400-\u9fff]", text))
    return has_kana if language == "ja" else not has_kana and not has_han


def validate_generated(raw: dict[str, Any], spec: dict[str, Any], seen: set[str]) -> dict[str, Any]:
    if raw.get("id") != spec["id"]:
        raise ValueError("id_mismatch")
    context = raw.get("context")
    question = raw.get("question")
    explanation = raw.get("answer_explanation")
    choices = raw.get("choices")
    if not all(isinstance(value, str) and value.strip() for value in (context, question, explanation)):
        raise ValueError("missing_text")
    if not isinstance(choices, list) or len(choices) != spec["choice_count"]:
        raise ValueError("choice_count")
    expected_ids = [f"c{index}" for index in range(1, spec["choice_count"] + 1)]
    if all(isinstance(choice, str) for choice in choices):
        choices = [{"id": choice_id, "text": text} for choice_id, text in zip(expected_ids, choices)]
    if not all(isinstance(choice, dict) for choice in choices):
        raise ValueError("choice_shape")
    if [choice.get("id") for choice in choices] != expected_ids:
        raise ValueError("choice_ids")
    texts = [choice.get("text") for choice in choices]
    if not all(isinstance(text, str) and text.strip() for text in texts) or len({normalize(text) for text in texts}) != len(texts):
        raise ValueError("choice_text")
    correct_choice_id = raw.get("correct_choice_id")
    if correct_choice_id not in expected_ids:
        raise ValueError("correct_choice_id")
    correct_index = expected_ids.index(correct_choice_id)
    target_index = expected_ids.index(spec["target_choice_id"])
    choices[correct_index]["text"], choices[target_index]["text"] = (
        choices[target_index]["text"], choices[correct_index]["text"]
    )
    full_text = context + " " + question + " " + " ".join(texts)
    if not language_ok(spec["language"], full_text):
        raise ValueError("language")
    forbidden = re.compile(r"\b(?:SAT|ACT)\b|東京大学|京都大学|共通テスト|College Board|https?://", re.IGNORECASE)
    if forbidden.search(full_text):
        raise ValueError("forbidden_reference")
    signature = hashlib.sha256((normalize(context) + "\n" + normalize(question)).encode()).hexdigest()
    if signature in seen:
        raise ValueError("duplicate")
    seen.add(signature)
    return {
        "schema_version": "1",
        "id": spec["id"],
        "group_id": spec["id"],
        "context": context.strip(),
        "question": question.strip(),
        "choices": [{"id": choice["id"], "text": choice["text"].strip()} for choice in choices],
        "target": {"kind": "hard", "choice_id": spec["target_choice_id"]},
        "language": spec["language"],
        "task_family": "exam_qa_weakness",
        "domain": spec["category"],
        "split": "train",
        "review_status": "deepseek_generated_unreviewed",
        "generation_spec": spec,
        "answer_explanation": explanation.strip(),
        "source_model": MODEL,
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.exists() else []


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def journal_cost(journal: list[dict[str, Any]]) -> tuple[float, float, set[str], set[str]]:
    responses = {row["batch_key"] for row in journal if row.get("event") == "response"}
    pending = {row["batch_key"]: row for row in journal if row.get("event") == "pending"}
    spent = sum(float(row.get("estimated_usd", 0)) for row in journal if row.get("event") == "response")
    unresolved = set(pending) - responses
    reserved = sum(float(pending[key].get("reserve_usd", 0)) for key in unresolved)
    return spent, reserved, responses, unresolved


def recover_generation_responses(
    journal: list[dict[str, Any]], candidate_path: Path, seed: int
) -> tuple[list[dict[str, Any]], Counter]:
    candidates = read_jsonl(candidate_path)
    existing = {row["id"] for row in candidates}
    seen = {
        hashlib.sha256((normalize(row["context"]) + "\n" + normalize(row["question"])).encode()).hexdigest()
        for row in candidates
    }
    spec_by_id = {row["id"]: row for row in specs(seed)}
    rejected = Counter()
    for event in journal:
        if event.get("event") != "response":
            continue
        examples = event.get("raw_response", {}).get("examples")
        if not isinstance(examples, list):
            rejected["batch_shape"] += len(event.get("ids", []))
            continue
        for raw in examples:
            if not isinstance(raw, dict) or raw.get("id") not in spec_by_id:
                rejected["unknown_item"] += 1
                continue
            if raw["id"] in existing:
                continue
            try:
                row = validate_generated(raw, spec_by_id[raw["id"]], seen)
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                rejected[str(exc)] += 1
                continue
            append_jsonl(candidate_path, row)
            candidates.append(row)
            existing.add(row["id"])
    return candidates, rejected


def call(client, system: str, prompt: str, max_tokens: int) -> tuple[dict[str, Any], dict[str, Any]]:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=max_tokens,
        extra_body={"thinking": {"type": "disabled"}},
    )
    usage = response.usage
    if not usage:
        raise RuntimeError("missing_usage")
    cost = usage.prompt_tokens * PROMPT_USD_PER_TOKEN + usage.completion_tokens * COMPLETION_USD_PER_TOKEN
    meta = {
        "response_model": response.model,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "estimated_usd": cost,
        "finish_reason": response.choices[0].finish_reason,
    }
    content = response.choices[0].message.content or "{}"
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        meta["parse_error"] = f"{exc.msg} at {exc.lineno}:{exc.colno}"
        payload = {"invalid_json_content": content}
    return payload, meta


def generate(output: Path, limit: int, batch_size: int, additional_budget: float, seed: int) -> None:
    from openai import OpenAI

    output.mkdir(parents=True, exist_ok=True)
    journal_path = output / "generation_journal.jsonl"
    candidate_path = output / "candidates.jsonl"
    journal = read_jsonl(journal_path)
    spent, unresolved_reserve, completed, unresolved = journal_cost(journal)
    if PREVIOUS_ESTIMATED_USD + spent + unresolved_reserve >= GLOBAL_CAP_USD:
        raise RuntimeError("global_budget_exhausted")
    candidates, recovered_rejections = recover_generation_responses(journal, candidate_path, seed)
    existing = {row["id"] for row in candidates}
    attempted_ids = {
        item_id
        for row in journal
        if row.get("event") == "pending"
        for item_id in row.get("ids", [])
    }
    seen = {hashlib.sha256((normalize(row["context"]) + "\n" + normalize(row["question"])).encode()).hexdigest() for row in candidates}
    selected = specs(seed)[:limit]
    client = OpenAI(base_url="https://api.orcarouter.ai/v1", api_key=load_key(), timeout=180, max_retries=0)
    rejected = Counter(recovered_rejections)
    for start in range(0, len(selected), batch_size):
        batch = selected[start:start + batch_size]
        pending = [spec for spec in batch if spec["id"] not in existing and spec["id"] not in attempted_ids]
        if not pending:
            continue
        batch_key = hashlib.sha256(json.dumps(pending, sort_keys=True).encode()).hexdigest()[:16]
        if batch_key in completed:
            rejected["response_journaled_but_no_candidates"] += len(pending)
            continue
        if batch_key in unresolved:
            rejected["request_outcome_unknown_not_retried"] += len(pending)
            continue
        prompt = generation_prompt(pending)
        reserve = (len(prompt) + len(SYSTEM_GENERATE)) * PROMPT_USD_PER_TOKEN + 7500 * COMPLETION_USD_PER_TOKEN
        if spent + unresolved_reserve + reserve > additional_budget or PREVIOUS_ESTIMATED_USD + spent + unresolved_reserve + reserve > GLOBAL_CAP_USD:
            print(f"BUDGET_STOP spent={spent:.4f} additional_cap={additional_budget:.2f}")
            break
        append_jsonl(journal_path, {"event": "pending", "batch_key": batch_key, "ids": [row["id"] for row in pending], "reserve_usd": reserve})
        payload, meta = call(client, SYSTEM_GENERATE, prompt, 7500)
        append_jsonl(journal_path, {"event": "response", "batch_key": batch_key, "ids": [row["id"] for row in pending], **meta, "raw_response": payload})
        spent += meta["estimated_usd"]
        generated = payload.get("examples")
        if not isinstance(generated, list) or len(generated) != len(pending):
            rejected["batch_shape"] += len(pending)
            continue
        for spec, raw in zip(pending, generated):
            try:
                row = validate_generated(raw, spec, seen)
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                rejected[str(exc)] += 1
                continue
            append_jsonl(candidate_path, row)
            existing.add(row["id"])
        print(f"generate {min(start + len(batch), len(selected))}/{len(selected)} accepted={len(existing)} spent=${spent:.4f}", flush=True)
    manifest = {
        "mode": "generation",
        "requested": len(selected),
        "accepted": len(existing),
        "rejected": dict(rejected),
        "estimated_new_usd": round(spent, 8),
        "estimated_unresolved_reserve_usd": round(unresolved_reserve, 8),
        "estimated_cumulative_usd": round(PREVIOUS_ESTIMATED_USD + spent + unresolved_reserve, 8),
        "model": MODEL,
        "status": "private_unpublished_unreviewed",
    }
    (output / "generation_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def judge(output: Path, batch_size: int, additional_budget: float) -> None:
    from openai import OpenAI

    candidates = read_jsonl(output / "candidates.jsonl")
    journal_path = output / "judge_journal.jsonl"
    judgments_path = output / "judgments.jsonl"
    journal = read_jsonl(journal_path)
    spent_before, generation_unresolved, _, _ = journal_cost(read_jsonl(output / "generation_journal.jsonl"))
    spent, judge_unresolved, completed, unresolved = journal_cost(journal)
    judged = {row["id"] for row in read_jsonl(judgments_path)}
    client = OpenAI(base_url="https://api.orcarouter.ai/v1", api_key=load_key(), timeout=180, max_retries=0)
    for start in range(0, len(candidates), batch_size):
        batch = [row for row in candidates[start:start + batch_size] if row["id"] not in judged]
        if not batch:
            continue
        blind = [{key: row[key] for key in ("id", "context", "question", "choices")} for row in batch]
        prompt = "Independently solve and audit these items: " + json.dumps(blind, ensure_ascii=False)
        reserve = (len(prompt) + len(SYSTEM_JUDGE)) * PROMPT_USD_PER_TOKEN + 2500 * COMPLETION_USD_PER_TOKEN
        committed = spent_before + generation_unresolved + spent + judge_unresolved
        if committed + reserve > additional_budget or PREVIOUS_ESTIMATED_USD + committed + reserve > GLOBAL_CAP_USD:
            print(f"BUDGET_STOP judge_spent={spent:.4f}")
            break
        batch_key = hashlib.sha256(json.dumps([row["id"] for row in batch]).encode()).hexdigest()[:16]
        if batch_key in completed:
            continue
        if batch_key in unresolved:
            continue
        append_jsonl(journal_path, {"event": "pending", "batch_key": batch_key, "ids": [row["id"] for row in batch], "reserve_usd": reserve})
        payload, meta = call(client, SYSTEM_JUDGE, prompt, 2500)
        append_jsonl(journal_path, {"event": "response", "batch_key": batch_key, "ids": [row["id"] for row in batch], **meta, "raw_response": payload})
        spent += meta["estimated_usd"]
        values = payload.get("judgments")
        if not isinstance(values, list) or len(values) != len(batch):
            continue
        for source, value in zip(batch, values):
            if value.get("id") != source["id"]:
                continue
            append_jsonl(judgments_path, {
                "id": source["id"],
                "valid": value.get("valid") is True,
                "selected_choice_id": value.get("selected_choice_id"),
                "issue": str(value.get("issue", ""))[:300],
                "agrees": value.get("valid") is True and value.get("selected_choice_id") == source["target"]["choice_id"],
            })
            judged.add(source["id"])
        print(f"judge {min(start + batch_size, len(candidates))}/{len(candidates)} judged={len(judged)} spent=${spent:.4f}", flush=True)
    manifest = {
        "mode": "answer_blind_judge",
        "candidates": len(candidates),
        "judged": len(judged),
        "estimated_generation_usd": round(spent_before, 8),
        "estimated_judge_usd": round(spent, 8),
        "estimated_unresolved_reserve_usd": round(generation_unresolved + judge_unresolved, 8),
        "estimated_cumulative_usd": round(
            PREVIOUS_ESTIMATED_USD + spent_before + generation_unresolved + spent + judge_unresolved, 8
        ),
        "model": MODEL,
    }
    (output / "judge_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


def package(output: Path) -> None:
    from build_exam_qa_erabi_v1 import TokenCounter

    candidates = {row["id"]: row for row in read_jsonl(output / "candidates.jsonl")}
    judgments = {row["id"]: row for row in read_jsonl(output / "judgments.jsonl")}
    counter = TokenCounter(TOKENIZER_DIR)
    accepted = []
    rejected = Counter()
    for item_id, row in candidates.items():
        judgment = judgments.get(item_id)
        if not judgment or not judgment["agrees"]:
            rejected["judge_disagreed_or_invalid"] += 1
            continue
        tokens = counter.count_parts(row["context"], row["question"], [choice["text"] for choice in row["choices"]])
        tier = row["generation_spec"]["length_tier"]
        lower = {"short": 50, "medium": 180, "long": 350}[tier]
        if tokens < lower or tokens > 1024:
            rejected[f"token_range_{tier}"] += 1
            continue
        copy = dict(row)
        copy.pop("answer_explanation", None)
        copy["input_tokens"] = tokens
        copy["review_status"] = "deepseek_generated_and_answer_blind_agreed_unreviewed"
        accepted.append(copy)
    accepted.sort(key=lambda row: row["id"])
    train_path = output / "train.jsonl"
    train_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in accepted), encoding="utf-8")
    manifest = {
        "generated_candidates": len(candidates),
        "answer_blind_judged": len(judgments),
        "answer_blind_valid": sum(1 for row in judgments.values() if row["valid"]),
        "answer_blind_agreed": sum(1 for row in judgments.values() if row["agrees"]),
        "accepted": len(accepted),
        "rejected": dict(rejected),
        "categories": dict(sorted(Counter(row["domain"] for row in accepted).items())),
        "languages": dict(sorted(Counter(row["language"] for row in accepted).items())),
        "choice_counts": dict(sorted(Counter(str(len(row["choices"])) for row in accepted).items())),
        "length_tiers": dict(sorted(Counter(row["generation_spec"]["length_tier"] for row in accepted).items())),
        "target_positions": {
            str(choice_count): dict(sorted(Counter(
                row["target"]["choice_id"] for row in accepted if len(row["choices"]) == choice_count
            ).items()))
            for choice_count in (4, 6, 8)
        },
        "token_min": min((row["input_tokens"] for row in accepted), default=None),
        "token_max": max((row["input_tokens"] for row in accepted), default=None),
        "sha256": hashlib.sha256(train_path.read_bytes()).hexdigest(),
        "status": "private_unpublished_deepseek_same_model_agreement_not_human_gold",
        "human_reviewed": 0,
        "intended_use": "private training candidates pending human review",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "judge", "package"))
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--limit", type=int, default=600)
    parser.add_argument("--batch-size", type=int, default=6)
    parser.add_argument("--additional-budget", type=float, default=1.5)
    parser.add_argument("--seed", type=int, default=20260924)
    args = parser.parse_args()
    if not 1 <= args.limit <= 600 or not 1 <= args.batch_size <= 8:
        raise ValueError("invalid limit or batch size")
    if not 0 < args.additional_budget <= GLOBAL_CAP_USD - PREVIOUS_ESTIMATED_USD:
        raise ValueError("additional budget exceeds global cap")
    if args.mode == "generate":
        generate(args.output_dir, args.limit, args.batch_size, args.additional_budget, args.seed)
    elif args.mode == "judge":
        judge(args.output_dir, args.batch_size, args.additional_budget)
    else:
        package(args.output_dir)


if __name__ == "__main__":
    main()
