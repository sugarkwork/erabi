"""Benchmark ERABI PyTorch CUDA latency, initialization, and VRAM use."""
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
CHECKPOINT = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "checkpoint_selected"
MAX_TOKENS = 1024


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    fraction = position - lower
    if lower + 1 < len(ordered):
        return ordered[lower] * (1 - fraction) + ordered[lower + 1] * fraction
    return ordered[lower]


def gpu_snapshot() -> dict[str, float] | None:
    command = [
        "nvidia-smi",
        "--query-gpu=temperature.gpu,clocks.sm,power.draw,memory.used,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    try:
        output = subprocess.run(
            command, check=True, capture_output=True, text=True, timeout=5
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
    summary = {}
    for key in samples[0]:
        values = [sample[key] for sample in samples]
        summary[key] = {
            "min": min(values),
            "median": statistics.median(values),
            "max": max(values),
        }
    return summary


def mib(value: int) -> float:
    return value / 1024**2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--warmup", type=int, default=8)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True)

    import torch
    from erabi.inference import GLiClassEngine
    from erabi.schema import ChoiceRequest

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available in this Python environment")
    rows = [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line]
    if len(rows) != 404:
        raise ValueError("Expected 404 final rows")
    requests = [ChoiceRequest.from_dict(row) for row in rows]

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    before = gpu_snapshot()
    load_started = time.perf_counter()
    engine = GLiClassEngine(str(CHECKPOINT), device="cuda:0", max_tokens=MAX_TOKENS)
    engine.model.eval()
    engine.pipe.pipe.max_length = MAX_TOKENS
    torch.cuda.synchronize()
    load_seconds = time.perf_counter() - load_started
    after_load = gpu_snapshot()
    allocator_after_load = {
        "allocated_mib": mib(torch.cuda.memory_allocated()),
        "reserved_mib": mib(torch.cuda.memory_reserved()),
    }

    for request in requests[: args.warmup]:
        engine.predict(request, temperature=1.0)
    torch.cuda.synchronize()
    after_warmup = gpu_snapshot()
    allocator_after_warmup = {
        "allocated_mib": mib(torch.cuda.memory_allocated()),
        "reserved_mib": mib(torch.cuda.memory_reserved()),
    }
    torch.cuda.reset_peak_memory_stats()

    samples: list[dict[str, float]] = []
    stop_sampling = threading.Event()

    def sample_gpu() -> None:
        while not stop_sampling.wait(1.0):
            sample = gpu_snapshot()
            if sample:
                samples.append(sample)

    sampler = threading.Thread(target=sample_gpu, name="nvidia-smi-sampler", daemon=True)
    sampler.start()
    records = []
    inference_started = time.perf_counter()
    for index, (row, request) in enumerate(zip(rows, requests), 1):
        torch.cuda.synchronize()
        started = time.perf_counter()
        response = engine.predict(request, temperature=1.0)
        torch.cuda.synchronize()
        elapsed_ms = (time.perf_counter() - started) * 1000
        if response.usage.truncated or response.usage.input_tokens > MAX_TOKENS:
            raise RuntimeError(f"Truncation or token overflow: {row['id']}")
        records.append(
            {
                "id": row["id"],
                "tokens": response.usage.input_tokens,
                "elapsed_ms": elapsed_ms,
                "correct": response.best_candidate_id == row["target"]["choice_id"],
            }
        )
        if index % 100 == 0 or index == len(rows):
            print(f"cuda: {index}/{len(rows)}", flush=True)
    inference_seconds = time.perf_counter() - inference_started
    stop_sampling.set()
    sampler.join(timeout=6)
    final_snapshot = gpu_snapshot()
    if final_snapshot:
        samples.append(final_snapshot)

    latencies = [record["elapsed_ms"] for record in records]
    properties = torch.cuda.get_device_properties(0)
    result = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "environment": {
            "python": __import__("sys").version,
            "torch": torch.__version__,
            "torch_cuda_runtime": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "device": properties.name,
            "device_total_memory_mib": mib(properties.total_memory),
        },
        "conditions": {
            "rows": len(rows),
            "warmup": args.warmup,
            "batch_size": 1,
            "max_tokens": MAX_TOKENS,
            "measurement": "CUDA synchronize before and after every single-item prediction",
        },
        "engine_initialization_seconds": load_seconds,
        "latency": {
            "mean_ms": statistics.mean(latencies),
            "p50_ms": percentile(latencies, 0.50),
            "p95_ms": percentile(latencies, 0.95),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "wall_seconds": inference_seconds,
            "throughput_from_mean_rps": 1000 / statistics.mean(latencies),
        },
        "vram": {
            "device_before": before,
            "device_after_load": after_load,
            "device_after_warmup": after_warmup,
            "torch_allocator_after_load": allocator_after_load,
            "torch_allocator_after_warmup": allocator_after_warmup,
            "torch_peak_inference_allocated_mib": mib(torch.cuda.max_memory_allocated()),
            "torch_peak_inference_reserved_mib": mib(torch.cuda.max_memory_reserved()),
            "nvidia_smi_inference_samples": summarize_samples(samples),
        },
        "thermal_note": "nvidia-smi samples are whole-device values and include other WDDM processes",
        "correct_count": sum(record["correct"] for record in records),
        "token_range": {
            "min": min(record["tokens"] for record in records),
            "max": max(record["tokens"] for record in records),
        },
        "records": records,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in ("environment", "engine_initialization_seconds", "latency", "vram", "correct_count")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
