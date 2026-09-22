"""Build original multilingual choice data with DeepSeek via OrcaRouter.

Only generated, non-private prompts are sent.  The script records token usage,
uses conservative peak-hour pricing for the spend guard, and never logs the key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

from erabi.schema import ChoiceRequest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "practical_v1"
KEY_FILE = ROOT / ".env.orcarouter.local"
MODEL = "deepseek/deepseek-v4.1-flash"
LANGUAGES = {"ja": "Japanese", "en": "English", "zh-Hans": "Simplified Chinese"}
CATEGORIES = (
    "everyday_arithmetic",
    "tool_routing",
    "dialogue_action",
    "json_log_routing",
    "reading_inference",
    "original_exam_style",
)
SPLITS = ("train", "dev", "eval_candidate")
SPLIT_TOPICS = {
    "train": ("shopping", "commuting", "school clubs", "cooking", "home repairs", "bookkeeping"),
    "dev": ("library services", "museum visits", "sports practice", "community events"),
    "eval_candidate": ("gardening", "travel planning", "public transport", "volunteer work"),
}
TOOL_IDS = ("no_tool", "web_search", "calculator", "weather", "calendar", "file_search")
ACTION_IDS = ("answer_directly", "ask_clarification", "request_permission", "call_tool", "refuse_unsafe")
TOOL_TEXT = {
    "ja": ("ツールを使わず回答する", "Web検索する", "計算ツールを使う", "天気ツールを使う", "カレンダーを確認する", "提供済みファイルを検索する"),
    "en": ("Answer without a tool", "Search the web", "Use a calculator", "Use a weather tool", "Check the calendar", "Search the provided files"),
    "zh-Hans": ("无需工具直接回答", "搜索网页", "使用计算器", "使用天气工具", "查看日历", "搜索已提供的文件"),
}
ACTION_TEXT = {
    "ja": ("そのまま回答する", "不足情報を質問する", "実行前に許可を求める", "適切なツールを使う", "危険な依頼を断る"),
    "en": ("Answer directly", "Ask for missing information", "Request permission before acting", "Use an appropriate tool", "Refuse an unsafe request"),
    "zh-Hans": ("直接回答", "询问缺失信息", "执行前征求许可", "使用合适的工具", "拒绝不安全的请求"),
}
SYSTEM = (
    "Return a JSON object with an 'examples' array, in exactly the requested order. "
    "Create entirely original fictional data for a local choice-ranking model. "
    "Do not copy actual entrance examinations, benchmarks, articles, private chats, real people, or copyrighted passages. "
    "Do not use secrets, real account details, or personally identifying information. "
    "Keep each context plus question under 600 characters; use only the requested language. "
    "Each example must have one unambiguously correct target from information in the context. "
    "Avoid jokes, answer-revealing choice text, stereotypes, and trick wording. "
    "For each requested spec output exactly {context, question}; for reading_inference and original_exam_style also output choices "
    "as four objects {id,text} with ids c1,c2,c3,c4 and target_choice_id. "
    "Output JSON only, with no markdown or explanation."
)


def _spec(category: str, split: str, index: int) -> dict:
    topic = SPLIT_TOPICS[split][index % len(SPLIT_TOPICS[split])]
    base = {"index": index, "topic": topic}
    if category in {"tool_routing", "json_log_routing"}:
        base["target"] = TOOL_IDS[index % len(TOOL_IDS)]
        base["requirement"] = {
            "no_tool": "a non-numeric fact is explicitly stated in the conversation; answer by quoting or restating it, with no calculation or live lookup",
            "web_search": "needs current information not already supplied",
            "calculator": "needs a nontrivial exact calculation from supplied numbers",
            "weather": "asks for a current or future weather forecast at a stated place",
            "calendar": "asks about an existing calendar entry not present in the conversation",
            "file_search": "asks for a fact inside a provided local file whose contents are not in the conversation",
        }[base["target"]]
    elif category == "dialogue_action":
        base["target"] = ACTION_IDS[index % len(ACTION_IDS)]
        base["requirement"] = {
            "answer_directly": "all needed facts are explicitly quoted in the visible context; no lookup or calculation is needed",
            "ask_clarification": "one essential detail is missing from the visible context and cannot be looked up with any available tool; ask, do not guess",
            "request_permission": "the user mentions a possible external side effect but explicitly says it must not be performed without their later approval; the next step is to ask permission",
            "call_tool": "a read-only live or private lookup is required, and the user explicitly authorizes that lookup; its answer is absent from the visible context",
            "refuse_unsafe": "the request is clearly unsafe; no tool execution",
        }[base["target"]]
    elif category == "everyday_arithmetic":
        split_index = index + {"train": 0, "dev": 1000, "eval_candidate": 2000}[split]
        a = 7 + ((split_index * 13) % 61)
        b = 2 + ((split_index * 7) % 19)
        operation = ("add", "subtract", "multiply")[split_index % 3]
        if operation == "subtract" and a <= b:
            a += 30
        base.update({"a": a, "b": b, "operation": operation})
    else:
        base["difficulty"] = ("easy", "medium", "hard")[index % 3]
        base["theme"] = ("time ordering", "comparison", "causal inference", "explicit exception")[index % 4]
    return base


def _prompt(category: str, language: str, split: str, specs: list[dict]) -> str:
    directions = {
        "everyday_arithmetic": "Write natural everyday word problems using exactly the specified a and b (Arabic numerals) and operation. Do not add other numbers, dates, discounts or unstated assumptions. The question must request the single arithmetic result; omit choices because they are computed separately.",
        "tool_routing": "Write a realistic user request or short exchange uniquely requiring the specified target action. The question asks which action/tool to choose; omit choices. For no_tool, use a plainly stated non-numeric fact, never arithmetic. Do not claim an unavailable tool was already used.",
        "dialogue_action": "Write a realistic short exchange uniquely requiring the specified next action. The question asks what the assistant should do next; omit choices. Keep all needed facts visible, never merely say the assistant has already seen an unseen document. For request_permission, the user has NOT approved the side effect yet; for call_tool, the user HAS approved a read-only lookup.",
        "json_log_routing": "Write context as a compact valid JSON string with a messages array containing role/content objects. It must uniquely require the specified target tool action. For no_tool, use a plainly stated non-numeric fact, never arithmetic. The question asks which action/tool to choose; omit choices. No real names or identifiers.",
        "reading_inference": "Write a short original paragraph, a question answerable only from that paragraph, four plausible distinct choices and one correct choice id. Do not rely on outside facts. Never make two choices defensible.",
        "original_exam_style": "Write an original exam-style multiple-choice question, not a paraphrase of a real exam. Use a small self-contained passage, data table in prose, or rules so the answer is derivable without outside knowledge. For medium and hard specifications require at least two reasoning steps; do not ask for a fact copied verbatim from the passage. State every needed assumption explicitly. Four plausible distinct choices and one correct choice id.",
    }[category]
    return (
        f"Generate {len(specs)} {category} examples in {LANGUAGES[language]}. "
        f"Domain pool for this split: {', '.join(SPLIT_TOPICS[split])}. "
        + directions
        + " Keep contexts varied in setting and phrasing; avoid repetitive templates. "
        + "Use these exact specifications in order: "
        + json.dumps(specs, ensure_ascii=False)
        + " Return JSON {\"examples\":[...]}."
    )


def _choices(category: str, language: str, spec: dict, generated: dict) -> tuple[list[dict], str]:
    if category in {"tool_routing", "json_log_routing"}:
        return [dict(id=i, text=t) for i, t in zip(TOOL_IDS, TOOL_TEXT[language])], spec["target"]
    if category == "dialogue_action":
        return [dict(id=i, text=t) for i, t in zip(ACTION_IDS, ACTION_TEXT[language])], spec["target"]
    if category == "everyday_arithmetic":
        a, b = spec["a"], spec["b"]
        correct = {"add": a + b, "subtract": a - b, "multiply": a * b}[spec["operation"]]
        alternatives = [correct + 1, correct - 1, correct + b]
        if len(set([correct, *alternatives])) != 4 or min(alternatives) < 0:
            alternatives = [correct + 1, correct + 2, correct + 3]
        values = [correct, *alternatives]
        random.Random(7900 + spec["index"]).shuffle(values)
        choices = [dict(id=f"c{i+1}", text=str(value)) for i, value in enumerate(values)]
        return choices, next(choice["id"] for choice in choices if choice["text"] == str(correct))
    return generated["choices"], generated["target_choice_id"]


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _language_ok(language: str, text: str) -> bool:
    has_han = bool(re.search(r"[\u3400-\u9fff]", text))
    has_kana = bool(re.search(r"[\u3040-\u30ff]", text))
    if language == "ja":
        return has_kana
    if language == "zh-Hans":
        return has_han and not has_kana
    return not has_han and not has_kana


def _validate(category: str, language: str, spec: dict, generated: dict, seen: set[str]) -> dict:
    context = generated["context"].strip()
    question = generated["question"].strip()
    if not context or not question or len(context) + len(question) > 600:
        raise ValueError("empty or overlong context/question")
    if not _language_ok(language, context + " " + question):
        raise ValueError("language mismatch")
    if category == "json_log_routing":
        log = json.loads(context)
        if not isinstance(log, dict) or not isinstance(log.get("messages"), list) or not log["messages"]:
            raise ValueError("invalid JSON conversation log")
        if any(not isinstance(m, dict) or m.get("role") not in {"user", "assistant", "tool"} or not isinstance(m.get("content"), str) for m in log["messages"]):
            raise ValueError("invalid JSON message")
    if category == "everyday_arithmetic":
        nums = set(re.findall(r"\d+", context + " " + question))
        if str(spec["a"]) not in nums or str(spec["b"]) not in nums or nums - {str(spec["a"]), str(spec["b"])}:
            raise ValueError(f"arithmetic numbers do not match spec: {sorted(nums)}")
    choices, target = _choices(category, language, spec, generated)
    if not isinstance(choices, list) or not 2 <= len(choices) <= 16:
        raise ValueError("invalid choice count")
    if target not in {choice["id"] for choice in choices}:
        raise ValueError("target not in choices")
    if len({_normalize(choice["text"]) for choice in choices}) != len(choices):
        raise ValueError("duplicate choice text")
    ChoiceRequest.from_dict({"context": context, "question": question, "choices": choices})
    signature = hashlib.sha256((_normalize(context) + "\n" + _normalize(question)).encode()).hexdigest()
    if signature in seen:
        raise ValueError("duplicate context/question")
    seen.add(signature)
    return {
        "context": context,
        "question": question,
        "choices": choices,
        "target": {"kind": "hard", "choice_id": target},
        "language": language,
        "family": category,
        "domain": spec["topic"],
        "source_model": MODEL,
        "source_type": "original_synthetic",
        "review_status": "teacher_proposed_unreviewed",
        "generation_spec": spec,
    }


def _load_key() -> str:
    line = KEY_FILE.read_text(encoding="utf-8").strip()
    name, sep, value = line.partition("=")
    if name != "ORCAROUTER_API_KEY" or not sep or not value:
        raise ValueError("Missing ORCAROUTER_API_KEY in local ignored key file")
    return value


def _read_json(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _save_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def repair_holdout_arithmetic() -> None:
    """Archive and remove only the holdout math made with repeated operand specs."""
    source = OUTPUT / "all.jsonl"
    if not source.exists():
        raise FileNotFoundError(source)
    backup = ROOT / "runs" / "practical_v1_holdout_math_before_repair.jsonl"
    if backup.exists():
        raise FileExistsError(backup)
    backup.parent.mkdir(parents=True, exist_ok=True)
    original = source.read_text(encoding="utf-8")
    backup.write_text(original, encoding="utf-8")
    kept = []
    removed = 0
    for line in original.splitlines():
        record = json.loads(line)
        if record["family"] == "everyday_arithmetic" and record["split"] != "train":
            removed += 1
        else:
            kept.append(line)
    source.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"Archived full corpus to {backup}; removed {removed} holdout arithmetic records for regeneration")


def generate(
    batch_size: int,
    train_batches: int,
    holdout_batches: int,
    budget_usd: float,
    splits: tuple[str, ...],
    categories: tuple[str, ...],
    languages: tuple[str, ...],
) -> None:
    from openai import OpenAI

    OUTPUT.mkdir(parents=True, exist_ok=True)
    ledger_path = OUTPUT / "usage_ledger.json"
    ledger = _read_json(ledger_path, {"model": MODEL, "requests": [], "estimated_peak_usd": 0.0})
    records_path = OUTPUT / "all.jsonl"
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()] if records_path.exists() else []
    existing = {record["id"] for record in records}
    seen = {hashlib.sha256((_normalize(record["context"]) + "\n" + _normalize(record["question"])).encode()).hexdigest() for record in records}
    client = OpenAI(base_url="https://api.orcarouter.ai/v1", api_key=_load_key(), timeout=90, max_retries=0)
    accepted = 0
    rejected = Counter()
    for split in splits:
        batch_count = train_batches if split == "train" else holdout_batches
        for category in categories:
            for language in languages:
                for batch in range(batch_count):
                    base = batch * batch_size
                    ids = [f"pv1_{split}_{category}_{language}_{base+i:04d}" for i in range(batch_size)]
                    pending = [(item, _spec(category, split, base + i)) for i, item in enumerate(ids) if item not in existing]
                    if not pending:
                        continue
                    ids, specs = zip(*pending)
                    prompt = _prompt(category, language, split, specs)
                    # Reserve a worst-case peak-price request before sending it.
                    max_tokens = 3600
                    conservative_prompt_tokens = len(prompt) + len(SYSTEM)
                    reserve = conservative_prompt_tokens * 0.30 / 1_000_000 + max_tokens * 1.20 / 1_000_000
                    if ledger["estimated_peak_usd"] + reserve > budget_usd:
                        print(f"BUDGET_STOP peak_estimate={ledger['estimated_peak_usd']:.4f} budget={budget_usd:.2f}")
                        return
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                        response_format={"type": "json_object"},
                        max_tokens=max_tokens,
                        extra_body={"thinking": {"type": "disabled"}},
                    )
                    usage = response.usage
                    if not usage:
                        raise RuntimeError("Model response omitted token usage; cannot enforce budget")
                    estimated = usage.prompt_tokens * 0.30 / 1_000_000 + usage.completion_tokens * 1.20 / 1_000_000
                    ledger["estimated_peak_usd"] += estimated
                    ledger["requests"].append({
                        "split": split, "category": category, "language": language, "batch": batch,
                        "response_model": response.model, "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "estimated_peak_usd": round(estimated, 8),
                        "finish_reason": response.choices[0].finish_reason,
                    })
                    _save_json(ledger_path, ledger)
                    if response.choices[0].finish_reason != "stop":
                        rejected["truncated_batch"] += len(specs)
                        continue
                    try:
                        generated = json.loads(response.choices[0].message.content or "{}")["examples"]
                    except (ValueError, KeyError, TypeError):
                        rejected["invalid_json_batch"] += len(specs)
                        continue
                    if not isinstance(generated, list) or len(generated) != len(specs):
                        rejected["wrong_batch_size"] += len(specs)
                        continue
                    for i, (spec, raw) in enumerate(zip(specs, generated)):
                        if ids[i] in existing:
                            continue
                        try:
                            record = _validate(category, language, spec, raw, seen)
                        except (ValueError, KeyError, TypeError) as exc:
                            rejected[type(exc).__name__ + ":" + str(exc)[:55]] += 1
                            continue
                        record.update({"id": ids[i], "group_id": ids[i], "split": split})
                        with records_path.open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                        existing.add(ids[i])
                        accepted += 1
                    print(f"{split}/{category}/{language}/b{batch}: accepted={accepted} peak_estimate=${ledger['estimated_peak_usd']:.4f}", flush=True)
    print(json.dumps({"accepted_this_run": accepted, "total_records": len(existing), "estimated_peak_usd": round(ledger["estimated_peak_usd"], 6), "rejections": dict(rejected)}, ensure_ascii=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-size", type=int, default=6)
    parser.add_argument("--train-batches", type=int, default=2)
    parser.add_argument("--holdout-batches", type=int, default=1)
    parser.add_argument("--budget-usd", type=float, default=5.0)
    parser.add_argument("--splits", nargs="+", choices=SPLITS, default=SPLITS)
    parser.add_argument("--categories", nargs="+", choices=CATEGORIES, default=CATEGORIES)
    parser.add_argument("--languages", nargs="+", choices=tuple(LANGUAGES), default=tuple(LANGUAGES))
    parser.add_argument("--repair-holdout-arithmetic", action="store_true")
    args = parser.parse_args()
    if args.repair_holdout_arithmetic:
        repair_holdout_arithmetic()
        return
    if args.budget_usd <= 0 or args.budget_usd > 10 or not 1 <= args.batch_size <= 8:
        raise ValueError("budget must be (0, 10] USD and batch size 1..8")
    generate(
        args.batch_size,
        args.train_batches,
        args.holdout_batches,
        args.budget_usd,
        tuple(args.splits),
        tuple(args.categories),
        tuple(args.languages),
    )


if __name__ == "__main__":
    main()
