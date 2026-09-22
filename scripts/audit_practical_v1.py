"""Audit and package the DeepSeek-generated practical-choice corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from erabi.schema import ChoiceRequest
from build_practical_v1 import _language_ok


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "practical_v1"
MODEL_PATH = ROOT / "release" / "rc3" / "model"
MODEL = "deepseek/deepseek-v4.1-flash"


def load_records() -> list[dict]:
    path = OUTPUT / "all.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if any(record.get("review_status") != "teacher_proposed_unreviewed" for record in records):
        for record in records:
            record["review_status"] = "teacher_proposed_unreviewed"
        path.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records), encoding="utf-8")
    return records


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(records: list[dict]) -> dict:
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH), local_files_only=True)
    seen_ids: set[str] = set()
    signatures: dict[str, str] = {}
    errors: list[str] = []
    lengths: list[int] = []
    by_split = Counter()
    by_language = Counter()
    by_family = Counter()
    by_cell = Counter()
    by_target = defaultdict(Counter)
    math_specs: dict[str, set[tuple[int, int, str]]] = defaultdict(set)
    language_mismatch: list[str] = []
    for record in records:
        rid = record["id"]
        split = record["split"]
        family = record["family"]
        language = record["language"]
        by_split[split] += 1
        by_language[language] += 1
        by_family[family] += 1
        by_cell[(split, family, language)] += 1
        by_target[(family, split)][record["target"]["choice_id"]] += 1
        if rid in seen_ids:
            errors.append(f"duplicate_id:{rid}")
        seen_ids.add(rid)
        signature = " ".join((record["context"] + " " + record["question"]).casefold().split())
        if signature in signatures:
            errors.append(f"duplicate_text:{rid}:{signatures[signature]}")
        signatures[signature] = rid
        if record["group_id"] != rid:
            errors.append(f"group_id:{rid}")
        if not _language_ok(language, record["context"] + " " + record["question"]):
            language_mismatch.append(rid)
        try:
            ChoiceRequest.from_dict(record)
        except ValueError as exc:
            errors.append(f"schema:{rid}:{exc}")
        if record["target"]["choice_id"] not in {choice["id"] for choice in record["choices"]}:
            errors.append(f"target:{rid}")
        count = len(tokenizer(record["question"] + " " + record["context"], add_special_tokens=True, truncation=False)["input_ids"])
        count = max([count] + [len(tokenizer(c["text"], add_special_tokens=True, truncation=False)["input_ids"]) for c in record["choices"]])
        lengths.append(count)
        if count > 512:
            errors.append(f"tokens:{rid}:{count}")
        if family == "json_log_routing":
            try:
                parsed = json.loads(record["context"])
                if not isinstance(parsed.get("messages"), list):
                    errors.append(f"json_log:{rid}")
            except (ValueError, AttributeError):
                errors.append(f"json_log:{rid}")
        if family == "everyday_arithmetic":
            spec = record["generation_spec"]
            a, b, op = spec["a"], spec["b"], spec["operation"]
            math_specs[split].add((a, b, op))
            answer = {"add": a + b, "subtract": a - b, "multiply": a * b}[op]
            target = next((c for c in record["choices"] if c["id"] == record["target"]["choice_id"]), None)
            if not target or target["text"] != str(answer):
                errors.append(f"math_oracle:{rid}")
    math_overlaps = {
        f"{left}__{right}": len(math_specs[left] & math_specs[right])
        for left, right in (("train", "dev"), ("train", "eval_candidate"), ("dev", "eval_candidate"))
    }
    return {
        "records": len(records),
        "by_split": dict(sorted(by_split.items())),
        "by_language": dict(sorted(by_language.items())),
        "by_family": dict(sorted(by_family.items())),
        "cell_counts": {"|".join(k): v for k, v in sorted(by_cell.items())},
        "target_balance": {"|".join(k): dict(v) for k, v in sorted(by_target.items())},
        "max_tokens": max(lengths, default=0),
        "p95_tokens": sorted(lengths)[int(len(lengths) * .95)] if lengths else 0,
        "over_512": sum(n > 512 for n in lengths),
        "arithmetic_spec_overlaps": math_overlaps,
        "language_mismatch": language_mismatch,
        "errors": errors,
    }


def judge_records(records: list[dict], budget_usd: float, all_splits: bool) -> None:
    """Second, answer-blind teacher pass; agreement is not human gold."""
    from openai import OpenAI

    key_line = (ROOT / ".env.orcarouter.local").read_text(encoding="utf-8").strip()
    key_name, separator, key = key_line.partition("=")
    if key_name != "ORCAROUTER_API_KEY" or not separator:
        raise ValueError("Local OrcaRouter key unavailable")
    client = OpenAI(base_url="https://api.orcarouter.ai/v1", api_key=key, timeout=90, max_retries=0)
    ledger_path = OUTPUT / "usage_ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    target_records = records if all_splits else [r for r in records if r["split"] == "eval_candidate"]
    result_path = OUTPUT / ("all_judgments.jsonl" if all_splits else "eval_judgments.jsonl")
    judged = {json.loads(line)["id"] for line in result_path.read_text(encoding="utf-8").splitlines()} if result_path.exists() else set()
    for start in range(0, len(target_records), 8):
        batch = [r for r in target_records[start : start + 8] if r["id"] not in judged]
        if not batch:
            continue
        visible = [{"id": r["id"], "context": r["context"], "question": r["question"], "choices": r["choices"]} for r in batch]
        prompt = (
            "Independently solve each choice question from its context. Do not assume any teacher label. "
            "For tool use, prefer no_tool when the answer is already explicit; use a tool only when the requested information genuinely requires it. "
            "Return JSON {\"answers\":[{\"id\":...,\"choice_id\":...,\"ambiguous\":true/false,\"reason\":...}]} "
            "in the same order. If multiple options are defensible, set ambiguous=true. "
            + json.dumps(visible, ensure_ascii=False)
        )
        max_tokens = 1800
        reserve = len(prompt) * .30 / 1_000_000 + max_tokens * 1.20 / 1_000_000
        if ledger["estimated_peak_usd"] + reserve > budget_usd:
            raise RuntimeError("Judge preflight would exceed budget")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "Output only valid JSON. Solve from the visible input; do not invent missing facts."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            extra_body={"thinking": {"type": "disabled"}},
        )
        usage = response.usage
        if not usage:
            raise RuntimeError("Judge response omitted usage")
        estimated = usage.prompt_tokens * .30 / 1_000_000 + usage.completion_tokens * 1.20 / 1_000_000
        ledger["estimated_peak_usd"] += estimated
        ledger["requests"].append({"kind": "answer_blind_judge", "response_model": response.model, "prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens, "estimated_peak_usd": round(estimated, 8), "finish_reason": response.choices[0].finish_reason})
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if response.choices[0].finish_reason != "stop":
            continue
        try:
            answers = json.loads(response.choices[0].message.content or "{}")["answers"]
        except (ValueError, KeyError, TypeError):
            continue
        answer_by_id = {item.get("id"): item for item in answers if isinstance(item, dict)}
        with result_path.open("a", encoding="utf-8") as handle:
            for record in batch:
                item = answer_by_id.get(record["id"])
                if not item:
                    continue
                row = {
                    "id": record["id"], "teacher_target": record["target"]["choice_id"],
                    "blind_judge_target": item.get("choice_id"), "ambiguous": bool(item.get("ambiguous", True)),
                    "agree": item.get("choice_id") == record["target"]["choice_id"] and not bool(item.get("ambiguous", True)),
                    "reason": str(item.get("reason", ""))[:300],
                }
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"judge {min(start + 8, len(target_records))}/{len(target_records)} peak_estimate=${ledger['estimated_peak_usd']:.4f}", flush=True)


def package(records: list[dict], report: dict) -> None:
    def packaged(record: dict) -> dict:
        result = dict(record)
        result["review_status"] = "same_model_blind_agreement_unreviewed"
        # Preserve semantic tool IDs. Reassign generic c1..c4 IDs after shuffling
        # so both target ID and answer position lose the generator's bias.
        result["choices"] = [dict(choice) for choice in record["choices"]]
        result["target"] = dict(record["target"])
        seed = int.from_bytes(hashlib.sha256(record["id"].encode()).digest()[:8], "big")
        rng = random.Random(seed)
        rng.shuffle(result["choices"])
        if all(choice["id"].startswith("c") and choice["id"][1:].isdigit() for choice in result["choices"]):
            for index, choice in enumerate(result["choices"]):
                if choice["id"] == record["target"]["choice_id"]:
                    result["target"]["choice_id"] = f"c{index + 1}"
                choice["id"] = f"c{index + 1}"
        return result

    train_math = {
        (r["generation_spec"]["a"], r["generation_spec"]["b"], r["generation_spec"]["operation"])
        for r in records if r["split"] == "train" and r["family"] == "everyday_arithmetic"
    }
    excluded = [
        r["id"] for r in records
        if r["split"] != "train" and r["family"] == "everyday_arithmetic"
        and (r["generation_spec"]["a"], r["generation_spec"]["b"], r["generation_spec"]["operation"]) in train_math
    ]
    report["packaging_excluded_train_math_overlap"] = excluded
    excluded.extend(report["language_mismatch"])
    all_judgments_path = OUTPUT / "all_judgments.jsonl"
    if all_judgments_path.exists():
        all_judgments = [json.loads(line) for line in all_judgments_path.read_text(encoding="utf-8").splitlines()]
        accepted_by_judge = {item["id"] for item in all_judgments if item["agree"]}
        report["all_blind_judge"] = {
            "judged": len(all_judgments),
            "agreed_unambiguous": sum(item["agree"] for item in all_judgments),
            "packaging_accepted": len(accepted_by_judge),
            "note": "Same-provider answer-blind check, not human gold",
        }
    else:
        accepted_by_judge = {r["id"] for r in records}
    packaged_rows = {}
    for split in ("train", "dev", "eval_candidate"):
        path = OUTPUT / f"{split}.jsonl"
        rows = [packaged(r) for r in records if r["split"] == split and r["id"] not in excluded and r["id"] in accepted_by_judge]
        packaged_rows[split] = rows
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    report["packaged_by_split"] = {split: len(rows) for split, rows in packaged_rows.items()}
    report["packaged_by_cell"] = {
        "|".join(key): count
        for key, count in sorted(Counter((r["split"], r["family"], r["language"]) for rows in packaged_rows.values() for r in rows).items())
    }
    report["packaged_generic_target_ids"] = dict(sorted(Counter(
        r["target"]["choice_id"] for rows in packaged_rows.values() for r in rows
        if r["target"]["choice_id"].startswith("c") and r["target"]["choice_id"][1:].isdigit()
    ).items()))
    judgments_path = OUTPUT / "eval_judgments.jsonl"
    if judgments_path.exists():
        judgments = [json.loads(line) for line in judgments_path.read_text(encoding="utf-8").splitlines()]
        report["blind_judge"] = {
            "judged": len(judgments),
            "agreed_unambiguous": sum(item["agree"] for item in judgments),
            "disagreed_or_ambiguous": [item["id"] for item in judgments if not item["agree"]],
            "note": "Same-provider answer-blind check, not independent human gold validation",
        }
        accepted_ids = ({item["id"] for item in judgments if item["agree"]} & accepted_by_judge) - set(excluded)
        (OUTPUT / "eval_teacher_agreed.jsonl").write_text(
            "".join(json.dumps(packaged(r), ensure_ascii=False) + "\n" for r in records if r["id"] in accepted_ids), encoding="utf-8"
        )
    ledger = json.loads((OUTPUT / "usage_ledger.json").read_text(encoding="utf-8"))
    report["estimated_peak_usd"] = ledger["estimated_peak_usd"]
    report["api_requests"] = len(ledger["requests"])
    report["sha256"] = {path.name: sha256(path) for path in OUTPUT.glob("*.jsonl")}
    (OUTPUT / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge-eval", action="store_true")
    parser.add_argument("--judge-all", action="store_true")
    parser.add_argument("--budget-usd", type=float, default=5.0)
    args = parser.parse_args()
    records = load_records()
    report = audit(records)
    if args.judge_eval or args.judge_all:
        judge_records(records, args.budget_usd, all_splits=args.judge_all)
    package(records, report)
    print(json.dumps({k: report[k] for k in ("records", "by_split", "by_family", "by_language", "max_tokens", "over_512", "arithmetic_spec_overlaps", "estimated_peak_usd")}, ensure_ascii=True, indent=2))
    if report["errors"]:
        raise SystemExit(f"Audit found {len(report['errors'])} structural errors")


if __name__ == "__main__":
    main()
