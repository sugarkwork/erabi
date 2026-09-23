"""One synthetic training step at a requested length; no checkpoint is changed."""

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
    parser.add_argument("--length", type=int, required=True)
    parser.add_argument("--batch-size", type=int, default=1)
    args = parser.parse_args()

    import torch
    import torch.nn.functional as F
    from erabi.inference import GLiClassEngine

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this diagnostic")
    engine = GLiClassEngine(str(args.model_dir), device="cuda:0", max_tokens=args.length)
    inner = engine.pipe.pipe
    inner.max_length = args.length
    labels = ["村人と雑談する", "村の地図を開く", "クエストを受注する", "道具を使う"]
    question = "次に行うべきNPCの行動を一つ選んでください。"
    unit = "村人は道を案内した。冒険者は礼を言った。"
    lo, hi = 0, args.length
    while lo < hi:
        mid = (lo + hi + 1) // 2
        count = len(engine.tokenizer(inner.prepare_input(unit * mid, labels, prompt=question), truncation=False)["input_ids"])
        if count <= args.length:
            lo = mid
        else:
            hi = mid - 1
    context = unit * lo
    full_tokens = len(engine.tokenizer(inner.prepare_input(context, labels, prompt=question), truncation=False)["input_ids"])
    inputs = inner.prepare_inputs([context] * args.batch_size, [labels] * args.batch_size, prompt=[question] * args.batch_size)
    actual_tokens = int(inputs["input_ids"].shape[1])
    if actual_tokens != full_tokens:
        raise RuntimeError(f"Truncated: {full_tokens} -> {actual_tokens}")
    max_classes = inner._resolve_max_num_classes([labels] * args.batch_size, same_labels=False)
    optimizer = torch.optim.AdamW(engine.model.parameters(), lr=1e-6)
    scaler = torch.amp.GradScaler("cuda", init_scale=1024.0)
    engine.model.train()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    with torch.amp.autocast("cuda", dtype=torch.float16):
        logits = engine.model(**inputs, max_num_classes=max_classes).logits[:, :len(labels)].float()
        loss = F.cross_entropy(logits, torch.zeros(args.batch_size, device="cuda:0", dtype=torch.long))
    scaler.scale(loss).backward()
    scale_before = scaler.get_scale()
    scaler.step(optimizer)
    scaler.update()
    torch.cuda.synchronize()
    print(json.dumps({
        "target_tokens": args.length,
        "actual_tokens": actual_tokens,
        "batch_size": args.batch_size,
        "step_ms": (time.perf_counter() - start) * 1000,
        "peak_allocated_mib": torch.cuda.max_memory_allocated() / 1024**2,
        "peak_reserved_mib": torch.cuda.max_memory_reserved() / 1024**2,
        "loss": float(loss.detach().cpu()),
        "scaler": scaler.get_scale(),
        "optimizer_step_skipped": scaler.get_scale() < scale_before,
    }, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
