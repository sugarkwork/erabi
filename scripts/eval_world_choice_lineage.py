"""Evaluate major historical ERABI checkpoints on World Choice V1 final_test."""
from __future__ import annotations

import argparse
import datetime as dt
import gc
import hashlib
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "world_choice_v1" / "final_test.jsonl"
DEFAULT_OUTPUT = ROOT / "runs" / "world_choice_v1_model_lineage_20260927"
MAX_TOKENS = 1024
MODELS = [
    ("rc1", ROOT / "release" / "rc1" / "model"),
    ("rc2", ROOT / "release" / "rc2" / "model"),
    ("rc2_1", ROOT / "release" / "rc2_1" / "model"),
    ("rc3", ROOT / "release" / "rc3" / "model"),
    ("practical_v1", ROOT / "runs" / "practical_v1_finetune_20260922" / "checkpoint"),
]


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--only", nargs="*", choices=[name for name, _ in MODELS])
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    selected = [(name, path) for name, path in MODELS if not args.only or name in args.only]
    if args.output_dir.exists() and not args.resume:
        raise FileExistsError(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, path in selected:
        if not (path / "model.safetensors").is_file():
            raise FileNotFoundError(f"Missing weights for {name}: {path}")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import torch
    from erabi.evaluate import compute_metrics
    from erabi.inference import GLiClassEngine
    from erabi.schema import ChoiceRequest

    rows = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != 404 or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Expected 404 unique World Choice final rows")
    summary_path = args.output_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "input": str(args.input.resolve()),
        "input_sha256": sha256(args.input),
        "rows": len(rows),
        "max_tokens": MAX_TOKENS,
        "device": args.device,
        "scope": "Major historical accepted ERABI checkpoints on exposed World Choice V1 final reference data.",
        "models": {},
    }
    if summary["input_sha256"] != sha256(args.input):
        raise RuntimeError("Input changed since lineage run started")

    for name, model_dir in selected:
        if name in summary["models"]:
            print(f"Skipping completed {name}", flush=True)
            continue
        weights = model_dir / "model.safetensors"
        print(f"Loading {name}: {weights}", flush=True)
        load_start = time.perf_counter()
        engine = GLiClassEngine(str(model_dir.resolve()), device=args.device, max_tokens=MAX_TOKENS)
        engine.model.eval()
        preparer = engine.pipe.pipe
        preparer.max_length = MAX_TOKENS
        load_seconds = time.perf_counter() - load_start
        predictions = []
        started = time.perf_counter()
        prediction_path = args.output_dir / f"{name}_predictions.jsonl"
        with prediction_path.open("x", encoding="utf-8") as handle:
            for index, row in enumerate(rows, 1):
                request = ChoiceRequest.from_dict(row)
                formatted = preparer.prepare_input(
                    request.context, [choice.text for choice in request.choices], prompt=request.question
                )
                input_tokens = len(engine.tokenizer(formatted, truncation=False)["input_ids"])
                if input_tokens > MAX_TOKENS:
                    raise ValueError(f"{row['id']}: {input_tokens} tokens exceeds contract")
                answer = engine.predict(request, return_logits=True)
                if answer.usage.truncated or answer.usage.input_tokens != input_tokens:
                    raise RuntimeError(f"{row['id']}: truncation or token mismatch")
                record = answer.to_dict() | {
                    "id": row["id"],
                    "domain": row["domain"],
                    "language": row["language"],
                    "target": row["target"]["choice_id"],
                    "correct": answer.best_candidate_id == row["target"]["choice_id"],
                }
                predictions.append(record)
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                if index % 100 == 0 or index == len(rows):
                    handle.flush()
                    print(f"{name}: {index}/{len(rows)} elapsed={time.perf_counter()-started:.1f}s", flush=True)

        def metrics(indices: list[int]) -> dict:
            chosen = [predictions[index] for index in indices]
            return compute_metrics(chosen, [item["target"] for item in chosen])

        elapsed = time.perf_counter() - started
        result = {
            "model_dir": str(model_dir.resolve()),
            "weights_sha256": sha256(weights),
            "load_seconds": load_seconds,
            "evaluation_seconds": elapsed,
            "overall": metrics(list(range(len(rows)))),
            "domain": {
                value: metrics([index for index, row in enumerate(rows) if row["domain"] == value])
                for value in sorted({row["domain"] for row in rows})
            },
            "language": {
                value: metrics([index for index, row in enumerate(rows) if row["language"] == value])
                for value in sorted({row["language"] for row in rows})
            },
            "predictions_sha256": sha256(prediction_path),
        }
        summary["models"][name] = result
        save_json(summary_path, summary)
        print(
            f"{name}: {result['overall']['correct_count']}/{len(rows)} "
            f"acc={result['overall']['accuracy']:.4f} nll={result['overall']['mean_nll']:.4f}",
            flush=True,
        )
        del engine
        gc.collect()
        torch.cuda.empty_cache()

    summary["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    summary["input_unchanged"] = sha256(args.input) == summary["input_sha256"]
    save_json(summary_path, summary)


if __name__ == "__main__":
    main()
