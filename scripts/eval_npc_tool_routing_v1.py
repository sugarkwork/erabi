"""Provisional NPC routing evaluation of existing weights at up to 2k tokens."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=ROOT / "runs/practical_v1_finetune_20260922/checkpoint")
    parser.add_argument("--backend", choices=["pytorch", "onnx"], default="pytorch")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data/npc_tool_routing_v1")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--skip-over-limit", action="store_true", help="Skip and count over-limit rows instead of failing")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    from erabi.schema import ChoiceRequest

    if args.backend == "pytorch":
        from erabi.inference import GLiClassEngine

        engine = GLiClassEngine(str(args.model_dir), device="cuda:0", max_tokens=args.max_tokens)
        inner = engine.pipe.pipe
    else:
        from erabi.onnx_engine import ERABIONNXEngine

        engine = ERABIONNXEngine(model_dir=args.model_dir, device="cuda:0", max_tokens=args.max_tokens)
        inner = engine.preparer
    inner.max_length = args.max_tokens
    results = []
    excluded = {"dev": [], "eval": []}
    for split in ("dev", "eval"):
        path = args.data_dir / f"{split}.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            request = ChoiceRequest.from_dict(row)
            labels = [choice.text for choice in request.choices]
            raw = inner.prepare_input(request.context, labels, prompt=request.question)
            full_tokens = len(engine.tokenizer(raw, truncation=False)["input_ids"])
            if full_tokens > args.max_tokens:
                if args.skip_over_limit:
                    excluded[split].append({"id": row["id"], "input_tokens": full_tokens})
                    continue
                raise RuntimeError(f"{row['id']}: {full_tokens} > {args.max_tokens}")
            start = time.perf_counter()
            answer = engine.predict(request)
            if answer.usage.input_tokens != full_tokens:
                raise RuntimeError(f"{row['id']}: silently truncated {full_tokens} -> {answer.usage.input_tokens}")
            results.append({
                "id": row["id"], "split": split, "group_id": row["group_id"],
                "input_tokens": full_tokens, "target": row["target"]["choice_id"],
                "predicted": answer.best_candidate_id,
                "correct": answer.best_candidate_id == row["target"]["choice_id"],
                "elapsed_ms": (time.perf_counter() - start) * 1000,
            })
    summary = {"model_dir": str(args.model_dir), "backend": args.backend, "max_tokens": args.max_tokens, "splits": {}}
    for split in ("dev", "eval"):
        subset = [row for row in results if row["split"] == split]
        long_subset = [row for row in subset if row["input_tokens"] > 512]
        summary["splits"][split] = {
            "correct": sum(row["correct"] for row in subset), "total": len(subset),
            "long_correct": sum(row["correct"] for row in long_subset), "long_total": len(long_subset),
            "max_tokens_observed": max(row["input_tokens"] for row in subset),
            "excluded_over_limit": excluded[split],
        }
    if args.output:
        if args.output.exists():
            raise FileExistsError(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"summary": summary, "rows": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
