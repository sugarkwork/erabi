"""Build the private Decision Mix V2 corpus with DeepSeek through OrcaRouter.

The script is resumable and fail-closed.  Paid requests are sent only during
the documented off-peak windows, each request is journaled before dispatch,
and unresolved requests are never retried automatically.
"""
from __future__ import annotations

import argparse
import asyncio
import copy
import datetime as dt
import hashlib
import json
import os
import random
import re
import statistics
import time
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from erabi.schema import ChoiceRequest
from scripts.build_exam_qa_erabi_v1 import TokenCounter
from scripts.build_exam_qa_weakness_v1 import append_jsonl, journal_cost, read_jsonl
from scripts.build_practical_v1 import _language_ok

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "decision_mix_v2"
KEY_FILE = ROOT / ".env.orcarouter.local"
TOKENIZER_DIR = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "checkpoint-epoch-3"
if not TOKENIZER_DIR.exists():
    TOKENIZER_DIR = ROOT / "runs" / "exam_qa_erabi_v1_finetune_20260923" / "checkpoint"
MODEL = "deepseek/deepseek-v4.1-flash"
VERSION = "v4"
SEED = 20260929
CAP_USD = 15.0
OFFPEAK_INPUT = 0.15 / 1_000_000
OFFPEAK_OUTPUT = 0.60 / 1_000_000
PILOT_PER_FAMILY = 15
GROUP_SIZE = 3
GROUPS_PER_FAMILY_ROUND = 3  # Nine examples per family before rotating.

FAMILIES: dict[str, dict[str, Any]] = {
    "npc_goal": {
        "purpose": "Choose an NPC action from role, priorities, relationships, ability, personality, emotion, body, resources, beliefs, partial knowledge and recent events.",
        "requirements": "Use readable field names. Separate stable traits from temporary emotion. State the priority hierarchy and effects of every offered action. Within a group change one named factor and make both changed and unchanged decisions possible. Do not assume universal morality.",
        "subskills": ["duty versus fear", "protective relationship", "mission versus ally", "belief correction", "resource scarcity"],
        "structured": True,
        "target": 1500,
    },
    "platformer_control": {
        "purpose": "Choose one short legal control macro in an original side-scrolling simulation.",
        "requirements": "No copyrighted game names, maps or characters. Give readable numeric position, velocity, grounded/jump phase, terrain, hazards, reaction delay, recent control and bounded action outcomes. Use only legal macros and make the one-step objective explicit.",
        "subskills": ["gap timing", "enemy contact horizon", "low ceiling", "momentum and braking", "stalled movement"],
        "structured": True,
        "target": 500,
    },
    "voxel_survival": {
        "purpose": "Choose the next executable skill or target in an original voxel survival simulation.",
        "requirements": "No copyrighted game names or assets. Give readable goal, subgoal, completion rule, dependencies, health, hunger, time, depth, light, hazards, equipment, durability, inventory, nearby resources and recent failures. Offer only currently executable skills. Keep skill choice and target choice separate.",
        "subskills": ["acquisition dependency", "night safety", "tool durability", "inventory bottleneck", "failed-action recovery"],
        "structured": True,
        "target": 700,
    },
    "command_safety": {
        "purpose": "Defensively classify the risk or handling policy for a command without executing it.",
        "requirements": "State OS, shell, cwd, allowed scope, privilege, execution versus quotation or dry-run, variables/globs/symlinks, backup and external transmission. Cover scope escape, secret access, deletion, history destruction, system damage, privilege escalation, exfiltration and recoverability. Include safe lookalikes and one-factor reversals. Never provide an attack tutorial.",
        "subskills": ["scope boundary", "secret access", "destructive filesystem", "repository history", "external transmission"],
        "structured": True,
        "target": 1000,
    },
    "weakness_counterfactual": {
        "purpose": "Create original boundary cases for observed weak task families without copying public benchmark text.",
        "requirements": "Create fully original self-contained items. Cycle sentiment intensity, emotion, English or Chinese NLI, and prompt-injection boundaries. Include negation, quotation, mixed emotion, instruction-versus-data separation and harmless near matches. Do not name or paraphrase a benchmark.",
        "subskills": ["sentiment intensity", "emotion boundary", "English NLI", "Chinese NLI", "prompt injection boundary"],
        "structured": False,
        "target": 1000,
    },
    "general_gate": {
        "purpose": "Classify non-graphic conversational gate categories and the appropriate handling level.",
        "requirements": "Use only non-graphic ordinary conversation, verbal abuse, harassment, non-explicit sexual harassment, threats, profanity, prompt injection, privacy or secret requests, and none. Distinguish direct utterance from quotation, reporting, victim support and refusal. Exclude child exploitation, explicit sexual content, medical decisions, criminal instructions and explosive construction.",
        "subskills": ["direct versus quoted abuse", "harassment versus criticism", "threat versus idiom", "privacy request", "prompt injection versus discussion"],
        "structured": False,
        "target": 800,
    },
}

COMMON_SYSTEM = """Return JSON only as {"examples":[...]}. Create original, self-contained single-answer examples for a local choice-ranking model. Each example must contain exactly: id, context, question, choices [{id,text}], correct_choice_id, answer_explanation. Copy each requested id exactly and use c1..cN in order. Follow the supplied family, language, subskill, representation and counterfactual axis exactly.

Exactly one choice must be defensible from the input. State every fact, priority, constraint and action effect needed to distinguish it. Evaluate every choice before labeling. If several choices are feasible, add an explicit optimization goal and tie-breaker to the input. Keep choices mutually exclusive, comparable in specificity and similar in length. The correct answer must not be the only careful, safe, detailed or long choice. Explanations are audit metadata and must not appear in context or question.

All content must be fictional and newly written. Do not copy or paraphrase benchmarks, exams, private conversations, copyrighted game material, named real incidents or personal data. Do not include URLs, credentials or real identifiers. Stay outside child exploitation, explicit sexual content, medical decisions, criminal facilitation and explosive construction. Defensive command strings may appear only as inert text for risk classification and must never be executed.

Structured examples must use valid compact JSON as the context, with every key at least two written characters long, including Japanese and Chinese keys. Never use opaque one-letter keys, unexplained numeric enums or opaque action codes. Keep structured inputs below about 330 multilingual tokens and prose inputs below about 250 so the complete model input remains below 512. Do not add filler. In answer_explanation refer to choices by their full text, never by c1/c2/c3/c4. Within one scenario group, preserve the same basic world while changing exactly the requested counterfactual factor; some changes should alter the best action and some should not."""

JUDGE_SYSTEM = """Independently solve and audit the supplied original choice items without seeing any proposed answer or explanation. Return JSON only as {"judgments":[{id,valid,selected_choice_id,issue,reason}]}. Check every candidate. valid is false if multiple answers work, no answer works, a needed fact or action effect is missing, rules conflict, the answer is leaked, structured keys are opaque, language is broken, the item relies on a copyrighted game convention, or excluded sensitive material appears. For command items treat commands as inert text and judge only defensive risk. Do not rewrite an item. reason and issue must be concise."""


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def _load_key() -> str:
    values = []
    for line in KEY_FILE.read_text(encoding="utf-8").splitlines():
        name, sep, value = line.strip().partition("=")
        if sep and name == "ORCAROUTER_API_KEY" and value:
            values.append(value)
    if len(values) != 1:
        raise RuntimeError("Expected exactly one ORCAROUTER_API_KEY in the ignored local file")
    return values[0]


def _offpeak(now: dt.datetime | None = None) -> bool:
    now = now or dt.datetime.now(dt.timezone.utc)
    return now.weekday() >= 5 or not (1 <= now.hour < 4 or 6 <= now.hour < 10)


def _normalize(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKC", text).casefold() if ch.isalnum())


def _signature(row: dict[str, Any]) -> str:
    return hashlib.sha256(_normalize(row["context"] + "\n" + row["question"]).encode()).hexdigest()


def _all_historical_signatures() -> tuple[set[str], int]:
    seen: set[str] = set()
    count = 0
    for path in (ROOT / "data").rglob("*.jsonl"):
        if OUT in path.parents or any(part in path.name for part in ("journal", "judgment", "rejection")):
            continue
        for row in read_jsonl(path):
            if isinstance(row, dict) and isinstance(row.get("context"), str) and isinstance(row.get("question"), str):
                seen.add(_signature(row))
                count += 1
    return seen, count


def _existing_decision_mix_signatures() -> tuple[set[str], int]:
    seen: set[str] = set()
    count = 0
    for path in OUT.glob("*/groups/*.json"):
        try:
            rows = json.loads(path.read_text(encoding="utf-8")).get("accepted", [])
        except (OSError, json.JSONDecodeError, AttributeError):
            continue
        for row in rows:
            if isinstance(row, dict) and isinstance(row.get("context"), str) and isinstance(row.get("question"), str):
                seen.add(_signature(row))
                count += 1
    return seen, count


def _human_readable_keys(value: Any) -> bool:
    if isinstance(value, dict):
        return all(isinstance(key, str) and len(key) >= 2 and _human_readable_keys(child) for key, child in value.items())
    if isinstance(value, list):
        return all(_human_readable_keys(child) for child in value)
    return True


def _language_for(index: int) -> str:
    return (["ja"] * 9 + ["en"] * 3 + ["zh-Hans"] * 3)[index % 15]


def _split_for(family: str, group_index: int) -> str:
    value = int(hashlib.sha256(f"{SEED}:{family}:{group_index}".encode()).hexdigest()[:8], 16) % 100
    if value < 80:
        return "train"
    if value < 88:
        return "dev"
    if value < 93:
        return "calibration"
    return "final_test"


def make_specs(family: str, pilot: bool) -> list[list[dict[str, Any]]]:
    config = FAMILIES[family]
    count = PILOT_PER_FAMILY if pilot else int(config["target"])
    groups = []
    for start in range(0, count, GROUP_SIZE):
        group_index = start // GROUP_SIZE
        group_id = f"dm2_{'pilot' if pilot else 'main'}_{VERSION}_{family}_{group_index:05d}"
        group = []
        for offset in range(min(GROUP_SIZE, count - start)):
            index = start + offset
            subskill = config["subskills"][group_index % len(config["subskills"])]
            group.append({
                "id": f"{group_id}_v{offset + 1}",
                "group_id": group_id,
                "family": family,
                "purpose": config["purpose"],
                "requirements": config["requirements"],
                "subskill": subskill,
                "language": _language_for(index),
                "representation": "readable_json" if config["structured"] else "natural_prose",
                "choice_count": 4,
                "counterfactual_axis": subskill,
                "variant": offset + 1,
                "split": "pilot" if pilot else _split_for(family, group_index),
                "diversity_seed": SEED + index * 97 + list(FAMILIES).index(family) * 100_000,
            })
        groups.append(group)
    return groups


def generation_prompt(specs: list[dict[str, Any]]) -> str:
    return json.dumps({
        "instruction": "Generate the requested counterfactual scenario group in the same order. Change exactly the requested factor between variants while keeping other relevant facts stable. Do not merely rename entities or copy sentences.",
        "specifications": specs,
    }, ensure_ascii=False)


def validate(raw: Any, spec: dict[str, Any], counter: TokenCounter) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("id") != spec["id"]:
        raise ValueError("id_mismatch")
    value = copy.deepcopy(raw)
    if spec["representation"] == "readable_json":
        if isinstance(value.get("context"), dict):
            if not _human_readable_keys(value["context"]):
                raise ValueError("opaque_key")
            value["context"] = json.dumps(value["context"], ensure_ascii=False, separators=(",", ":"))
        elif isinstance(value.get("context"), str):
            parsed = json.loads(value["context"])
            if not isinstance(parsed, dict) or not _human_readable_keys(parsed):
                raise ValueError("invalid_readable_json")
            value["context"] = json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
        else:
            raise ValueError("context_not_json")
    for key in ("context", "question", "answer_explanation"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError("missing_" + key)
    choices = value.get("choices")
    if not isinstance(choices, list) or len(choices) != spec["choice_count"]:
        raise ValueError("choice_count")
    if [choice.get("id") for choice in choices if isinstance(choice, dict)] != [f"c{i + 1}" for i in range(len(choices))]:
        raise ValueError("choice_ids")
    ChoiceRequest.from_dict({"context": value["context"], "question": value["question"], "choices": choices})
    texts = [choice["text"].strip() for choice in choices]
    if len({_normalize(text) for text in texts}) != len(texts):
        raise ValueError("duplicate_choices")
    if value.get("correct_choice_id") not in {choice["id"] for choice in choices}:
        raise ValueError("invalid_target")
    combined = value["context"] + " " + value["question"] + " " + " ".join(texts)
    if not _language_ok(spec["language"], combined):
        raise ValueError("language")
    if re.search(r"https?://|sk-[A-Za-z0-9]{10,}|<<LABEL>>|<<SEP>>|<<EXAMPLE>>", combined):
        raise ValueError("forbidden_text")
    if spec["family"] == "general_gate" and re.search(r"児童|child sexual|爆弾.{0,8}(作|製)|explosive.{0,8}(build|make)", combined, re.I):
        raise ValueError("excluded_sensitive_scope")
    row = {"id": value["id"], "context": value["context"], "question": value["question"], "choices": choices}
    token_count = counter.count(row)
    if not 20 <= token_count <= 512:
        raise ValueError("token_range")
    answer_text = next(choice["text"] for choice in choices if choice["id"] == value["correct_choice_id"])
    old_ids_by_text = {choice["text"]: choice["id"] for choice in choices}
    random.Random(spec["id"]).shuffle(choices)
    shuffled = [{"id": f"c{i + 1}", "text": choice["text"]} for i, choice in enumerate(choices)]
    target_id = next(choice["id"] for choice in shuffled if choice["text"] == answer_text)
    new_ids_by_old = {
        old_ids_by_text[choice["text"]]: choice["id"]
        for choice in shuffled
    }
    explanation = value["answer_explanation"]
    explanation = re.sub(
        r"\bc([1-4])\b",
        lambda match: "__CHOICE_" + new_ids_by_old.get(match.group(0), match.group(0))[1:] + "__",
        explanation,
    )
    explanation = re.sub(r"__CHOICE_([1-4])__", r"c\1", explanation)
    lengths = [len(choice["text"]) for choice in shuffled]
    return {
        "schema_version": "1",
        "id": value["id"],
        "group_id": spec["group_id"],
        "task_family": "decision_mix_v2",
        "domain": spec["family"],
        "language": spec["language"],
        "split": spec["split"],
        "context": value["context"],
        "question": value["question"],
        "choices": shuffled,
        "target": {"kind": "hard", "choice_id": target_id},
        "answer_explanation": explanation,
        "input_tokens": token_count,
        "choice_char_lengths": lengths,
        "source": {"kind": "synthetic", "model": MODEL, "prompt_version": VERSION},
        "generation_spec": spec,
        "quality": {"label_status": "deepseek_generated_unreviewed"},
    }


class BudgetExhausted(RuntimeError):
    pass


class BudgetClient:
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        self.path = OUT / "api_journal.jsonl"
        journal = read_jsonl(self.path)
        self.spent, self.reserved, _, _ = journal_cost(journal)
        self.responses = {row["batch_key"]: row for row in journal if row.get("event") == "response"}
        self.pending = {row["batch_key"] for row in journal if row.get("event") == "pending"}
        self.active = 0
        self.client = AsyncOpenAI(base_url="https://api.orcarouter.ai/v1", api_key=_load_key(), timeout=240, max_retries=0)

    async def call(self, kind: str, ids: list[str], system: str, prompt: str, max_tokens: int) -> dict[str, Any]:
        key = hashlib.sha256((kind + VERSION + system + prompt).encode()).hexdigest()
        if key in self.responses:
            event = self.responses[key]
            return event["payload"] if event.get("finish_reason") == "stop" else {}
        if key in self.pending:
            return {}
        if not _offpeak() or not _offpeak(dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=240)):
            raise RuntimeError("paid_call_outside_offpeak")
        reserve = (len((system + prompt).encode("utf-8")) + 1024) * OFFPEAK_INPUT + max_tokens * OFFPEAK_OUTPUT
        while self.spent + self.reserved + reserve >= CAP_USD:
            if not self.active:
                raise BudgetExhausted("new_15_usd_cap_reached")
            await asyncio.sleep(1)
        self.pending.add(key)
        self.reserved += reserve
        append_jsonl(self.path, {"event": "pending", "batch_key": key, "kind": kind, "ids": ids, "reserve_usd": reserve, "time": time.time()})
        self.active += 1
        try:
            response = await self.client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7 if kind == "generate" else 0,
                max_tokens=max_tokens,
                reasoning_effort="low",
                extra_body={"thinking": {"type": "disabled"}},
            )
            if response.usage is None:
                raise RuntimeError("missing_usage")
            content = response.choices[0].message.content or ""
            try:
                payload = json.loads(content)
                if not isinstance(payload, dict):
                    payload = {"invalid_shape": True}
            except json.JSONDecodeError:
                payload = {"invalid_json": content}
            cost = response.usage.prompt_tokens * OFFPEAK_INPUT + response.usage.completion_tokens * OFFPEAK_OUTPUT
            event = {
                "event": "response", "batch_key": key, "kind": kind, "ids": ids,
                "payload": payload, "estimated_usd": cost,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "response_model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "input_usd_per_token": OFFPEAK_INPUT,
                "output_usd_per_token": OFFPEAK_OUTPUT,
            }
            append_jsonl(self.path, event)
            self.responses[key] = event
            self.spent += cost
            self.reserved -= reserve
            return payload if event["finish_reason"] == "stop" else {}
        except Exception as exc:
            append_jsonl(self.path, {"event": "error", "batch_key": key, "error_type": type(exc).__name__, "http_status": getattr(exc, "status_code", None)})
            return {}
        finally:
            self.active -= 1

    def summary(self) -> dict[str, Any]:
        return {"new_estimated_usd": round(self.spent, 8), "unresolved_reserved_usd": round(self.reserved, 8), "conservative_total_usd": round(self.spent + self.reserved, 8), "cap_usd": CAP_USD}


async def build(mode: str, workers: int, attempts: int, selected_families: list[str]) -> None:
    if not _offpeak():
        raise RuntimeError("paid_call_outside_offpeak")
    OUT.mkdir(parents=True, exist_ok=True)
    prompt_manifest = {
        "version": VERSION,
        "model": MODEL,
        "common_system": COMMON_SYSTEM,
        "judge_system": JUDGE_SYSTEM,
        "families": FAMILIES,
        "common_sha256": hashlib.sha256(COMMON_SYSTEM.encode()).hexdigest(),
        "judge_sha256": hashlib.sha256(JUDGE_SYSTEM.encode()).hexdigest(),
    }
    _write_json(OUT / f"prompts_{VERSION}.json", prompt_manifest)
    if mode == "main":
        approval = json.loads((OUT / "pilot_approval.json").read_text(encoding="utf-8"))
        if approval.get("approved_prompt_sha256") != prompt_manifest["common_sha256"]:
            raise RuntimeError("pilot_not_approved_for_current_prompt")
        if approval.get("prompt_version") != VERSION:
            raise RuntimeError("pilot_version_not_approved")
        approved = set(approval.get("approved_families", []))
        if not set(selected_families) <= approved:
            raise RuntimeError("family_not_approved")
    counter = TokenCounter(TOKENIZER_DIR)
    seen, history_count = _all_historical_signatures()
    existing_seen, existing_count = _existing_decision_mix_signatures()
    seen.update(existing_seen)
    client = BudgetClient()
    semaphore = asyncio.Semaphore(workers)
    rejected: Counter[str] = Counter()
    accepted_by_family: dict[str, list[dict[str, Any]]] = {family: [] for family in selected_families}

    async def run_group(specs: list[dict[str, Any]]) -> None:
        family = specs[0]["family"]
        group_id = specs[0]["group_id"]
        path = OUT / mode / "groups" / f"{group_id}.json"
        if path.exists():
            accepted_by_family[family].extend(json.loads(path.read_text(encoding="utf-8")).get("accepted", []))
            return
        async with semaphore:
            accepted: list[dict[str, Any]] = []
            for attempt in range(attempts):
                pending_specs = [{**spec, "attempt": attempt + 1} for spec in specs if spec["id"] not in {row["id"] for row in accepted}]
                if not pending_specs:
                    break
                payload = await client.call("generate", [spec["id"] for spec in pending_specs], COMMON_SYSTEM, generation_prompt(pending_specs), 4000)
                values = payload.get("examples", [])
                by_id = {row.get("id"): row for row in values if isinstance(row, dict)} if isinstance(values, list) else {}
                if len(pending_specs) == 1 and isinstance(values, list) and len(values) == 1 and isinstance(values[0], dict):
                    by_id[pending_specs[0]["id"]] = {**values[0], "id": pending_specs[0]["id"]}
                candidates = []
                for spec in pending_specs:
                    try:
                        row = validate(by_id.get(spec["id"]), spec, counter)
                        signature = _signature(row)
                        if signature in seen:
                            raise ValueError("duplicate_input")
                        seen.add(signature)
                        candidates.append(row)
                    except Exception as exc:
                        rejected[f"local:{str(exc)[:80]}"] += 1
                        append_jsonl(OUT / "rejections.jsonl", {"id": spec["id"], "stage": "local", "reason": str(exc)[:200]})
                if candidates:
                    blind = [{key: row[key] for key in ("id", "domain", "context", "question", "choices")} for row in candidates]
                    judged = await client.call("judge", [row["id"] for row in candidates], JUDGE_SYSTEM, json.dumps({"items": blind}, ensure_ascii=False), 2500)
                    judgments = judged.get("judgments", [])
                    judged_by_id = {item.get("id"): item for item in judgments if isinstance(item, dict)} if isinstance(judgments, list) else {}
                    for row in candidates:
                        judgment = judged_by_id.get(row["id"], {})
                        append_jsonl(OUT / "judgments.jsonl", {"id": row["id"], **judgment})
                        if judgment.get("valid") is True and judgment.get("selected_choice_id") == row["target"]["choice_id"]:
                            row["quality"] = {"label_status": "deepseek_answer_blind_agreed_not_human_gold", "judge_reason": judgment.get("reason", "")}
                            accepted.append(row)
                        else:
                            rejected["judge:invalid_or_disagreed"] += 1
                            append_jsonl(OUT / "rejections.jsonl", {"id": row["id"], "stage": "judge", "judgment": judgment})
            _write_json(path, {"group_id": group_id, "family": family, "accepted": accepted})
            accepted_by_family[family].extend(accepted)

    jobs = []
    groups_by_family = {
        family: make_specs(family, mode == "pilot")
        for family in selected_families
    }
    max_groups = max((len(groups) for groups in groups_by_family.values()), default=0)
    # Keep the corpus balanced if the spend cap is reached mid-run. A scenario
    # group contains three counterfactual variants, so rotate after 3 groups =
    # 9 requested examples instead of breaking a group to hit exactly ten.
    for start in range(0, max_groups, GROUPS_PER_FAMILY_ROUND):
        for family in selected_families:
            jobs.extend(
                run_group(group)
                for group in groups_by_family[family][start:start + GROUPS_PER_FAMILY_ROUND]
            )
    try:
        await asyncio.gather(*jobs)
    finally:
        _write_json(OUT / "cost_summary.json", client.summary())
        await client.client.close()

    rows = [row for family in selected_families for row in accepted_by_family[family]]
    _write_jsonl(OUT / mode / "accepted.jsonl", rows)
    family_report = {}
    rng = random.Random(SEED)
    samples = []
    for family, family_rows in accepted_by_family.items():
        target_count = PILOT_PER_FAMILY if mode == "pilot" else FAMILIES[family]["target"]
        longest_correct = sum(
            row["choice_char_lengths"][int(row["target"]["choice_id"][1:]) - 1] == max(row["choice_char_lengths"])
            for row in family_rows
        )
        family_report[family] = {
            "accepted": len(family_rows),
            "target": target_count,
            "acceptance_rate": len(family_rows) / target_count if target_count else 0,
            "token_min": min((row["input_tokens"] for row in family_rows), default=None),
            "token_median": statistics.median((row["input_tokens"] for row in family_rows)) if family_rows else None,
            "token_max": max((row["input_tokens"] for row in family_rows), default=None),
            "longest_choice_correct_rate": longest_correct / len(family_rows) if family_rows else None,
            "position_counts": dict(Counter(row["target"]["choice_id"] for row in family_rows)),
        }
        samples.extend(rng.sample(family_rows, min(3, len(family_rows))))
    report = {
        "mode": mode,
        "model": MODEL,
        "prompt_version": VERSION,
        "historical_rows_screened": history_count,
        "existing_decision_mix_rows_screened": existing_count,
        "accepted": len(rows),
        "families": family_report,
        "rejections_this_process": dict(rejected),
        "cost": client.summary(),
    }
    _write_json(OUT / f"{mode}_report.json", report)
    _write_json(OUT / f"{mode}_fixed_sample.json", samples)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


def inspect() -> None:
    report_path = OUT / "pilot_report.json"
    if not report_path.exists():
        raise FileNotFoundError(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("pilot", "main", "inspect"))
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--attempts", type=int, default=2)
    parser.add_argument("--families", nargs="+", choices=tuple(FAMILIES), default=list(FAMILIES))
    args = parser.parse_args()
    if not 1 <= args.workers <= 12 or not 1 <= args.attempts <= 4:
        parser.error("invalid workers or attempts")
    if args.mode == "inspect":
        inspect()
    else:
        asyncio.run(build(args.mode, args.workers, args.attempts, args.families))


if __name__ == "__main__":
    main()
