"""Single-process release latency/resource check on a supplied private JSONL.

Does not execute commands appearing in the input. Results stay in runs/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import threading
import time
from pathlib import Path

import psutil
import torch
from erabi.model_loader import load_engine
from erabi.schema import ChoiceRequest
from scripts.benchmark_laya_decision_mix_v2 import gpu_snapshot, percentile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--format", choices=("pytorch", "onnx-fp32", "onnx-fp16"), required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    torch.set_num_threads(args.threads)
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    requests = [ChoiceRequest.from_dict(row) for row in rows]
    process = psutil.Process()
    cuda = args.device.startswith("cuda")
    before_gpu = gpu_snapshot() if cuda else None
    samples = []
    stop = threading.Event()

    def sample():
        while not stop.is_set():
            samples.append({"rss_mib": process.memory_info().rss / 2**20,
                            "gpu": gpu_snapshot() if cuda else None})
            stop.wait(.5 if cuda else .02)

    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    try:
        start = time.perf_counter()
        engine = load_engine(model_id=args.model, model_format=args.format, device=args.device)
        if cuda:
            torch.cuda.synchronize()
        load_seconds = time.perf_counter() - start
        for request in requests[:8]:
            engine.predict(request)
        if cuda:
            torch.cuda.synchronize()
        latencies, tokens, correct = [], [], 0
        wall_start = time.perf_counter()
        for row, request in zip(rows, requests):
            start = time.perf_counter()
            response = engine.predict(request)
            if cuda:
                torch.cuda.synchronize()
            latencies.append(1000 * (time.perf_counter() - start))
            tokens.append(response.usage.input_tokens)
            if response.usage.truncated:
                raise RuntimeError("Unexpected truncation")
            correct += response.best_candidate_id == row["target"]["choice_id"]
        wall = time.perf_counter() - wall_start
    finally:
        stop.set()
        sampler.join(timeout=6)
    gpu_samples = [sample["gpu"] for sample in samples if sample["gpu"]]
    report = {
        "format": args.format, "device": args.device, "threads": args.threads,
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "rows": len(rows), "correct": correct, "accuracy": correct / len(rows),
        "tokens": {"min": min(tokens), "max": max(tokens)},
        "load_seconds": load_seconds, "wall_seconds": wall,
        "requests_per_second": len(rows) / wall,
        "latency_ms": {"mean": statistics.mean(latencies), "p50": percentile(latencies, .5),
                       "p95": percentile(latencies, .95)},
        "peak_rss_mib": max(sample["rss_mib"] for sample in samples),
        "gpu_before": before_gpu,
        "gpu_peak_mib": max((sample["memory_used_mib"] for sample in gpu_samples), default=None),
        "gpu_temperature_range": [min(sample["temperature_c"] for sample in gpu_samples),
                                  max(sample["temperature_c"] for sample in gpu_samples)] if gpu_samples else None,
        "gpu_clock_median_mhz": statistics.median(sample["sm_clock_mhz"] for sample in gpu_samples) if gpu_samples else None,
        "versions": {"torch": torch.__version__, "onnxruntime": __import__("onnxruntime").__version__},
        "providers": getattr(engine, "active_providers", None),
        "onnx_intra_op_threads": engine.session.get_session_options().intra_op_num_threads if hasattr(engine, "session") else None,
        "notes": "Batch 1, eight warmups, tokenization included. GPU is whole-device sampled at 0.5 s, not process VRAM.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
