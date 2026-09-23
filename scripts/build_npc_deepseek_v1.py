"""Generate original Japanese NPC routing candidate data using DeepSeek only.

No Codex-authored example text is sent. The API key stays in the ignored local
key file. Spend is guarded against the previous practical-v1 ledger as well as
this corpus's own persisted ledger.
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
OUT = ROOT / "data" / "npc_deepseek_v1"
KEY_FILE = ROOT / ".env.orcarouter.local"
PREVIOUS_LEDGER = ROOT / "data" / "practical_v1" / "usage_ledger.json"
MODEL = "deepseek/deepseek-v4.1-flash"
PRICES = {"prompt": 0.30 / 1_000_000, "completion": 1.20 / 1_000_000}

ACTIONS = {
    "talk": "NPCが会話だけで答える",
    "web": "現実世界の最新情報をWeb検索する",
    "image_create": "新しいイラストを生成する",
    "video_create": "短い動画を生成する",
    "command": "許可された開発環境でコマンドを実行する",
    "screenshot": "現在のゲーム画面をスクリーンショット取得する",
    "image_analyze": "既に添付された画像を解析する",
    "game_state": "ゲーム状態APIで現在の所持品・位置・天候を調べる",
    "quest_log": "ゲームのクエスト記録APIで進行状況を調べる",
    "pathfind": "ゲーム内経路探索APIで通行可能な経路を調べる",
}

# Abstract routing contrasts only: the model invents every dialogue and fact.
PAIRS = [
    ("talk", "web"),
    ("screenshot", "image_analyze"),
    ("image_create", "video_create"),
    ("game_state", "quest_log"),
    ("game_state", "pathfind"),
    ("command", "talk"),
    ("web", "game_state"),
    ("quest_log", "talk"),
    ("image_analyze", "image_create"),
    ("pathfind", "talk"),
]
SETTINGS = {
    "train": ["floating market", "underground observatory", "desert caravan", "clockwork academy", "forest settlement", "snowbound outpost"],
    "dev": ["tidal monastery", "cavern railway", "orchard citadel"],
    "eval": ["skyship port", "volcanic archive", "coral capital"],
}
SYSTEM = (
    "You are DeepSeek generating original Japanese training candidates for a local action-routing classifier. "
    "Return JSON only with a groups array in the exact requested order. Invent all conversations, NPC names, "
    "fictional worlds, game states, and user utterances from scratch. Do not copy private transcripts, ChatGPT/Codex "
    "examples, public benchmarks, game dialogue, copyrighted passages, or real account details. "
    "A group contains exactly two variants that share a believable multi-turn situation but differ in one decisive "
    "fact or current player request; the two target actions must differ. Do not print the answer ID or an explicit "
    "answer explanation inside context or question. Context must include speaker-labeled NPC/player conversation and "
    "only facts visible to that NPC; latest player utterance belongs in question. Never claim a tool has already "
    "been called unless the spec explicitly needs an existing image attachment. Real-world current data needs Web, "
    "fictional current game state needs a game API, an attached image needs analysis, and an unavailable screenshot "
    "needs capture first. Commands must be benign and explicitly authorized in a sandbox. "
    "Return each variant as {context,question,target_choice_id}. No markdown."
)


def load_key() -> str:
    name, sep, value = KEY_FILE.read_text(encoding="utf-8").strip().partition("=")
    if name != "ORCAROUTER_API_KEY" or not sep or not value:
        raise ValueError("Missing ORCAROUTER_API_KEY in ignored local file")
    return value


def read_json(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def split_for(index: int) -> str:
    return "train" if index < 70 else "dev" if index < 85 else "eval"


def spec_for(index: int) -> dict:
    split = split_for(index)
    pair = PAIRS[index % len(PAIRS)]
    size = (2, 4, 6, 8, 10)[(index // len(PAIRS)) % 5]
    randomizer = random.Random(20260922 + index)
    others = [action for action in ACTIONS if action not in pair]
    randomizer.shuffle(others)
    choice_ids = list(pair) + others[: size - 2]
    randomizer.shuffle(choice_ids)
    return {
        "index": index,
        "split": split,
        "setting": SETTINGS[split][(index // len(PAIRS)) % len(SETTINGS[split])],
        "choice_ids": choice_ids,
        "targets": list(pair),
        "long": index % 10 == 9,
    }


def prompt_for(specs: list[dict]) -> str:
    compact = []
    for spec in specs:
        compact.append({
            "group_index": spec["index"],
            "setting_inspiration": spec["setting"],
            "choices": [{"id": action, "text": ACTIONS[action]} for action in spec["choice_ids"]],
            "variant_target_ids_in_order": spec["targets"],
            "length": (
                "Long natural multi-turn conversation: approximately 1200-1700 Japanese characters of context, "
                "12-20 turns with meaningful earlier facts, and a concise current question. Stay safely under "
                "2048 tokenizer tokens including choices. No filler repetition."
                if spec["long"] else
                "Natural multi-turn conversation: 4-8 turns, approximately 180-450 Japanese characters of context."
            ),
        })
    return (
        "Generate each group in order from these abstract specifications. Vary genres, player intents, "
        "NPC personalities, phrasing, and decisive details. Include plausible hard negatives among available choices. "
        "For the two variants of a group, preserve a recognizable shared history but change a decisive "
        "fact/current request so that only the specified target is appropriate. "
        + json.dumps(compact, ensure_ascii=False)
        + ' Return {"groups":[{"variants":[{"context":"...","question":"...","target_choice_id":"..."},...]}...]}.'
    )


def normalize(s: str) -> str:
    return " ".join(s.casefold().split())


def validated_pair(spec: dict, raw: dict, fingerprints: set[str]) -> list[dict]:
    variants = raw["variants"]
    if not isinstance(variants, list) or len(variants) != 2:
        raise ValueError("not exactly two variants")
    records = []
    new_fingerprints = []
    for variant_index, variant in enumerate(variants):
        context, question = variant["context"].strip(), variant["question"].strip()
        target = variant["target_choice_id"]
        if not context or not question or target != spec["targets"][variant_index]:
            raise ValueError("empty text or wrong target")
        speaker_lines = re.findall(r"(?m)^[^\n：:「]{1,30}(?:[：:]|「)", context)
        if not re.search(r"プレイヤー|Player", context, re.IGNORECASE) or len(speaker_lines) < 3:
            raise ValueError("missing multi-turn speaker labels")
        if len(context) + len(question) > 6500:
            raise ValueError("overlong text")
        choices = [{"id": action, "text": ACTIONS[action]} for action in spec["choice_ids"]]
        ChoiceRequest.from_dict({"context": context, "question": question, "choices": choices})
        fingerprint = hashlib.sha256((normalize(context) + "\n" + normalize(question)).encode()).hexdigest()
        if fingerprint in fingerprints or fingerprint in new_fingerprints:
            raise ValueError("duplicate context/question")
        new_fingerprints.append(fingerprint)
        records.append({
            "id": f"npcds_v1_{spec['index']:03d}_{variant_index}",
            "group_id": f"npcds_v1_{spec['index']:03d}",
            "split": spec["split"],
            "family": "npc_multiturn_tool_routing",
            "language": "ja",
            "context": context,
            "question": question,
            "choices": choices,
            "target": {"kind": "hard", "choice_id": target},
            "source_model": MODEL,
            "source_type": "original_synthetic",
            "review_status": "deepseek_generated_unreviewed",
            "generation_spec": {"index": spec["index"], "setting": spec["setting"], "long": spec["long"]},
        })
    fingerprints.update(new_fingerprints)
    return records


def generate(group_count: int, batch_size: int, total_budget: float) -> None:
    from openai import OpenAI

    OUT.mkdir(parents=True, exist_ok=True)
    previous = float(read_json(PREVIOUS_LEDGER, {})["estimated_peak_usd"])
    ledger_path = OUT / "usage_ledger.json"
    ledger = read_json(ledger_path, {"model": MODEL, "estimated_peak_usd": 0.0, "requests": []})
    all_path = OUT / "all.jsonl"
    rows = [json.loads(line) for line in all_path.read_text(encoding="utf-8").splitlines()] if all_path.exists() else []
    present = {row["group_id"] for row in rows}
    fingerprints = {hashlib.sha256((normalize(row["context"]) + "\n" + normalize(row["question"])).encode()).hexdigest() for row in rows}
    # Re-check already-paid raw responses after validation fixes; no second call.
    raw_path = OUT / "raw_responses.jsonl"
    recovered = 0
    if raw_path.exists():
        for line in raw_path.read_text(encoding="utf-8").splitlines():
            raw_response = json.loads(line)
            if raw_response["finish_reason"] != "stop":
                continue
            try:
                generated_groups = json.loads(raw_response["content"])["groups"]
            except (ValueError, KeyError, TypeError):
                continue
            if len(generated_groups) != len(raw_response["group_indices"]):
                continue
            for index, generated_group in zip(raw_response["group_indices"], generated_groups):
                group_id = f"npcds_v1_{index:03d}"
                if index >= group_count or group_id in present:
                    continue
                try:
                    pair = validated_pair(spec_for(index), generated_group, fingerprints)
                except (ValueError, KeyError, TypeError):
                    continue
                with all_path.open("a", encoding="utf-8") as handle:
                    for row in pair:
                        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows.extend(pair)
                present.add(group_id)
                recovered += 1
    if recovered:
        print(f"recovered_paid_groups={recovered}", flush=True)
    client = OpenAI(base_url="https://api.orcarouter.ai/v1", api_key=load_key(), timeout=120, max_retries=0)
    errors = Counter()
    for first in range(0, group_count, batch_size):
        specs = [spec_for(i) for i in range(first, min(first + batch_size, group_count)) if f"npcds_v1_{i:03d}" not in present]
        if not specs:
            continue
        # Long groups get an independent request to keep output small and auditable.
        batches = [[s] for s in specs if s["long"]]
        normal = [s for s in specs if not s["long"]]
        if normal:
            batches.insert(0, normal)
        for batch in batches:
            prompt = prompt_for(batch)
            max_tokens = 5800 if len(batch) == 1 and batch[0]["long"] else 7000
            reserve = (len(prompt) + len(SYSTEM)) * PRICES["prompt"] + max_tokens * PRICES["completion"]
            if previous + ledger["estimated_peak_usd"] + reserve > total_budget:
                print(f"BUDGET_STOP previous=${previous:.4f} new=${ledger['estimated_peak_usd']:.4f} cap=${total_budget:.2f}", flush=True)
                publish(rows, ledger, previous)
                return
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=max_tokens,
                extra_body={"thinking": {"type": "disabled"}},
            )
            usage = response.usage
            if usage is None:
                raise RuntimeError("No token usage; stop before any further paid request")
            cost = usage.prompt_tokens * PRICES["prompt"] + usage.completion_tokens * PRICES["completion"]
            ledger["estimated_peak_usd"] += cost
            ledger["requests"].append({
                "group_indices": [s["index"] for s in batch],
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "estimated_peak_usd": round(cost, 8),
                "response_model": response.model,
                "finish_reason": response.choices[0].finish_reason,
            })
            save_json(ledger_path, ledger)
            with (OUT / "raw_responses.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps({
                    "group_indices": [s["index"] for s in batch],
                    "response_model": response.model,
                    "finish_reason": response.choices[0].finish_reason,
                    "content": response.choices[0].message.content,
                }, ensure_ascii=False) + "\n")
            if response.choices[0].finish_reason != "stop":
                errors["truncated"] += len(batch)
                continue
            try:
                groups = json.loads(response.choices[0].message.content or "{}")["groups"]
                if not isinstance(groups, list) or len(groups) != len(batch):
                    raise ValueError("wrong group count")
            except (ValueError, KeyError, TypeError):
                errors["bad_json"] += len(batch)
                continue
            for spec, group in zip(batch, groups):
                try:
                    pair = validated_pair(spec, group, fingerprints)
                except (ValueError, KeyError, TypeError) as exc:
                    errors[str(exc)[:60]] += 1
                    print(f"reject_group={spec['index']} reason={type(exc).__name__}:{str(exc)[:80]}", flush=True)
                    continue
                with all_path.open("a", encoding="utf-8") as handle:
                    for row in pair:
                        handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows.extend(pair)
                present.add(pair[0]["group_id"])
            print(f"groups={len(present)}/{group_count} new_peak=${ledger['estimated_peak_usd']:.4f} errors={sum(errors.values())}", flush=True)
    publish(rows, ledger, previous)
    print(json.dumps({"records": len(rows), "groups": len(present), "previous_usd": previous, "new_usd": round(ledger["estimated_peak_usd"], 6), "errors": dict(errors)}, ensure_ascii=False))


def publish(rows: list[dict], ledger: dict, previous: float) -> None:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(ROOT / "runs/rc3_training/checkpoints/epoch_9"), local_files_only=True)
    lengths = {}
    groups_by_split = {split: set() for split in ("train", "dev", "eval")}
    all_groups: dict[str, list[dict]] = {}
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate record ID in raw corpus")
    for row in rows:
        formatted = "".join("<<LABEL>>" + c["text"] for c in row["choices"]) + "<<SEP>>" + row["question"] + row["context"]
        lengths[row["id"]] = len(tokenizer(formatted, truncation=False)["input_ids"])
        all_groups.setdefault(row["group_id"], []).append(row)
    for group_id, pair in all_groups.items():
        if len(pair) != 2 or len({row["split"] for row in pair}) != 1:
            raise ValueError(f"Invalid paired group: {group_id}")
    oversized_groups = {group_id for group_id, pair in all_groups.items() if any(lengths[row["id"]] > 2048 for row in pair)}
    selected_rows = [row for row in rows if row["group_id"] not in oversized_groups]
    for row in selected_rows:
        groups_by_split[row["split"]].add(row["group_id"])
    assert sum(len(groups) for groups in groups_by_split.values()) == len(set().union(*groups_by_split.values()))
    if len(all_groups) >= 100 and not 150 <= len(selected_rows) <= 250:
        raise ValueError("Full run has fewer than 150 or more than 250 usable records")
    manifest = {
        "status": "deepseek_generated_unreviewed_not_gold",
        "model_requested": MODEL,
        "split_policy": "Group indices 0-69 train, 70-84 dev, 85-99 eval; settings disjoint by split",
        "limitations": ["DeepSeek-proposed labels are not human-reviewed gold.", "Evaluation uses generated synthetic contexts; no real-player validity claim."],
        "previous_estimated_peak_usd": round(previous, 6),
        "new_estimated_peak_usd": round(ledger["estimated_peak_usd"], 6),
        "combined_estimated_peak_usd": round(previous + ledger["estimated_peak_usd"], 6),
        "token_lengths": {"min": min(lengths.values()) if lengths else 0, "max": max(lengths.values()) if lengths else 0, "over_512": sum(n > 512 for n in lengths.values()), "over_2048": sum(n > 2048 for n in lengths.values())},
        "oversized_groups_excluded_from_splits": sorted(oversized_groups),
        "raw_records": len(rows),
        "usable_records": len(selected_rows),
        "splits": {},
    }
    for split in ("train", "dev", "eval"):
        selected = [row for row in selected_rows if row["split"] == split]
        data = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected)
        (OUT / f"{split}.jsonl").write_bytes(data.encode("utf-8"))
        manifest["splits"][split] = {
            "records": len(selected),
            "groups": len(groups_by_split[split]),
            "sha256": hashlib.sha256(data.encode("utf-8")).hexdigest(),
            "target_counts": dict(Counter(row["target"]["choice_id"] for row in selected)),
        }
    save_json(OUT / "manifest.json", manifest)
    save_json(OUT / "token_audit.json", lengths)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group-count", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--total-budget-usd", type=float, default=5.0)
    parser.add_argument("--publish-only", action="store_true", help="Rebuild splits and audits from accepted raw rows without an API call")
    args = parser.parse_args()
    if not 1 <= args.group_count <= 100 or not 1 <= args.batch_size <= 4 or not 0 < args.total_budget_usd <= 5.0:
        raise ValueError("group-count 1..100, batch-size 1..4, total budget at most $5")
    if args.publish_only:
        rows = [json.loads(line) for line in (OUT / "all.jsonl").read_text(encoding="utf-8").splitlines()]
        ledger = read_json(OUT / "usage_ledger.json", {})
        previous = float(read_json(PREVIOUS_LEDGER, {})["estimated_peak_usd"])
        publish(rows, ledger, previous)
        return
    generate(args.group_count, args.batch_size, args.total_budget_usd)


if __name__ == "__main__":
    main()
