"""Benchmark Laya on ERABI's exposed World Choice V1 reference test."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import statistics
import subprocess
import threading
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "world_choice_v1" / "final_test.jsonl"


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    fraction = position - lower
    if lower + 1 < len(ordered):
        return ordered[lower] * (1 - fraction) + ordered[lower + 1] * fraction
    return ordered[lower]


def gpu_snapshot() -> dict[str, float] | None:
    try:
        output = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=temperature.gpu,clocks.sm,power.draw,memory.used,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.splitlines()[0]
        temperature, clock, power, memory, utilization = (
            float(value.strip()) for value in output.split(",")
        )
        return {
            "temperature_c": temperature,
            "sm_clock_mhz": clock,
            "power_w": power,
            "device_memory_used_mib": memory,
            "utilization_percent": utilization,
        }
    except (FileNotFoundError, IndexError, ValueError, subprocess.SubprocessError):
        return None


def summarize_samples(samples: list[dict[str, float]]) -> dict:
    if not samples:
        return {}
    return {
        key: {
            "min": min(sample[key] for sample in samples),
            "median": statistics.median(sample[key] for sample in samples),
            "max": max(sample[key] for sample in samples),
        }
        for key in samples[0]
    }


def to_questions(row: dict) -> dict:
    return {
        "answer": {
            "type": "choice",
            "instructions": row["question"],
            "criteria": {choice["id"]: choice["text"] for choice in row["choices"]},
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--warmup", type=int, default=8)
    parser.add_argument("--max-len", type=int, default=1024)
    parser.add_argument("--head-max-len", type=int, default=512)
    parser.add_argument("--routing", choices=("routed", "multilingual"), default="routed")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True)

    import torch
    import transformers
    from laya import Router, __version__ as laya_version

    rows = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line]
    if args.limit is not None:
        rows = rows[: args.limit]
    if not rows:
        raise ValueError("No benchmark rows")

    use_cuda = args.device.startswith("cuda")
    if use_cuda and not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")
    if use_cuda:
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    before = gpu_snapshot() if use_cuda else None
    load_started = time.perf_counter()
    router = Router(device=args.device, default="multilingual", revision="reviewed", max_loaded=2)
    model_names = ["english", "multilingual"] if args.routing == "routed" else ["multilingual"]
    router.preload(model_names)
    if use_cuda:
        torch.cuda.synchronize()
    load_seconds = time.perf_counter() - load_started
    after_load = gpu_snapshot() if use_cuda else None

    # Audit the exact rendered Laya sequence at the shared 1,024-token cap. A second
    # 8,192-token encoding reveals whether that cap shortened the state.
    audits = []
    requests = []
    for row in rows:
        questions = to_questions(row)
        model_name = (
            router.route(row["context"], questions)["model"]
            if args.routing == "routed" else "multilingual"
        )
        agent = router.load(model_name)
        internal = {"answer": agent._to_internal(questions["answer"])}
        capped = agent._encode_state(
            row["context"], ["answer"], internal,
            max_len=args.max_len, head_max_len=args.head_max_len,
        )[0]
        full = agent._encode_state(
            row["context"], ["answer"], internal,
            max_len=8192, head_max_len=2048,
        )[0]
        audits.append({
            "id": row["id"],
            "capped_tokens": len(capped["ids"]),
            "full_tokens": len(full["ids"]),
            "truncated": len(capped["ids"]) < len(full["ids"]),
            "options": capped["options"],
            "model": model_name,
        })
        requests.append((row["context"], questions, model_name))

    for state, questions, model_name in requests[: args.warmup]:
        router.predict(
            state, questions, model=(model_name if args.routing == "multilingual" else None),
            max_len=args.max_len, head_max_len=args.head_max_len,
        )
    if use_cuda:
        torch.cuda.synchronize()

    samples: list[dict[str, float]] = []
    stop_sampling = threading.Event()

    def sample_gpu() -> None:
        while not stop_sampling.wait(1.0):
            sample = gpu_snapshot()
            if sample:
                samples.append(sample)

    sampler = threading.Thread(target=sample_gpu, daemon=True)
    if use_cuda:
        torch.cuda.reset_peak_memory_stats()
        sampler.start()

    records = []
    inference_started = time.perf_counter()
    for index, (row, (state, questions, model_name)) in enumerate(zip(rows, requests), 1):
        if use_cuda:
            torch.cuda.synchronize()
        started = time.perf_counter()
        response = router.predict(
            state, questions, model=(model_name if args.routing == "multilingual" else None),
            max_len=args.max_len, head_max_len=args.head_max_len,
        )
        if use_cuda:
            torch.cuda.synchronize()
        elapsed_ms = (time.perf_counter() - started) * 1000
        answer = response["answers"]["answer"]
        records.append({
            "id": row["id"],
            "target": row["target"]["choice_id"],
            "prediction": answer["choice"],
            "correct": answer["choice"] == row["target"]["choice_id"],
            "probabilities": answer["probabilities"],
            "answer_confidence": answer["answer_confidence"],
            "input_tokens": response["usage"]["input_tokens"],
            "model": response["routing"]["model"],
            "elapsed_ms": elapsed_ms,
        })
        if index % 100 == 0 or index == len(rows):
            print(f"laya: {index}/{len(rows)}", flush=True)
    inference_seconds = time.perf_counter() - inference_started

    if use_cuda:
        stop_sampling.set()
        sampler.join(timeout=6)
        final_snapshot = gpu_snapshot()
        if final_snapshot:
            samples.append(final_snapshot)

    latencies = [record["elapsed_ms"] for record in records]
    result = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": {
            "repository": "https://github.com/NandhaKishorM/laya",
            "git_commit": "9d955671415fc19f069b9cc998928075c1f255ec",
            "laya_version": laya_version,
            "checkpoints": model_names,
            "revision_policy": "reviewed",
        },
        "environment": {
            "python": __import__("sys").version,
            "torch": torch.__version__,
            "torch_cuda_runtime": torch.version.cuda,
            "transformers": transformers.__version__,
            "device": args.device,
        },
        "conditions": {
            "dataset": str(DATA),
            "rows": len(rows),
            "warmup": args.warmup,
            "batch_size": 1,
            "max_len": args.max_len,
            "head_max_len": args.head_max_len,
            "routing": args.routing,
            "candidate_order": "original",
            "measurement": "CUDA synchronized around every prediction; routing and tokenization included",
        },
        "engine_initialization_seconds": load_seconds,
        "accuracy": {
            "correct": sum(record["correct"] for record in records),
            "total": len(records),
            "value": sum(record["correct"] for record in records) / len(records),
        },
        "latency": {
            "wall_seconds": inference_seconds,
            "throughput_requests_per_second": len(records) / inference_seconds,
            "mean_ms": statistics.mean(latencies),
            "p50_ms": percentile(latencies, 0.50),
            "p95_ms": percentile(latencies, 0.95),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
        },
        "input_audit": {
            "truncated_count": sum(audit["truncated"] for audit in audits),
            "collapsed_option_count": sum(
                audit["options"]["options_distinct"] < audit["options"]["options"]
                for audit in audits
            ),
            "capped_token_range": {
                "min": min(audit["capped_tokens"] for audit in audits),
                "max": max(audit["capped_tokens"] for audit in audits),
            },
            "full_token_max": max(audit["full_tokens"] for audit in audits),
            "model_counts": {
                model_name: sum(audit["model"] == model_name for audit in audits)
                for model_name in sorted({audit["model"] for audit in audits})
            },
        },
        "gpu": {
            "before": before,
            "after_load": after_load,
            "torch_peak_inference_allocated_mib": (
                torch.cuda.max_memory_allocated() / 1024**2 if use_cuda else None
            ),
            "torch_peak_inference_reserved_mib": (
                torch.cuda.max_memory_reserved() / 1024**2 if use_cuda else None
            ),
            "samples": summarize_samples(samples),
        },
        "records": records,
        "audits": audits,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in (
        "source", "environment", "conditions", "engine_initialization_seconds",
        "accuracy", "latency", "input_audit", "gpu",
    )}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
