"""Benchmark ERABI batch inference with output-parity checks."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "world_choice_v1" / "final_test.jsonl"
CHECKPOINT = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "checkpoint_selected"
ONNX_FP32 = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "onnx" / "fp32"
ONNX_FP16 = ROOT / "runs" / "world_choice_v1_finetune_20260927" / "onnx" / "fp16"
MAX_TOKENS = 1024


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend",
        required=True,
        choices=("pytorch_cuda", "onnx_fp16_cuda", "onnx_fp32_cpu"),
    )
    parser.add_argument("--batch-sizes", default="1,2,4,8,16")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    import torch
    from erabi.inference import GLiClassEngine
    from erabi.onnx_engine import ERABIONNXEngine
    from erabi.schema import ChoiceRequest

    torch.set_num_threads(args.threads)
    batch_sizes = [int(value) for value in args.batch_sizes.split(",")]
    if not batch_sizes or any(value < 1 for value in batch_sizes):
        raise ValueError("Batch sizes must be positive integers")

    rows = [
        json.loads(line)
        for line in DATA.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if args.limit is not None:
        rows = rows[: args.limit]
    requests = [ChoiceRequest.from_dict(row) for row in rows]

    load_started = time.perf_counter()
    if args.backend == "pytorch_cuda":
        engine = GLiClassEngine(CHECKPOINT, device="cuda:0", max_tokens=MAX_TOKENS)
        engine.model.eval()
        engine.pipe.pipe.max_length = MAX_TOKENS
    elif args.backend == "onnx_fp16_cuda":
        engine = ERABIONNXEngine(ONNX_FP16, device="cuda:0", max_tokens=MAX_TOKENS)
        engine.preparer.max_length = MAX_TOKENS
        if "CUDAExecutionProvider" not in engine.active_providers:
            raise RuntimeError(f"CUDA provider is not active: {engine.active_providers}")
    else:
        engine = ERABIONNXEngine(ONNX_FP32, device="cpu", max_tokens=MAX_TOKENS)
        engine.preparer.max_length = MAX_TOKENS
    if torch.cuda.is_available() and "cuda" in args.backend:
        torch.cuda.synchronize()
    load_seconds = time.perf_counter() - load_started

    result = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "backend": args.backend,
        "rows": len(rows),
        "max_tokens": MAX_TOKENS,
        "threads": args.threads,
        "engine_initialization_seconds": load_seconds,
        "measurement": (
            "One full pass per batch size after one untimed warmup batch; original row order; "
            "end-to-end tokenization plus inference; CUDA synchronized around timed pass."
        ),
        "batch_sizes": {},
    }
    baseline = None
    for batch_size in batch_sizes:
        engine.predict_batch(
            requests[:batch_size],
            temperature=1.0,
            return_logits=True,
            batch_size=batch_size,
        )
        if torch.cuda.is_available() and "cuda" in args.backend:
            torch.cuda.synchronize()
        started = time.perf_counter()
        responses = engine.predict_batch(
            requests,
            temperature=1.0,
            return_logits=True,
            batch_size=batch_size,
        )
        if torch.cuda.is_available() and "cuda" in args.backend:
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - started

        predictions = [response.best_candidate_id for response in responses]
        correct = sum(
            prediction == row["target"]["choice_id"]
            for prediction, row in zip(predictions, rows)
        )
        if baseline is None:
            baseline = responses
            top1_matches = len(responses)
            max_logit_delta = 0.0
        else:
            top1_matches = sum(
                response.best_candidate_id == reference.best_candidate_id
                for response, reference in zip(responses, baseline)
            )
            max_logit_delta = max(
                abs(value - reference_value)
                for response, reference in zip(responses, baseline)
                for value, reference_value in zip(
                    response.raw_logits or [], reference.raw_logits or []
                )
            )
        result["batch_sizes"][str(batch_size)] = {
            "wall_seconds": elapsed,
            "throughput_requests_per_second": len(rows) / elapsed,
            "mean_wall_ms_per_request": elapsed * 1000 / len(rows),
            "correct_count": correct,
            "top1_matches_vs_batch_1": top1_matches,
            "max_abs_logit_delta_vs_batch_1": max_logit_delta,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps({"batch_size": batch_size, **result["batch_sizes"][str(batch_size)]}), flush=True)

    baseline_throughput = result["batch_sizes"][str(batch_sizes[0])][
        "throughput_requests_per_second"
    ]
    for values in result["batch_sizes"].values():
        values["speedup_vs_first_batch_size"] = (
            values["throughput_requests_per_second"] / baseline_throughput
        )
    result["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
