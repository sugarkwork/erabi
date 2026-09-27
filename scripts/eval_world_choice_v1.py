"""Reference-only full-corpus scoring; never trains, selects, or saves weights."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import inspect
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=ROOT / "runs/exam_qa_erabi_v1_finetune_20260923/checkpoint")
    parser.add_argument("--input", type=Path, default=ROOT / "data/world_choice_v1/all.jsonl")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    if not args.model_dir.is_dir():
        parser.error("A local model directory is required; no download is performed.")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    import torch
    from erabi.evaluate import compute_metrics
    from erabi.inference import GLiClassEngine
    from erabi.schema import ChoiceRequest

    torch.set_num_threads(4)
    torch.manual_seed(20260926)
    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Empty input or duplicate ids")
    weights = args.model_dir / "model.safetensors"
    hashes = {"input_sha256": sha256(args.input), "weights_sha256": sha256(weights)}
    config = {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "input": str(args.input.resolve()), "model_dir": str(args.model_dir.resolve()),
        "device": args.device, "max_tokens": 1024, "temperature": 1.0,
        "expected_rows": len(rows), "torch_version": torch.__version__, **hashes,
        "gliclass_version": importlib.metadata.version("gliclass"),
        "transformers_version": importlib.metadata.version("transformers"),
        "scope": "User-authorized reference measurement across ALL original splits, including final_test and calibration. No training or model selection. These rows are now exposed diagnostics, not a future untouched acceptance test.",
        "label_quality": "DeepSeek synthetic agreement; provisional, not human gold.",
    }
    save_json(args.output_dir / "config.json", config)
    print(f"Loading local model; rows={len(rows)} weights_sha256={hashes['weights_sha256']}", flush=True)
    load_start = time.perf_counter()
    engine = GLiClassEngine(str(args.model_dir.resolve()), device=args.device, max_tokens=1024)
    engine.model.eval()
    preparer = engine.pipe.pipe
    preparer.max_length = 1024
    config["input_formatter_sha256"] = hashlib.sha256(inspect.getsource(preparer.prepare_input).encode()).hexdigest()
    config["input_formatter_note"] = "Use the current installed inference formatter unchanged. Stored generation counts use a separate helper; both lengths are recorded, and the actual inference input is independently checked without truncation."
    save_json(args.output_dir / "config.json", config)
    load_seconds = time.perf_counter() - load_start
    print(f"Model loaded in {load_seconds:.2f}s, dtype={next(engine.model.parameters()).dtype}", flush=True)
    predictions = []
    start = time.perf_counter()
    with (args.output_dir / "predictions.jsonl").open("x", encoding="utf-8") as handle:
        for index, row in enumerate(rows, 1):
            request = ChoiceRequest.from_dict(row)
            raw_input = preparer.prepare_input(request.context, [c.text for c in request.choices], prompt=request.question)
            tokens = len(engine.tokenizer(raw_input, truncation=False)["input_ids"])
            if tokens > 1024:
                raise ValueError(f"{row['id']}: over token limit: {tokens}")
            item_start = time.perf_counter()
            answer = engine.predict(request, return_logits=True)
            if answer.usage.truncated or answer.usage.input_tokens != tokens:
                raise RuntimeError(f"{row['id']}: truncation detected")
            record = answer.to_dict() | {
                "id": row["id"], "domain": row["domain"], "language": row["language"],
                "original_split": row["split"], "group_id": row["group_id"],
                "target": row["target"]["choice_id"],
                "generation_input_tokens": row["input_tokens"],
                "correct": answer.best_candidate_id == row["target"]["choice_id"],
                "elapsed_ms": (time.perf_counter() - item_start) * 1000,
            }
            predictions.append(record)
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            if index % 100 == 0 or index == len(rows):
                handle.flush()
                print(f"Scored {index}/{len(rows)}; elapsed={time.perf_counter()-start:.1f}s", flush=True)
    elapsed = time.perf_counter() - start

    def metrics(indices):
        selected = [predictions[i] for i in indices]
        return compute_metrics(selected, [p["target"] for p in selected])

    summary = config | {
        "status": "complete", "model_load_seconds": load_seconds,
        "evaluation_seconds": elapsed,
        "overall": metrics(range(len(rows))),
        "breakdowns": {field: {
            str(value): metrics([i for i, r in enumerate(rows) if r[field] == value])
            for value in sorted({r[field] for r in rows})
        } for field in ("domain", "language", "split")},
        "length_breakdown": {name: metrics([i for i, p in enumerate(predictions) if (p["usage"]["input_tokens"] > 512) == is_long])
            for name, is_long in (("up_to_512", False), ("513_to_1024", True))},
        "uniform_random_expected_accuracy": sum(1/len(r["choices"]) for r in rows)/len(rows),
        "longest_option_accuracy": sum(max(r["choices"], key=lambda c: len(c["text"]))["id"] == r["target"]["choice_id"] for r in rows)/len(rows),
        "inference_errors": 0, "skipped_rows": 0,
        "actual_input_tokens": {"min": min(p["usage"]["input_tokens"] for p in predictions),
            "max": max(p["usage"]["input_tokens"] for p in predictions),
            "differs_from_generation_count": sum(p["usage"]["input_tokens"] != p["generation_input_tokens"] for p in predictions)},
        "predictions_sha256": sha256(args.output_dir / "predictions.jsonl"),
    }
    if sha256(args.input) != hashes["input_sha256"] or sha256(weights) != hashes["weights_sha256"]:
        raise RuntimeError("Input data or weights changed during scoring")
    save_json(args.output_dir / "summary.json", summary)
    print(json.dumps({"overall": summary["overall"], "elapsed_seconds": elapsed,
                      "categories": {key: {m: value[m] for m in ("count", "correct_count", "accuracy")} for key, value in summary["breakdowns"]["domain"].items()}}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
