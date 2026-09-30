"""Evaluate stock Laya on the fixed Decision Mix V2 final test."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import statistics
import subprocess
import sys
import threading
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "decision_mix_v2" / "combined_final_test.jsonl"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def percentile(values: list[float], q: float) -> float:
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo = int(pos)
    frac = pos - lo
    return values[lo] if lo + 1 == len(values) else values[lo] * (1 - frac) + values[lo + 1] * frac


def gpu_snapshot() -> dict | None:
    try:
        line = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,temperature.gpu,clocks.sm,power.draw,utilization.gpu",
             "--format=csv,noheader,nounits"], check=True, capture_output=True, text=True, timeout=5
        ).stdout.splitlines()[0]
        vals = [float(value.strip()) for value in line.split(",")]
        return dict(zip(("memory_used_mib", "temperature_c", "sm_clock_mhz", "power_w", "utilization_percent"), vals))
    except (FileNotFoundError, IndexError, ValueError, subprocess.SubprocessError):
        return None


def metric_block(rows: list[dict]) -> dict:
    if not rows:
        return {"count": 0, "correct_count": 0, "accuracy": None, "mean_nll": None, "mean_brier": None}
    nll = 0.0
    brier = 0.0
    for row in rows:
        probabilities = row["probabilities"]
        target = row["target"]
        target_p = max(float(probabilities.get(target, 0.0)), 1e-12)
        nll -= math.log(target_p)
        brier += sum((float(probabilities.get(cid, 0.0)) - (cid == target)) ** 2 for cid in row["choice_ids"])
    correct = sum(bool(row["correct"]) for row in rows)
    return {
        "count": len(rows), "correct_count": correct, "accuracy": correct / len(rows),
        "mean_nll": nll / len(rows), "mean_brier": brier / len(rows),
    }


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
        "by_family": family,
        "by_language": language,
        "canonical_group_all_correct": {
            "groups": len(groups), "correct_groups": sum(all(values) for values in groups.values()),
            "rate": sum(all(values) for values in groups.values()) / len(groups),
        },
        "uniform_random_expected_accuracy": statistics.mean(1 / len(row["choice_ids"]) for row in rows),
        "longest_choice_baseline_accuracy": sum(row["target"] in row["longest_choice_ids"] for row in rows) / len(rows),
        "model_on_gold_longest": metric_block(longest),
        "model_on_gold_not_longest": metric_block(non_longest),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--warmup", type=int, default=8)
    parser.add_argument("--max-len", type=int, default=1024)
    parser.add_argument("--head-max-len", type=int, default=512)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True)

    import torch
    import transformers
    from laya import Router, __version__ as laya_version

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.limit:
        rows = rows[:args.limit]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Empty input or duplicate ids")
    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")

    before = gpu_snapshot()
    load_started = time.perf_counter()
    router = Router(device=args.device, default="multilingual", revision="reviewed", max_loaded=2,
                    auto_task_detection=False)
    router.preload(["english", "multilingual"])
    torch.cuda.synchronize()
    load_seconds = time.perf_counter() - load_started
    after_load = gpu_snapshot()

    requests = []
    audits = []
    for row in rows:
        questions = {"answer": {"type": "choice", "instructions": row["question"],
                                "criteria": {choice["id"]: choice["text"] for choice in row["choices"]}}}
        route = router.route(row["context"], questions)
        agent = router.load(route["model"])
        internal = {"answer": agent._to_internal(questions["answer"])}
        capped = agent._encode_state(row["context"], ["answer"], internal,
                                     max_len=args.max_len, head_max_len=args.head_max_len)[0]
        full = agent._encode_state(row["context"], ["answer"], internal,
                                   max_len=8192, head_max_len=2048)[0]
        raw_option_tokens = [len(agent.tok(" " + choice["text"], add_special_tokens=False)["input_ids"])
                             for choice in row["choices"]]
        option_stats = capped.get("options", {})
        audits.append({
            "id": row["id"], "model": route["model"], "capped_tokens": len(capped["ids"]),
            "full_tokens": len(full["ids"]), "truncated": len(capped["ids"]) < len(full["ids"]),
            "raw_option_tokens": raw_option_tokens,
            "options_over_48_token_cap": sum(value > 48 for value in raw_option_tokens),
            "options": option_stats,
        })
        requests.append((questions, route["model"]))

    for row, (questions, _) in zip(rows[: args.warmup], requests[: args.warmup]):
        router.predict(row["context"], questions, max_len=args.max_len, head_max_len=args.head_max_len)
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()

    samples: list[dict] = []
    stop = threading.Event()
    def collect() -> None:
        while not stop.wait(0.5):
            sample = gpu_snapshot()
            if sample:
                samples.append(sample)
    sampler = threading.Thread(target=collect, daemon=True)
    sampler.start()

    records = []
    run_started = time.perf_counter()
    for index, (row, (questions, routed_model)) in enumerate(zip(rows, requests), 1):
        torch.cuda.synchronize()
        started = time.perf_counter()
        response = router.predict(row["context"], questions, max_len=args.max_len,
                                  head_max_len=args.head_max_len)
        torch.cuda.synchronize()
        elapsed_ms = (time.perf_counter() - started) * 1000
        answer = response["answers"]["answer"]
        probabilities = {str(key): float(value) for key, value in answer["probabilities"].items()}
        choice_ids = [choice["id"] for choice in row["choices"]]
        if set(probabilities) != set(choice_ids):
            raise RuntimeError(f"{row['id']}: Laya candidate IDs changed: {sorted(probabilities)}")
        prediction = str(answer["choice"])
        if prediction not in choice_ids:
            raise RuntimeError(f"{row['id']}: unknown prediction {prediction}")
        lengths = [len(choice["text"]) for choice in row["choices"]]
        max_length = max(lengths)
        records.append({
            "id": row["id"], "canonical_group_id": row["canonical_group_id"],
            "domain": row["domain"], "language": row["language"],
            "target": row["target"]["choice_id"], "prediction": prediction,
            "correct": prediction == row["target"]["choice_id"],
            "choice_ids": choice_ids, "probabilities": probabilities,
            "longest_choice_ids": [choice_ids[i] for i, value in enumerate(lengths) if value == max_length],
            "input_tokens": response.get("usage", {}).get("input_tokens"),
            "model": response.get("routing", {}).get("model", routed_model), "elapsed_ms": elapsed_ms,
        })
        if index % 50 == 0 or index == len(rows):
            print(f"laya {index}/{len(rows)}", flush=True)
    wall_seconds = time.perf_counter() - run_started
    stop.set()
    sampler.join(timeout=5)
    final_sample = gpu_snapshot()
    if final_sample:
        samples.append(final_sample)

    runtime = {}
    for name in router.loaded:
        agent = router.load(name)
        runtime[name] = {
            "device": str(agent.device), "dtype": str(agent.dtype),
            "parameter_dtype": str(next(agent.model.parameters()).dtype),
            "amp_enabled": bool(agent.amp_enabled), "compiled": bool(getattr(agent, "_compiled", False)),
            "fast_path_enabled": agent._fast is not None,
        }
    latencies = [row["elapsed_ms"] for row in records]
    sample_summary = {
        key: {"min": min(row[key] for row in samples), "median": statistics.median(row[key] for row in samples),
              "max": max(row[key] for row in samples)}
        for key in samples[0]
    } if samples else {}
    result = {
        "format": "decision-mix-v2-laya-eval-v1", "status": "complete",
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "input": str(args.input.resolve()), "input_sha256": sha256(args.input), "rows": len(rows),
        "source": {"repository": "https://github.com/NandhaKishorM/laya",
                   "git_commit": "9d955671415fc19f069b9cc998928075c1f255ec",
                   "laya_version": laya_version, "revision": "reviewed"},
        "environment": {"python": sys.version, "torch": torch.__version__,
                        "torch_cuda_runtime": torch.version.cuda, "transformers": transformers.__version__},
        "conditions": {"device": args.device, "warmup": args.warmup, "batch_size": 1,
                       "max_len": args.max_len, "head_max_len": args.head_max_len,
                       "candidate_order": "original", "training_on_decision_mix_v2": False},
        "runtime": runtime, "engine_initialization_seconds": load_seconds,
        "metrics": summarize(records),
        "latency": {"wall_seconds": wall_seconds, "requests_per_second": len(records) / wall_seconds,
                    "mean_ms": statistics.mean(latencies), "p50_ms": percentile(latencies, .5),
                    "p95_ms": percentile(latencies, .95)},
        "input_audit": {"truncated_rows": sum(row["truncated"] for row in audits),
                        "option_cap_hit_rows": sum(row["options_over_48_token_cap"] > 0 for row in audits),
                        "option_cap_hit_options": sum(row["options_over_48_token_cap"] for row in audits),
                        "collapsed_option_rows": sum(
                            row["options"].get("options_distinct", 0) < row["options"].get("options", 0)
                            for row in audits),
                        "route_counts": dict(Counter(row["model"] for row in audits))},
        "gpu": {"before": before, "after_load": after_load,
                "torch_peak_allocated_mib": torch.cuda.max_memory_allocated() / 1024**2,
                "torch_peak_reserved_mib": torch.cuda.max_memory_reserved() / 1024**2,
                "whole_device_samples": sample_summary,
                "caveat": "nvidia-smi is whole-device usage and may include unrelated processes."},
        "label_note": "Synthetic DeepSeek generator plus answer-blind same-family judge; provisional, not human gold.",
        "records": records, "audits": audits,
    }
    (args.output_dir / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"metrics": result["metrics"], "latency": result["latency"],
                      "input_audit": result["input_audit"], "gpu": result["gpu"]},
                     ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
