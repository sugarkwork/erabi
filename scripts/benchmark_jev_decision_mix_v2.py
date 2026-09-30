"""Evaluate OrcaRouter Jev on the fixed Decision Mix V2 final test."""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import os
import statistics
import threading
import time
from collections import Counter
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "runs" / "decision_mix_v2_finetune_20260930" / "filtered_final.jsonl"
ENDPOINT = "https://api.orcarouter.ai/v1/systemone"
MODEL = "typesafe/jev-1.13"
PRICE_PER_M_INPUT = 0.042
PRICE_PER_M_OUTPUT_CONSERVATIVE = 0.042


def load_key() -> str:
    key = os.environ.get("ORCAROUTER_API_KEY")
    if key:
        return key
    for path in (ROOT / ".env.orcarouter.local", ROOT / ".env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("ORCAROUTER_API_KEY="):
                value = line.split("=", 1)[1].strip()
                if value:
                    return value
    raise RuntimeError("ORCAROUTER_API_KEY is unavailable")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metric_block(rows: list[dict]) -> dict:
    if not rows:
        return {"count": 0, "correct_count": 0, "accuracy": None, "mean_nll": None, "mean_brier": None}
    nll = 0.0
    brier = 0.0
    for row in rows:
        probabilities = row["probabilities"]
        target = row["target"]
        nll -= math.log(max(float(probabilities.get(target, 0.0)), 1e-12))
        brier += sum((float(probabilities.get(cid, 0.0)) - (cid == target)) ** 2 for cid in row["choice_ids"])
    correct = sum(bool(row["correct"]) for row in rows)
    return {"count": len(rows), "correct_count": correct, "accuracy": correct / len(rows),
            "mean_nll": nll / len(rows), "mean_brier": brier / len(rows)}


def summarize(rows: list[dict]) -> dict:
    families = sorted({row["domain"] for row in rows})
    family = {name: metric_block([row for row in rows if row["domain"] == name]) for name in families}
    languages = sorted({row["language"] for row in rows})
    language = {name: metric_block([row for row in rows if row["language"] == name]) for name in languages}
    groups: dict[str, list[bool]] = {}
    for row in rows:
        groups.setdefault(row["canonical_group_id"], []).append(bool(row["correct"]))
    longest = [row for row in rows if row["target"] in row["longest_choice_ids"]]
    non_longest = [row for row in rows if row["target"] not in row["longest_choice_ids"]]
    return {
        "overall": metric_block(rows),
        "family_macro_accuracy": statistics.mean(item["accuracy"] for item in family.values()),
        "by_family": family, "by_language": language,
        "canonical_group_all_correct": {"groups": len(groups),
            "correct_groups": sum(all(values) for values in groups.values()),
            "rate": sum(all(values) for values in groups.values()) / len(groups)},
        "uniform_random_expected_accuracy": statistics.mean(1 / len(row["choice_ids"]) for row in rows),
        "longest_choice_baseline_accuracy": len(longest) / len(rows),
        "model_on_gold_longest": metric_block(longest),
        "model_on_gold_not_longest": metric_block(non_longest),
    }


def call_one(row: dict, key: str, timeout: float, attempts: int) -> dict:
    payload = {
        "model": MODEL,
        "state": row["context"],
        "questions": {"answer": {"type": "choice", "instructions": row["question"],
                                  "criteria": {choice["id"]: choice["text"] for choice in row["choices"]}}},
    }
    error = None
    for attempt in range(1, attempts + 1):
        started = time.perf_counter()
        try:
            response = requests.post(ENDPOINT, headers={"Authorization": f"Bearer {key}"},
                                     json=payload, timeout=timeout)
            if response.status_code == 429 or response.status_code >= 500:
                raise RuntimeError(f"retryable HTTP {response.status_code}")
            response.raise_for_status()
            body = response.json()
            answer = body["answers"]["answer"]
            choice_ids = [choice["id"] for choice in row["choices"]]
            prediction = str(answer["choice"])
            probabilities = {str(cid): float(value) for cid, value in answer["probabilities"].items()}
            if prediction not in choice_ids or set(probabilities) != set(choice_ids):
                raise ValueError("candidate IDs changed")
            if any(not math.isfinite(value) or value < 0 for value in probabilities.values()):
                raise ValueError("invalid probability")
            if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=0.02):
                raise ValueError("probabilities do not sum to one")
            lengths = [len(choice["text"]) for choice in row["choices"]]
            maximum = max(lengths)
            usage = body.get("usage", {})
            return {
                "id": row["id"], "canonical_group_id": row["canonical_group_id"],
                "domain": row["domain"], "language": row["language"],
                "target": row["target"]["choice_id"], "prediction": prediction,
                "correct": prediction == row["target"]["choice_id"], "choice_ids": choice_ids,
                "probabilities": probabilities,
                "longest_choice_ids": [choice_ids[i] for i, value in enumerate(lengths) if value == maximum],
                "confidence": answer.get("confidence"), "served_model": body.get("model"),
                "input_tokens": int(usage.get("input_tokens", 0)),
                "output_tokens": int(usage.get("output_tokens", 0)),
                "elapsed_ms": (time.perf_counter() - started) * 1000, "attempt": attempt,
            }
        except (requests.RequestException, ValueError, KeyError, TypeError, RuntimeError) as exc:
            error = str(exc)
            if attempt < attempts:
                time.sleep(min(2 ** (attempt - 1), 4))
    raise RuntimeError(f"{row['id']}: {error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    if not 1 <= args.workers <= 16:
        raise ValueError("workers must be 1..16")
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[:args.limit]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("empty input or duplicate IDs")
    key = load_key()
    args.output_dir.mkdir(parents=True)
    started_at = dt.datetime.now(dt.timezone.utc).isoformat()
    run_started = time.perf_counter()
    records = []
    lock = threading.Lock()
    journal = args.output_dir / "predictions.jsonl"
    with journal.open("x", encoding="utf-8") as handle:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(call_one, row, key, args.timeout, args.attempts): row["id"] for row in rows}
            for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
                record = future.result()
                records.append(record)
                with lock:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                    handle.flush()
                if completed % 25 == 0 or completed == len(rows):
                    print(f"jev {completed}/{len(rows)}", flush=True)
    wall_seconds = time.perf_counter() - run_started
    records.sort(key=lambda row: row["id"])
    input_tokens = sum(row["input_tokens"] for row in records)
    output_tokens = sum(row["output_tokens"] for row in records)
    conservative_cost = (input_tokens * PRICE_PER_M_INPUT + output_tokens * PRICE_PER_M_OUTPUT_CONSERVATIVE) / 1_000_000
    latencies = [row["elapsed_ms"] for row in records]
    result = {
        "format": "decision-mix-v2-jev-eval-v1", "status": "complete", "started_at": started_at,
        "input": str(args.input.resolve()), "input_sha256": sha256(args.input), "rows": len(records),
        "endpoint": ENDPOINT, "requested_model": MODEL,
        "served_models": dict(Counter(row["served_model"] for row in records)),
        "conditions": {"workers": args.workers, "timeout_seconds": args.timeout,
                       "candidate_order": "original", "training_on_decision_mix_v2": False},
        "metrics": summarize(records),
        "latency": {"wall_seconds": wall_seconds, "requests_per_second": len(records) / wall_seconds,
                    "mean_request_ms": statistics.mean(latencies), "median_request_ms": statistics.median(latencies),
                    "p95_request_ms": sorted(latencies)[int(.95 * (len(latencies) - 1))]},
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens,
                  "official_input_price_per_million_usd": PRICE_PER_M_INPUT,
                  "conservative_output_price_per_million_usd": PRICE_PER_M_OUTPUT_CONSERVATIVE,
                  "conservative_estimated_cost_usd": conservative_cost},
        "attempt_counts": dict(Counter(row["attempt"] for row in records)),
        "label_note": "Synthetic DeepSeek generator plus answer-blind same-family judge; provisional, not human gold.",
        "records": records,
    }
    (args.output_dir / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("served_models", "metrics", "latency", "usage", "attempt_counts")},
                     ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
