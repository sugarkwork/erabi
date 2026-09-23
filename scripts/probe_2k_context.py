"""Isolated long-context diagnostic; does not alter the 512-token release contract."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=ROOT / "runs/practical_v1_finetune_20260922/checkpoint")
    parser.add_argument("--backend", choices=["pytorch", "onnx"], default="pytorch")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--lengths", type=int, nargs="+", default=[512, 1024, 2048])
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError(args.output)

    import torch
    from erabi.schema import ChoiceRequest

    if args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable")

    if args.backend == "pytorch":
        from erabi.inference import GLiClassEngine

        engine = GLiClassEngine(model_id=str(args.model_dir), device=args.device, max_tokens=max(args.lengths))
        inner = engine.pipe.pipe
    else:
        from erabi.onnx_engine import ERABIONNXEngine

        engine = ERABIONNXEngine(model_dir=args.model_dir, device=args.device, max_tokens=max(args.lengths))
        inner = engine.preparer
    inner.max_length = max(args.lengths)
    labels = ["村人と雑談する", "村の地図を開く", "クエストを受注する", "道具を使う"]
    question = "次に行うべきNPCの行動を一つ選んでください。"
    unit = "村人は道を案内した。冒険者は礼を言った。"

    def make_request(target: int) -> tuple[ChoiceRequest, int]:
        lo, hi = 0, target
        while lo < hi:
            mid = (lo + hi + 1) // 2
            prepared = inner.prepare_input(unit * mid, labels, prompt=question)
            count = len(engine.tokenizer(prepared, truncation=False)["input_ids"])
            if count <= target:
                lo = mid
            else:
                hi = mid - 1
        from erabi.schema import ChoiceInput

        request = ChoiceRequest(
            context=unit * lo,
            question=question,
            choices=[ChoiceInput(id=f"c{i}", text=label) for i, label in enumerate(labels)],
        )
        formatted = inner.prepare_input(request.context, labels, prompt=question)
        full_tokens = len(engine.tokenizer(formatted, truncation=False)["input_ids"])
        return request, full_tokens

    results = []
    for target in args.lengths:
        request, full_tokens = make_request(target)
        result = {"backend": args.backend, "target_tokens": target, "full_tokens_before_pipeline": full_tokens}
        if args.backend == "onnx":
            result["active_providers"] = engine.active_providers
        try:
            prepared = inner.prepare_inputs([request.context], [labels], prompt=[question])
            result["tokens_after_pipeline"] = int(prepared["input_ids"].shape[1])
            if result["tokens_after_pipeline"] != full_tokens:
                raise RuntimeError("Pipeline silently truncated the input")
            if args.device.startswith("cuda"):
                torch.cuda.reset_peak_memory_stats()
            for _ in range(args.warmup):
                engine.predict(request)
            if args.device.startswith("cuda"):
                torch.cuda.synchronize()
            times = []
            for _ in range(args.repeats):
                start = time.perf_counter()
                answer = engine.predict(request)
                if args.device.startswith("cuda"):
                    torch.cuda.synchronize()
                times.append((time.perf_counter() - start) * 1000)
            result["p50_ms"] = statistics.median(times)
            result["p95_ms"] = sorted(times)[min(len(times) - 1, int(len(times) * .95))]
            result["chosen_id"] = answer.best_candidate_id
            if args.device.startswith("cuda") and args.backend == "pytorch":
                result["peak_allocated_mib"] = torch.cuda.max_memory_allocated() / 1024**2
                result["peak_reserved_mib"] = torch.cuda.max_memory_reserved() / 1024**2
        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            if args.device.startswith("cuda"):
                torch.cuda.empty_cache()
        print(json.dumps(result, ensure_ascii=False), flush=True)
        results.append(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"model_dir": str(args.model_dir), "device": args.device, "warmup": args.warmup, "repeats": args.repeats, "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
