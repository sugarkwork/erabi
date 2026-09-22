"""Reproducible Practical V1 ONNX quantization and inference comparison.

Run from the repository root with the project virtual environment. Outputs are
experimental artifacts under runs/, not package defaults or release candidates.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import time
from collections import defaultdict
from pathlib import Path

import torch

from erabi.inference import GLiClassEngine
from erabi.onnx_engine import ERABIONNXEngine
from erabi.schema import ChoiceRequest, MAX_TOKENS


def load_stratified(path: Path, count: int) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                row = json.loads(line)
                groups[f"{row.get('family', '')}/{row.get('language', '')}"].append(row)
    selected: list[dict] = []
    while len(selected) < count and any(groups.values()):
        for key in sorted(groups):
            if groups[key] and len(selected) < count:
                selected.append(groups[key].pop(0))
    return selected


def prepare_onnx_inputs(engine: ERABIONNXEngine, row: dict) -> dict:
    request = ChoiceRequest.from_dict(row)
    tensors = engine.preparer.prepare_inputs(
        [request.context],
        [[choice.text for choice in request.choices]],
        same_labels=False,
        prompt=[request.question],
    )
    if tensors["input_ids"].shape[1] > MAX_TOKENS:
        raise ValueError(f"Input exceeds {MAX_TOKENS} tokens: {row.get('id')}")
    return {
        "input_ids": tensors["input_ids"].cpu().numpy(),
        "attention_mask": tensors["attention_mask"].cpu().numpy(),
    }


def quantize(args: argparse.Namespace) -> None:
    from onnxruntime.quantization import (
        CalibrationDataReader,
        CalibrationMethod,
        QuantFormat,
        QuantType,
        quantize_dynamic,
        quantize_static,
    )

    source = Path(args.fp32_dir)
    output = Path(args.output_dir)
    if not (source / "model.onnx").is_file():
        raise FileNotFoundError(source / "model.onnx")
    output.mkdir(parents=True, exist_ok=True)
    destination = output / "model.onnx"
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing model: {destination}")

    if args.mode == "dynamic":
        quantize_dynamic(
            str(source / "model.onnx"),
            str(destination),
            per_channel=True,
            weight_type=QuantType.QInt8,
            op_types_to_quantize=["MatMul", "Gemm"],
            extra_options={"MatMulConstBOnly": True},
        )
    else:
        rows = load_stratified(Path(args.train_file), args.calibration_count)
        if len(rows) != args.calibration_count:
            raise ValueError("Not enough calibration records")
        preparer = ERABIONNXEngine(source, device="cpu")
        batches = [prepare_onnx_inputs(preparer, row) for row in rows]
        del preparer

        class Reader(CalibrationDataReader):
            def __init__(self, inputs: list[dict]):
                self.inputs = iter(inputs)

            def get_next(self):
                return next(self.inputs, None)

        quantize_static(
            str(source / "model.onnx"),
            str(destination),
            Reader(batches),
            quant_format=QuantFormat.QDQ,
            per_channel=True,
            activation_type=QuantType.QInt8,
            weight_type=QuantType.QInt8,
            op_types_to_quantize=["MatMul", "Gemm"],
            calibrate_method=CalibrationMethod.MinMax,
        )

    for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
        shutil.copy2(source / name, output / name)
    print(f"Saved {args.mode} INT8 model: {destination} ({destination.stat().st_size} bytes)")


def percentile(values: list[float], quantile: float) -> float:
    sorted_values = sorted(values)
    position = (len(sorted_values) - 1) * quantile
    lower = int(position)
    fraction = position - lower
    if lower + 1 < len(sorted_values):
        return sorted_values[lower] * (1 - fraction) + sorted_values[lower + 1] * fraction
    return sorted_values[lower]


def benchmark(args: argparse.Namespace) -> None:
    rows = load_stratified(Path(args.eval_file), args.cases)
    if len(rows) != args.cases:
        raise ValueError("Not enough evaluation records")
    requests = [ChoiceRequest.from_dict(row) for row in rows]
    if args.threads:
        torch.set_num_threads(args.threads)
    if args.backend == "pytorch":
        engine = GLiClassEngine(model_id=args.model_dir, device=args.device)
        weight_file = Path(args.model_dir) / "model.safetensors"
    else:
        engine = ERABIONNXEngine(model_dir=args.model_dir, device=args.device)
        weight_file = Path(args.model_dir) / "model.onnx"
        if args.device == "cuda" and "CUDAExecutionProvider" not in engine.active_providers:
            raise RuntimeError(f"CUDA provider not active: {engine.active_providers}")

    predictions = []
    for row, request in zip(rows, requests):
        response = engine.predict(request, temperature=1.0)
        predictions.append({
            "id": row["id"],
            "target_id": row["target"]["choice_id"],
            "best_candidate_id": response.best_candidate_id,
            "choices": [{"id": c.id, "probability": c.probability} for c in response.choices],
        })

    for index in range(args.warmup):
        engine.predict(requests[index % len(requests)], temperature=1.0)
    latency_ms = []
    for index in range(args.iterations):
        start = time.perf_counter()
        engine.predict(requests[index % len(requests)], temperature=1.0)
        if args.backend == "pytorch" and args.device == "cuda":
            torch.cuda.synchronize()
        latency_ms.append((time.perf_counter() - start) * 1000)

    correct = sum(p["best_candidate_id"] == p["target_id"] for p in predictions)
    result = {
        "backend": args.backend,
        "device": args.device,
        "model_dir": str(Path(args.model_dir).resolve()),
        "model_bytes": weight_file.stat().st_size,
        "eval_file": str(Path(args.eval_file).resolve()),
        "cases": len(predictions),
        "teacher_label_correct": correct,
        "teacher_label_accuracy": correct / len(predictions),
        "temperature": 1.0,
        "warmup": args.warmup,
        "iterations": args.iterations,
        "threads_torch": args.threads,
        "latency_ms": {
            "mean": statistics.mean(latency_ms),
            "p50": percentile(latency_ms, 0.50),
            "p95": percentile(latency_ms, 0.95),
            "min": min(latency_ms),
            "max": max(latency_ms),
        },
        "predictions": predictions,
    }
    if args.backend == "onnx":
        result["active_providers"] = engine.active_providers
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{args.backend} {args.device}: {correct}/{len(predictions)}, "
          f"p50={result['latency_ms']['p50']:.2f}ms, p95={result['latency_ms']['p95']:.2f}ms -> {output}")


def compare(args: argparse.Namespace) -> None:
    baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))
    base_predictions = {p["id"]: p for p in baseline["predictions"]}
    other_predictions = {p["id"]: p for p in candidate["predictions"]}
    if base_predictions.keys() != other_predictions.keys():
        raise ValueError("Evaluation IDs differ")
    match = 0
    drifts = []
    for key in base_predictions:
        left = base_predictions[key]
        right = other_predictions[key]
        if left["best_candidate_id"] == right["best_candidate_id"]:
            match += 1
        left_choices = {c["id"]: c["probability"] for c in left["choices"]}
        right_choices = {c["id"]: c["probability"] for c in right["choices"]}
        if left_choices.keys() != right_choices.keys():
            raise ValueError(f"Choice IDs differ: {key}")
        drifts.append(max(abs(left_choices[choice] - right_choices[choice]) for choice in left_choices))
    print(json.dumps({
        "cases": len(base_predictions),
        "top1_matches": match,
        "top1_parity": match / len(base_predictions),
        "mean_max_probability_drift": statistics.mean(drifts),
        "max_probability_drift": max(drifts),
        "candidate_teacher_label_accuracy": candidate["teacher_label_accuracy"],
        "baseline_p50_ms": baseline["latency_ms"]["p50"],
        "candidate_p50_ms": candidate["latency_ms"]["p50"],
    }, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    quant = subparsers.add_parser("quantize")
    quant.add_argument("--mode", choices=["dynamic", "static"], required=True)
    quant.add_argument("--fp32-dir", required=True)
    quant.add_argument("--output-dir", required=True)
    quant.add_argument("--train-file", default="data/practical_v1/train.jsonl")
    quant.add_argument("--calibration-count", type=int, default=128)
    quant.set_defaults(func=quantize)
    bench = subparsers.add_parser("benchmark")
    bench.add_argument("--backend", choices=["pytorch", "onnx"], required=True)
    bench.add_argument("--device", choices=["cpu", "cuda"], required=True)
    bench.add_argument("--model-dir", required=True)
    bench.add_argument("--eval-file", default="data/practical_v1/eval_teacher_agreed.jsonl")
    bench.add_argument("--cases", type=int, default=90)
    bench.add_argument("--warmup", type=int, default=8)
    bench.add_argument("--iterations", type=int, default=40)
    bench.add_argument("--threads", type=int, default=None)
    bench.add_argument("--output", required=True)
    bench.set_defaults(func=benchmark)
    comp = subparsers.add_parser("compare")
    comp.add_argument("--baseline", required=True)
    comp.add_argument("--candidate", required=True)
    comp.set_defaults(func=compare)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
