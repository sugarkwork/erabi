"""Private DeepSeek world/choice corpus: pilot, budgeted generation, blind audit.

Run from repository root with ``python -m scripts.build_world_choice_v1``.
All example text and labels originate in DeepSeek responses, not this script.
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
import time
import unicodedata
from collections import Counter
from pathlib import Path

from erabi.schema import ChoiceRequest
from scripts.build_exam_qa_erabi_v1 import TokenCounter
from scripts.build_exam_qa_weakness_v1 import journal_cost, read_jsonl, append_jsonl
from scripts.build_practical_v1 import _language_ok

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/world_choice_v1"
TOKENIZER = ROOT / "runs/exam_qa_erabi_v1_finetune_20260923/checkpoint"
MODEL = os.environ.get("ERABI_DATA_GEN_MODEL", "deepseek/deepseek-v4.1-flash")
SEED = 20260926
# Earlier cumulative $2.2612974 plus pilot $0.0099438, rounded UP.
PRIOR_USD = 2.28
GLOBAL_CAP = 10.0
INPUT_PRICE, OUTPUT_PRICE = 0.30 / 1e6, 1.20 / 1e6
VERSION = "v4"

CATEGORIES = {
    "color_shape": ("色・形・身近な属性", "Everyday colors, shapes, material properties and object classification. Include ordinary basic knowledge; qualify variety, ripeness, lighting or convention if relevant. Do not assert that every apple has one color.", ["food properties", "geometric shapes", "everyday materials", "object sorting", "color conventions"]),
    "animals": ("動物・鳴き声・生態", "Animal sounds, movement, body features, diet and habitats. Qualify species, life stage, language-specific onomatopoeia and exceptions. Avoid subjective or culturally ambiguous categories.", ["animal sounds", "movement", "habitats", "life stages", "physical features"]),
    "everyday_quantity": ("日常の数量・時間判断", "Practical quantity, duration, capacity, scheduling and unit reasoning. Supply exact numbers, units, rounding and every needed assumption. Compute the answer twice; exactly one numeric option must agree.", ["time scheduling", "capacity", "unit conversion", "two-step quantities", "rates and stock"]),
    "tool_routing": ("会話・ツール選択", "A natural multi-turn user/assistant conversation and selection of the single immediate next tool or no-tool reply. Vary chat, web search, image creation, video creation, permitted sandbox command, screenshot capture, attached-image analysis and game-state query. State tool availability, image attachment status, authorization and whether information is already supplied. Do not use a web search for fictional game state.", ["freshness versus supplied facts", "capture versus image analysis", "image versus video creation", "authorized execution versus explanation", "game state versus real world"]),
    "conversation_memory": ("会話の記憶・訂正・確認", "Multi-turn conversation requiring an earlier fact, a later correction, temporal order, speaker attribution, scope of a preference or a targeted clarification. Include necessary information in actual messages. Vary direct answer, clarification and honoring a changed request. The last message must not restate all relevant history.", ["later correction", "speaker attribution", "changed preference", "missing information", "temporal order"]),
    "robot_fault": ("自律ロボットの故障対応", "Fictional robot with battery, mobility, sensor, communication or thermal faults. State its objective, priority order, exact constraints and effects/availability of candidate actions. Require combining at least two facts. Vary safe continuation, substitution, local repair, returning, stopping and requesting help; do not make stopping always correct.", ["mobility and battery", "sensor substitution", "communication failure", "safe local repair", "conflicting alarms"]),
    "resource_navigation": ("資源・経路・作業計画", "Fictional agent choosing a feasible route or next work step with energy, time, terrain, carrying capacity and dependencies. Define costs and safety margins precisely. Supply all graph edges if routing matters; choose a uniquely optimal or uniquely feasible option under an explicit priority.", ["route energy", "deadline and detour", "payload constraints", "task dependencies", "reserve and replenishment"]),
    "rpg_survival": ("RPGの戦闘・生存判断", "Original RPG situation combining health, status effects, turn order, equipment, available items, enemies and terrain. Explicitly state relevant game rules, damage/healing, action effects and objective. Avoid unstated real-game conventions. Vary healing, defense, attack, retreat, assistance and status management. Never offer nonexistent items as if usable.", ["poison and turn order", "equipment interaction", "escape constraints", "healing versus damage", "ally assistance"]),
    "npc_social_quest": ("NPCの会話・クエスト判断", "Original NPC/player multi-turn conversation with local knowledge, role, inventory, quest prerequisites, trust or negotiated goals. State permission and reward rules. The NPC may use only knowledge it has; vary responding, asking, querying state, trading, giving a quest and declining. Require history plus a current state fact.", ["quest prerequisite", "inventory and trade", "limited NPC knowledge", "role and permission", "dialogue state transition"]),
    "world_rules": ("複合世界ルール・例外判断", "Fictional world simulation combining multiple entities, state updates, resource limits and ordered rules/exceptions. State priority and tie-breaking rules. Require at least two facts, not a direct copy of an answer sentence. Include negation, unavailable evidence and a justified request for clarification where uniquely correct.", ["rule exceptions", "simultaneous events", "shared resources", "conflicting objectives", "partial observation"]),
}

SYSTEM = """Create original high-quality single-answer examples for a local choice-ranking model. Return JSON only: {"examples":[...]}. Invent every example, world, conversation and answer yourself. Do not copy published benchmarks, exams, copyrighted game dialogue, private logs or real personal data. Follow each supplied specification exactly.
Each example is {id,context,question,choices:[{id:"c1",text:...},...],correct_choice_id,answer_explanation}. All strings must be in the specified language except JSON keys, proper names and standard technical labels. Exactly one answer must be defensible. Keep the explanation brief, at most 50 words, outside the input. Solve independently twice, including arithmetic and state transitions, before returning the label. Never include answer labels, grading instructions or explanations in context/question. Choice ids are c1..cN in order. Choose the correct answer naturally; answer positions will be randomized locally.
Use realistic concise choices of comparable detail and length; the correct option must not stand out by being the only nuanced/safe/long one. Distractors should represent plausible mistakes. For policy/action tasks explicitly state the objective, relevant action effects, available actions and priority/tie rules, so the answer is not an arbitrary value judgment. Avoid outside information, omitted images, implicit probabilities and unstated game mechanics. Basic everyday-fact categories may test stable common knowledge; qualify ambiguous properties.
All examples in a batch must differ in underlying facts and decisions, not merely names or numbers. No translations/paraphrases of another item. Do not use example ids, seed or split names inside the problem. When conversation_json is true, context must be a JSON-encoded object with a messages array of at least 3 {role,content} messages and optional state/rules fields. roles are user/assistant/system; content is a string. End the messages with a user request. No assistant turn may already solve or summarize the answer to the final question; require genuine use of history. When false, use natural prose or compact state with full sentences. Total input, including choices, must fit 1024 multilingual model tokens. Target the provided length guidance; no filler padding.
Mandatory uniqueness checks before output: (1) Evaluate EVERY choice under the exact stated rules. (2) Different descriptions of the SAME action/route are duplicates even if reasons differ, and are forbidden. (3) If multiple actions succeed, put an explicit optimization objective and tie-breaker in the INPUT, never only in the explanation. (4) Candidate actions must be mutually exclusive single next actions; do not mix one action and multi-action plans or attach redundant conditional clauses. (5) In combat state enemy damage, initiative, status tick timing, action costs and the evaluation horizon. Check survival and feasibility of every option numerically. (6) An exception must really override a rule under the stated priority; avoid contradictory priority declarations. (7) Use only justified distractors; do not pad larger choice sets with unavailable magic capabilities or implausible misconduct. For basic facts ask the actual fact about a concrete named object/species, not repeat an adjective already in context. The explanation must establish why the selected action is uniquely best, not just feasible.
For complex simulations prefer a bounded one-turn/one-step decision with explicitly defined effects for ALL listed actions. Compute consequences before finalizing numbers; alter the fictional initial conditions if needed so exactly one choice wins. Do not publish a problem whose own explanation admits no solution. The rules are the authoritative world model, so do not silently assume an unmentioned option has a cost/effect. Keep concise narrative realism while making the small simulated world executable from the supplied facts. For conversations, do not have the assistant prescribe the final next step before the user asks; use a new state update that changes the decision.
Quantity wording must distinguish BEFORE/AFTER, initial/current stock, owned/physically available stock, and percentage points/relative percent. Borrowing a library book does not remove it from the library's owned collection; use available-on-shelf stock with explicit return assumptions if needed. If an amount is given before an already completed action, explicitly say it was the initial amount. In tool requests name the subject/place/object sufficiently to act; when required information is missing, clarification can be the right response. Vary the real-world setting and mechanism per item; do not fill a batch with renamed water tanks or the same algebraic template. Match the id exactly and keep example order identical to the requested specification order."""

JUDGE = """Independently solve these original choice problems without a proposed answer. Return JSON {"judgments":[{id,valid,selected_choice_id,issue,reason}]} in order. valid must be false if multiple answers work, no answer works, arithmetic/game rules conflict, a necessary assumption/action effect is missing, the question leaks the answer, the requested next action is unsupported, or language is broken. Basic stable everyday knowledge is allowed for colors/animals. For simulations use the stated objective, action order, constraints and effects, not assumptions from real games. Recompute numeric outcomes. Check EVERY alternative: two phrasings of the same action/route count as multiple correct answers even if one explanation sounds better. If several actions meet the stated goal and no explicit optimization preference separates them, reject. Combat requires numeric damage, status timing and horizon; reject if a missing value could change the best choice. Reject conversation-memory items where the last assistant already states the full answer, and internally conflicting exception priorities. Check quantity language literally: initial versus current stock, already consumed versus still to consume, ownership versus available inventory. Reject when either reading could change the answer. Tool requests need enough information to identify the target. Do not assume the longest or safest option is correct. reason is a short factual justification, at most 30 words. issue is empty if valid. Never rewrite the item."""


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_prices():
    # Confirmed provider listing 2026-09-26: weekends $0.15/$0.60 per M.
    # Use peak rates if a call could overlap a weekday peak window (180s timeout).
    now = dt.datetime.now(dt.timezone.utc)
    def peak(value):
        return value.weekday() < 5 and (1 <= value.hour < 4 or 6 <= value.hour < 10)
    multiplier = 1 if any(peak(now + dt.timedelta(seconds=s)) for s in (0, 180)) else .5
    return INPUT_PRICE * multiplier, OUTPUT_PRICE * multiplier


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum())


def signature(row):
    return hashlib.sha256(normalized(row["context"] + "\n" + row["question"]).encode()).hexdigest()


def historical_signatures():
    seen = set()
    rows = 0
    for path in (ROOT / "data").rglob("*.jsonl"):
        if OUT in path.parents or any(x in path.name for x in ("journal", "judgment", "rejection")):
            continue
        for row in read_jsonl(path):
            if isinstance(row, dict) and isinstance(row.get("context"), str) and isinstance(row.get("question"), str):
                seen.add(signature(row))
                rows += 1
    return seen, rows


def group_specs(pilot=False):
    groups = []
    # Batch/family boundaries are assigned before text generation. No batch crosses splits.
    for ci, category in enumerate(CATEGORIES):
        split_list = ["train"] * 35 + ["dev"] * (8 if ci % 2 == 0 else 7) + ["calibration"] * (2 if ci % 2 == 0 else 3) + ["final_test"] * 5
        random.Random(SEED + ci).shuffle(split_list)
        languages = ["ja"] * 30 + ["en"] * 10 + ["zh-Hans"] * 10
        random.Random(SEED + 100 + ci).shuffle(languages)
        for i in range(1 if pilot else 50):
            group_id = f"wc1_{'pilot_' + VERSION if pilot else 'main_' + VERSION}_{ci:02d}_{i:03d}"
            groups.append({"group_id": group_id, "category": category,
                           "language": (["ja"] * 6 + ["en"] * 2 + ["zh-Hans"] * 2)[ci] if pilot else languages[i],
                           "split": "pilot" if pilot else split_list[i], "count": 1 if pilot else 10,
                           "subskill": CATEGORIES[category][2][i % 5], "seed": SEED + ci * 1000 + i})
    random.Random(SEED).shuffle(groups)
    return groups


def item_specs(group, attempt, count):
    specs = []
    for j in range(count):
        rng = random.Random(group["seed"] + attempt * 100 + j)
        k = rng.choices([2, 4, 6, 8], weights=[10, 55, 25, 10])[0]
        simple = group["category"] in ("color_shape", "animals")
        tier = "short" if simple else rng.choices(["short", "medium", "long"], [25, 55, 20])[0]
        specs.append({**group, "id": f"{group['group_id']}_a{attempt}_{j:02d}", "choice_count": k,
                      "subskill": CATEGORIES[group["category"]][2][(j + attempt + group["seed"]) % 5],
                      "length_tier": tier, "conversation_json": group["category"] in ("tool_routing", "conversation_memory", "npc_social_quest"),
                      "diversity_seed": rng.randrange(10000000)})
    return specs


def generation_prompt(specs):
    guidance = {"short": "Concise: roughly 60-220 tokens including choices.",
                "medium": "Roughly 220-500 tokens including choices; integrate at least two facts.",
                "long": "Roughly 500-850 tokens including choices; integrate at least three separated facts. Stay below 1024."}
    visible = [{k: s[k] for k in ("id", "category", "language", "subskill", "choice_count", "conversation_json", "diversity_seed")} |
               {"category_instruction": CATEGORIES[s["category"]][1], "length": guidance[s["length_tier"]]} for s in specs]
    return json.dumps(visible, ensure_ascii=False)


def validate(raw, spec, counter):
    if not isinstance(raw, dict) or raw.get("id") != spec["id"]:
        raise ValueError("id_mismatch")
    raw = copy.deepcopy(raw)
    context_object = isinstance(raw.get("context"), dict)
    if context_object and spec["conversation_json"]:
        raw["context"] = json.dumps(raw["context"], ensure_ascii=False, separators=(",", ":"))
    for key in ("context", "question", "answer_explanation"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            raise ValueError("missing_" + key)
    row = {k: raw[k] for k in ("id", "context", "question", "choices", "answer_explanation")}
    ChoiceRequest.from_dict(row)
    choices = row["choices"]
    if len(choices) != spec["choice_count"] or [c["id"] for c in choices] != [f"c{i+1}" for i in range(len(choices))]:
        raise ValueError("choice_shape")
    if len({normalized(c["text"]) for c in choices}) != len(choices):
        raise ValueError("duplicate_choices")
    if raw.get("correct_choice_id") not in {c["id"] for c in choices}:
        raise ValueError("invalid_target")
    full = row["context"] + row["question"] + " ".join(c["text"] for c in choices)
    if not _language_ok(spec["language"], full):
        raise ValueError("language")
    if re.search(r"https?://|sk-[a-zA-Z0-9]{12,}|<<LABEL>>|<<SEP>>|<<EXAMPLE>>", full):
        raise ValueError("forbidden_text")
    if spec["conversation_json"]:
        messages = json.loads(row["context"]).get("messages")
        if not isinstance(messages, list) or len(messages) < 3 or any(not isinstance(m, dict) or m.get("role") not in ("user", "assistant", "system") or not isinstance(m.get("content"), str) or not m["content"].strip() for m in messages):
            raise ValueError("conversation_shape")
        if not {"user", "assistant"} <= {m["role"] for m in messages}:
            raise ValueError("conversation_roles")
        if messages[-1]["role"] != "user":
            raise ValueError("conversation_must_end_with_user")
    tokens = counter.count(row)
    if not 15 <= tokens <= 1024:
        raise ValueError("token_range")
    # Preserve answer identity through a deterministic full permutation.
    answer_text = next(c["text"] for c in choices if c["id"] == raw["correct_choice_id"])
    random.Random(spec["id"]).shuffle(choices)
    row["choices"] = [{"id": f"c{i+1}", "text": c["text"]} for i, c in enumerate(choices)]
    row.update(schema_version="1", group_id=spec["group_id"], domain=spec["category"], task_family="world_choice",
               language=spec["language"], split=spec["split"], source_model=MODEL, generation_spec=spec,
               input_tokens=tokens, target={"kind": "hard", "choice_id": next(c["id"] for c in row["choices"] if c["text"] == answer_text)},
               prompt_version=VERSION,
               review_status="deepseek_generated_unreviewed")
    if context_object:
        row["normalizations"] = ["conversation_object_to_json_string_without_content_changes"]
    return row


class BudgetExhausted(RuntimeError):
    pass


class BudgetClient:
    def __init__(self, output, cap):
        from openai import AsyncOpenAI
        self.output, self.cap = output, cap
        self.path = output / "api_journal.jsonl"
        journal = read_jsonl(self.path)
        spent, reserved, _, _ = journal_cost(journal)
        self.spent, self.reserved = spent, reserved
        self.active = 0
        self.responses = {r["batch_key"]: r for r in journal if r.get("event") == "response"}
        self.pending = {r["batch_key"] for r in journal if r.get("event") == "pending"}
        base_url = os.environ.get("ERABI_DATA_GEN_BASE_URL")
        api_key = os.environ.get("ERABI_DATA_GEN_API_KEY")
        if not base_url or not api_key:
            raise RuntimeError(
                "Set ERABI_DATA_GEN_BASE_URL and ERABI_DATA_GEN_API_KEY for an "
                "OpenAI-compatible endpoint."
            )
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=180,
            max_retries=0,
        )
        self.extended = any(r.get("event") == "second_tranche" for r in journal)

    async def call(self, kind, ids, system, prompt, max_tokens):
        key = hashlib.sha256((kind + VERSION + system + prompt).encode()).hexdigest()
        if key in self.responses:
            return self.responses[key]["payload"] if self.responses[key]["finish_reason"] == "stop" else {}
        if key in self.pending:
            return {}  # Ambiguous paid request is never automatically resubmitted.
        # UTF-8 byte count is a conservative input-token upper bound, including framing.
        input_price, output_price = current_prices()
        reserve = (len((system + prompt).encode("utf-8")) + 1024) * input_price + max_tokens * output_price
        total = PRIOR_USD + self.spent + self.reserved + reserve
        while total > self.cap:
            if not self.active:
                raise BudgetExhausted("budget_exhausted")
            # Let already-paid work finish and release unused token reservations.
            # A budget stop must not cancel every concurrent in-flight request.
            await asyncio.sleep(1)
            total = PRIOR_USD + self.spent + self.reserved + reserve
        if total > 5 and not self.extended:
            append_jsonl(self.path, {"event": "second_tranche", "reason": "5000 accepted rows not yet complete; previously authorized extra $5", "global_cap_usd": self.cap})
            self.extended = True
            print("BUDGET: initial cumulative $5 reached; using pre-authorized second tranche, absolute cap $10", flush=True)
        self.pending.add(key)
        self.reserved += reserve
        append_jsonl(self.path, {"event": "pending", "batch_key": key, "kind": kind, "ids": ids, "reserve_usd": reserve, "time": time.time()})
        self.active += 1
        try:
            response = await self.client.chat.completions.create(model=MODEL, messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}], response_format={"type": "json_object"}, temperature=0.7 if kind == "generate" else 0, max_tokens=max_tokens, reasoning_effort="low", extra_body={"thinking": {"type": "enabled"}})
            usage = response.usage
            if not usage:
                raise RuntimeError("missing_usage")
            cost = usage.prompt_tokens * input_price + usage.completion_tokens * output_price
            content = response.choices[0].message.content or ""
            try:
                payload = json.loads(content)
                if not isinstance(payload, dict):
                    payload = {"invalid_shape": True}
            except json.JSONDecodeError:
                payload = {"invalid_json": content}
            event = {"event": "response", "batch_key": key, "kind": kind, "ids": ids, "payload": payload,
                     "estimated_usd": cost, "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens,
                     "input_usd_per_token": input_price, "output_usd_per_token": output_price,
                     "usage_details": usage.model_dump(),
                     "response_model": response.model, "finish_reason": response.choices[0].finish_reason}
            append_jsonl(self.path, event)
            self.responses[key] = event
            self.spent += cost
            self.reserved -= reserve
            return payload if event["finish_reason"] == "stop" else {}
        except Exception as exc:
            # Error details may contain request internals; log only class/status.
            append_jsonl(self.path, {"event": "error", "batch_key": key, "error_type": type(exc).__name__, "http_status": getattr(exc, "status_code", None)})
            print(f"API outcome unresolved: {type(exc).__name__}; reserved ${reserve:.4f}", flush=True)
            return {}
        finally:
            self.active -= 1

    def report(self):
        return {"prior_conservative_usd": PRIOR_USD, "new_estimated_usd": round(self.spent, 8), "unresolved_reserved_usd": round(self.reserved, 8), "cumulative_conservative_usd": round(PRIOR_USD + self.spent + self.reserved, 8), "global_cap_usd": self.cap}


async def generate(args):
    OUT.mkdir(parents=True, exist_ok=True)
    if args.mode != "pilot":
        approval = json.loads((OUT / "pilot_review.json").read_text(encoding="utf-8"))
        if not approval.get("approved") or approval.get("prompt_sha256") != hashlib.sha256(SYSTEM.encode()).hexdigest():
            raise RuntimeError("Pilot review missing or prompt changed")
    save_json(OUT / f"prompt_{VERSION}.json", {"version": VERSION, "system": SYSTEM, "judge": JUDGE, "categories": CATEGORIES})
    counter = TokenCounter(TOKENIZER)
    seen, historical_rows = historical_signatures()
    seen.update(signature(r) for r in collect(args.mode == "pilot"))
    print(f"Historical duplicate screen: {historical_rows} rows", flush=True)
    client = BudgetClient(OUT, args.cap)
    groups = group_specs(args.mode == "pilot")
    if args.limit_groups:
        groups = groups[:args.limit_groups]
    sem = asyncio.Semaphore(args.workers)
    rejected = Counter()
    finished = 0

    async def run_group(group):
        nonlocal finished
        async with sem:
            path = OUT / "groups" / (group["group_id"] + ".json")
            path.parent.mkdir(exist_ok=True)
            cached_accepted_ids = set()
            if path.exists():
                cached = json.loads(path.read_text(encoding="utf-8"))
                cached_accepted_ids = {r["id"] for r in cached["accepted"]}
                if len(cached["accepted"]) >= group["count"]:
                    finished += 1
                    return
            accepted = []
            for attempt in range(args.attempts):
                needed = group["count"] - len(accepted)
                if needed <= 0:
                    break
                batch_count = min(needed, 5) if group["category"] in ("robot_fault", "resource_navigation", "rpg_survival", "world_rules") else needed
                specs = item_specs(group, attempt, batch_count)
                payload = await client.call("generate", [s["id"] for s in specs], SYSTEM, generation_prompt(specs), min(32000, 2000 * batch_count + 7000))
                raw_rows = payload.get("examples", [])
                raw_by_id = {r.get("id"): r for r in raw_rows if isinstance(r, dict)} if isinstance(raw_rows, list) else {}
                if len(specs) == 1 and isinstance(raw_rows, list) and len(raw_rows) == 1 and isinstance(raw_rows[0], dict) and raw_rows[0].get("id") != specs[0]["id"]:
                    # Single-item response has an unambiguous local identity; do not
                    # waste a correct example because the teacher invented an id.
                    raw_by_id = {specs[0]["id"]: {**raw_rows[0], "id": specs[0]["id"]}}
                    append_jsonl(OUT / "normalizations.jsonl", {"kind": "single_response_id", "id": specs[0]["id"], "response_id": raw_rows[0].get("id")})
                candidates = []
                for spec in specs:
                    try:
                        candidate = validate(raw_by_id.get(spec["id"]), spec, counter)
                        sig = signature(candidate)
                        if sig in seen:
                            # A resumed partial group may replay its own journaled rows.
                            if candidate["id"] not in cached_accepted_ids:
                                raise ValueError("duplicate_input")
                        seen.add(sig)
                        candidates.append(candidate)
                    except (ValueError, TypeError, KeyError, AttributeError) as exc:
                        rejected[str(exc)[:60]] += 1
                        append_jsonl(OUT / "rejections.jsonl", {"id": spec["id"], "stage": "local", "reason": str(exc)[:200]})
                if candidates:
                    blind = [{k: r[k] for k in ("id", "context", "question", "choices")} for r in candidates]
                    judged = await client.call("judge", [r["id"] for r in candidates], JUDGE, json.dumps(blind, ensure_ascii=False), min(22000, len(blind) * 1400 + 4000))
                    values = judged.get("judgments", [])
                    by_id = {j.get("id"): j for j in values if isinstance(j, dict)} if isinstance(values, list) else {}
                    for row in candidates:
                        j = by_id.get(row["id"], {})
                        append_jsonl(OUT / "judgments.jsonl", {"id": row["id"], **j})
                        if j.get("valid") is True and j.get("selected_choice_id") == row["target"]["choice_id"]:
                            row["review_status"] = "deepseek_generated_answer_blind_agreed_not_human_gold"
                            row["judge_reason"] = j.get("reason", "")
                            accepted.append(row)
                        else:
                            rejected["blind_disagreement_or_invalid"] += 1
                            append_jsonl(OUT / "rejections.jsonl", {"id": row["id"], "stage": "judge", "judgment": j, "row": row})
                save_json(path, {"group": group, "accepted": accepted, "attempts": attempt + 1})
            finished += 1
            print(f"{args.mode} groups={finished}/{len(groups)} {group['group_id']} accepted={len(accepted)}/{group['count']} cumulative=${PRIOR_USD+client.spent+client.reserved:.3f}", flush=True)

    async def bounded_group(group):
        try:
            await run_group(group)
        except BudgetExhausted:
            rejected["budget_stopped_groups"] += 1
            print(f"BUDGET_STOP group={group['group_id']}; existing in-flight requests will finish", flush=True)

    try:
        await asyncio.gather(*(bounded_group(g) for g in groups))
    finally:
        save_json(OUT / "cost_summary.json", client.report())
        await client.client.close()
    save_json(OUT / (args.mode + "_summary.json"), {"groups": len(groups), "rejections_this_process": dict(rejected), **client.report()})


def collect(pilot=False):
    rows = []
    for group in group_specs(pilot):
        path = OUT / "groups" / (group["group_id"] + ".json")
        if path.exists():
            rows.extend(json.loads(path.read_text(encoding="utf-8"))["accepted"])
    return rows


def snapshot_existing():
    paths = sorted(p for p in (ROOT / "data").rglob("*.jsonl") if OUT not in p.parents and ("sealed" in str(p).lower() or any(x in p.name.lower() for x in ("test", "eval", "valid", "dev", "calibration"))))
    path = OUT / "existing_evaluation_snapshot.json"
    current = {str(p.relative_to(ROOT)).replace("\\", "/"): digest(p) for p in paths}
    if path.exists():
        previous = json.loads(path.read_text(encoding="utf-8"))
        changed = [name for name, sha in previous.items() if current.get(name) != sha]
        if changed:
            raise RuntimeError(f"Existing evaluations changed: {changed}")
        if current.keys() != previous.keys():
            save_json(path, current)
    else:
        save_json(path, current)
    return len(current)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["pilot", "generate", "inspect"])
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--limit-groups", type=int, default=0)
    parser.add_argument("--cap", type=float, default=10.0)
    args = parser.parse_args()
    if not 1 <= args.workers <= 48 or not 1 <= args.attempts <= 6 or not PRIOR_USD < args.cap <= GLOBAL_CAP:
        parser.error("invalid workers, attempts or cap")
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Frozen evaluation files verified: {snapshot_existing()}", flush=True)
    if args.mode in ("pilot", "generate"):
        asyncio.run(generate(args))
    rows = collect(args.mode == "pilot")
    print(json.dumps({"accepted": len(rows), "categories": dict(Counter(r["domain"] for r in rows)), "splits": dict(Counter(r["split"] for r in rows))}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
