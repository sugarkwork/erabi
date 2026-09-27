"""Measure current ERABI PyTorch and ONNX FP32 CPU latency on World Choice V1."""
from __future__ import annotations

import argparse
import datetime as dt
import gc
import json
import os
import statistics
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "world_choice_v1" / "final_test.jsonl"
CHECKPOINT = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "checkpoint_selected"
ONNX_FP32 = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "onnx" / "fp32"
OUTPUT = ROOT / "runs" / "world_choice_v1_cpu_benchmark_20260927"
MAX_TOKENS = 1024


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    fraction = position - lower
    if lower + 1 < len(ordered):
        return ordered[lower] * (1 - fraction) + ordered[lower + 1] * fraction
    return ordered[lower]


def stats(records: list[dict]) -> dict:
    latency = [record["elapsed_ms"] for record in records]
    return {
        "count": len(records),
        "mean_ms": statistics.mean(latency),
        "p50_ms": percentile(latency, 0.50),
        "p95_ms": percentile(latency, 0.95),
        "min_ms": min(latency),
        "max_ms": max(latency),
        "throughput_from_mean_rps": 1000 / statistics.mean(latency),
    }


def run_backend(name: str, rows: list[dict], threads: int) -> dict:
    import psutil

    process = psutil.Process()
    phase = {"name": "imports"}
    phase_peak_rss = {"imports": process.memory_info().rss}
    stop_sampling = threading.Event()

    def sample_resources() -> None:
        while not stop_sampling.wait(0.02):
            current_phase = phase["name"]
            rss = process.memory_info().rss
            phase_peak_rss[current_phase] = max(phase_peak_rss.get(current_phase, 0), rss)

    sampler = threading.Thread(target=sample_resources, name="resource-sampler", daemon=True)
    sampler.start()
    rss_at_process_start = process.memory_info().rss

    import torch
    from erabi.inference import GLiClassEngine
    from erabi.onnx_engine import ERABIONNXEngine
    from erabi.schema import ChoiceRequest

    torch.set_num_threads(threads)
    rss_after_imports = process.memory_info().rss
    phase["name"] = "model_load"
    load_started = time.perf_counter()
    if name == "onnx_fp32":
        engine = ERABIONNXEngine(ONNX_FP32, device="cpu", max_tokens=MAX_TOKENS)
        preparer = engine.preparer
    else:
        engine = GLiClassEngine(str(CHECKPOINT), device="cpu", max_tokens=MAX_TOKENS)
        engine.model.eval()
        preparer = engine.pipe.pipe
    preparer.max_length = MAX_TOKENS
    load_seconds = time.perf_counter() - load_started
    rss_after_model_load = process.memory_info().rss

    requests = [ChoiceRequest.from_dict(row) for row in rows]
    phase["name"] = "warmup"
    for request in requests[:8]:
        engine.predict(request, temperature=1.0)
    rss_after_warmup = process.memory_info().rss

    phase["name"] = "inference"
    cpu_before = process.cpu_times()
    inference_started = time.perf_counter()
    measured = []
    for index, (row, request) in enumerate(zip(rows, requests), 1):
        started = time.perf_counter()
        response = engine.predict(request, temperature=1.0)
        elapsed_ms = (time.perf_counter() - started) * 1000
        if response.usage.truncated or response.usage.input_tokens > MAX_TOKENS:
            raise RuntimeError(f"Truncation or token overflow: {row['id']}")
        measured.append({
            "id": row["id"],
            "tokens": response.usage.input_tokens,
            "elapsed_ms": elapsed_ms,
            "correct": response.best_candidate_id == row["target"]["choice_id"],
        })
        if index % 100 == 0 or index == len(rows):
            print(f"{name}: {index}/{len(rows)}", flush=True)
    inference_wall_seconds = time.perf_counter() - inference_started
    cpu_after = process.cpu_times()
    inference_cpu_seconds = (
        cpu_after.user + cpu_after.system - cpu_before.user - cpu_before.system
    )
    effective_logical_cores = inference_cpu_seconds / inference_wall_seconds
    logical_processors = psutil.cpu_count(logical=True) or 1
    stop_sampling.set()
    sampler.join(timeout=1)
    phase_peak_rss[phase["name"]] = max(
        phase_peak_rss.get(phase["name"], 0), process.memory_info().rss
    )

    buckets = {
        "1_128": [record for record in measured if record["tokens"] <= 128],
        "129_256": [record for record in measured if 128 < record["tokens"] <= 256],
        "257_512": [record for record in measured if 256 < record["tokens"] <= 512],
        "513_1024": [record for record in measured if record["tokens"] > 512],
    }
    result = {
        "backend": name,
        "load_seconds": load_seconds,
        "overall": stats(measured),
        "token_buckets": {key: stats(value) for key, value in buckets.items() if value},
        "token_range": {"min": min(r["tokens"] for r in measured), "max": max(r["tokens"] for r in measured)},
        "correct_count": sum(record["correct"] for record in measured),
        "resources": {
            "rss_at_process_start_bytes": rss_at_process_start,
            "rss_after_imports_bytes": rss_after_imports,
            "rss_after_model_load_bytes": rss_after_model_load,
            "rss_after_warmup_bytes": rss_after_warmup,
            "peak_rss_bytes": max(phase_peak_rss.values()),
            "peak_rss_by_phase_bytes": phase_peak_rss,
            "model_load_rss_increment_bytes": rss_after_model_load - rss_after_imports,
            "runtime_rss_increment_bytes": rss_after_warmup - rss_at_process_start,
            "inference_wall_seconds": inference_wall_seconds,
            "inference_cpu_seconds": inference_cpu_seconds,
            "average_effective_logical_cores": effective_logical_cores,
            "average_host_cpu_capacity_percent": effective_logical_cores / logical_processors * 100,
            "logical_processors": logical_processors,
        },
        "records": measured,
    }
    if name == "onnx_fp32":
        result["active_providers"] = engine.active_providers
    del engine
    gc.collect()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--backend", choices=("onnx_fp32", "pytorch_fp32"), action="append")
    args = parser.parse_args()
    if not 1 <= args.threads <= 16:
        raise ValueError("threads must be 1..16")
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    rows = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 404:
        raise ValueError("Expected 404 final rows")

    result = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "cpu": os.environ.get("PROCESSOR_IDENTIFIER"),
        "threads": args.threads,
        "rows": len(rows),
        "max_tokens": MAX_TOKENS,
        "measurement": "Eight untimed warmups followed by one timed single-item inference per row; no batching.",
        "backends": {},
    }
    backends = args.backend or ["onnx_fp32", "pytorch_fp32"]
    for backend in backends:
        result["backends"][backend] = run_backend(backend, rows, args.threads)
        (args.output_dir / "summary.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    result["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    compact = {
        name: {"load_seconds": value["load_seconds"], **value["overall"], "buckets": value["token_buckets"]}
        for name, value in result["backends"].items()
    }
    print(json.dumps(compact, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
