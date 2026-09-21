"""Run 2: Gentle Continual Calibration of 438M Large Model from SWA Checkpoint.

Starting Checkpoint: runs/rc3_large_curriculum/best_model_swa (87.92% Bridge Acc, 98.70% Core Retention)
Goal: Advance +0.21pt to clear Milestone 31 Development Gate (>= 88.0% Overall, >= 80.0% Paired Both).
Strategy: Low-temperature continual fine-tuning (peak LR = 2.5e-6, 1 epoch, checkpointing every 180 steps).
"""

from __future__ import annotations

import argparse
import datetime
import gc
import json
import logging
import math
from pathlib import Path
import random
import shutil
import sys
import time
from typing import Any, Dict, List, Optional

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer
from gliclass import GLiClassModel, ZeroShotClassificationPipeline

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.train import set_seed
from scripts.train_rc3 import evaluate_records, evaluate_development_gate, load_jsonl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.train_large_gentle")

BASE_MODEL = ROOT / "runs" / "rc3_large_curriculum" / "best_model_swa"
TRAIN_FILE = ROOT / "data" / "rc3_train" / "train.jsonl"
DEV_FILE = ROOT / "data" / "rc3_train" / "dev.jsonl"
BRIDGE_BENCHMARK_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
EVAL_V2_FILE = ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl"
OUT_DIR = ROOT / "runs" / "rc3_large_gentle"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoints_dir = OUT_DIR / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    set_seed(42)

    logger.info(f"Loading base SWA model from {BASE_MODEL}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = GLiClassModel.from_pretrained(BASE_MODEL).to(device)

    pipeline = ZeroShotClassificationPipeline(
        model=model,
        tokenizer=tokenizer,
        classification_type="single-label",
        device=device,
    )
    inner_pipe = pipeline.pipe

    train_records = load_jsonl(TRAIN_FILE)
    bridge_records = load_jsonl(BRIDGE_BENCHMARK_FILE)
    ev2_records = load_jsonl(EVAL_V2_FILE)

    lr = 2.5e-6
    weight_decay = 0.01
    micro_batch_size = 2
    gradient_accumulation_steps = 8
    max_norm = 1.0

    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scaler = torch.amp.GradScaler("cuda", enabled=True)

    total_micro_batches = (len(train_records) + micro_batch_size - 1) // micro_batch_size
    total_steps = (total_micro_batches + gradient_accumulation_steps - 1) // gradient_accumulation_steps
    warmup_steps = 40

    def get_lr(step: int) -> float:
        if step < warmup_steps:
            return lr * (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return 5e-7 + 0.5 * (lr - 5e-7) * (1.0 + math.cos(math.pi * progress))

    logger.info(f"Total steps: {total_steps}, Warmup: {warmup_steps}, LR: {lr:.2e}")

    # Shuffle training records by group
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in train_records:
        groups.setdefault(r["group_id"], []).append(r)
    group_list = list(groups.values())
    random.Random(42).shuffle(group_list)
    shuffled_train: List[Dict[str, Any]] = []
    for g in group_list:
        shuffled_train.extend(g)

    micro_batches = [shuffled_train[i:i + micro_batch_size] for i in range(0, len(shuffled_train), micro_batch_size)]
    num_windows = (len(micro_batches) + gradient_accumulation_steps - 1) // gradient_accumulation_steps

    step_results = {}
    best_step = -1
    best_bridge_acc = -1.0
    best_checkpoint_dir = None

    model.train()
    rng = random.Random(42)
    step = 0

    for w_idx in range(num_windows):
        w_start = w_idx * gradient_accumulation_steps
        w_end = min(w_start + gradient_accumulation_steps, len(micro_batches))
        w_batches = micro_batches[w_start:w_end]
        w_total_samples = sum(len(b) for b in w_batches)

        cur_lr = get_lr(step)
        for pg in optimizer.param_groups:
            pg["lr"] = cur_lr

        optimizer.zero_grad()

        for b in w_batches:
            texts, labels_list, prompts, target_indices = [], [], [], []
            for row in b:
                c_list = list(row["choices"])
                rng.shuffle(c_list)
                tgt_cid = row["target"]["choice_id"]
                target_indices.append(next(i for i, c in enumerate(c_list) if c["id"] == tgt_cid))
                texts.append(row.get("context", ""))
                labels_list.append([c["text"] for c in c_list])
                prompts.append(row.get("question", ""))

            tokenized = inner_pipe.prepare_inputs(texts=texts, labels=labels_list, same_labels=False, prompt=prompts)
            tokenized = {k: v.to(device) if hasattr(v, "to") else v for k, v in tokenized.items()}
            max_classes = max(len(lbls) for lbls in labels_list)

            with torch.amp.autocast("cuda", enabled=True):
                outputs = model(**tokenized, max_num_classes=max_classes)
                batch_loss = torch.tensor(0.0, device=device)
                for i, (tgt, lbls) in enumerate(zip(target_indices, labels_list)):
                    logits = outputs.logits[i, :len(lbls)].to(torch.float32)
                    batch_loss = batch_loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([tgt], device=device))
                weighted_loss = batch_loss / w_total_samples

            scaler.scale(weighted_loss).backward()

        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
        scaler.step(optimizer)
        scaler.update()
        step += 1

        # Evaluate checkpoint every 135 steps (~4 checks per epoch) or final step
        if step % 135 == 0 or step == total_steps:
            ckpt_dir = checkpoints_dir / f"step_{step}"
            ckpt_dir.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(ckpt_dir)
            tokenizer.save_pretrained(ckpt_dir)

            eval_engine = GLiClassEngine(model_id=str(ckpt_dir), device=device)
            res_b = evaluate_records(eval_engine, bridge_records, test_permutation=False)
            res_e = evaluate_records(eval_engine, ev2_records, test_permutation=False)
            del eval_engine
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

            b_acc = res_b["accuracy"]
            e_acc = res_e["accuracy"]
            p_both = res_b["paired_both_rate"]
            logger.info(f"Step {step:4d}/{total_steps} | Bridge: {b_acc*100:.2f}% ({res_b['correct']}/480, Paired: {p_both*100:.2f}%) | eval_v2: {e_acc*100:.2f}% | Loss: {batch_loss.item():.4f}")

            step_results[step] = {
                "step": step,
                "bridge_acc": b_acc,
                "bridge_correct": res_b["correct"],
                "bridge_paired": p_both,
                "eval_v2_acc": e_acc,
                "families": {f: s["accuracy"] for f, s in res_b["by_family"].items()},
                "checkpoint_dir": str(ckpt_dir),
            }

            if e_acc >= 0.96 and (b_acc > best_bridge_acc or (b_acc == best_bridge_acc and p_both > step_results.get(best_step, {}).get("bridge_paired", 0))):
                best_bridge_acc = b_acc
                best_step = step
                best_checkpoint_dir = ckpt_dir

    logger.info(f"Gentle fine-tuning complete! Best Step: {best_step} with Bridge Acc: {best_bridge_acc*100:.2f}%")

    # Select best model directory
    best_model_final = OUT_DIR / "best_model"
    if best_model_final.exists():
        shutil.rmtree(best_model_final)
    shutil.copytree(best_checkpoint_dir or checkpoints_dir / f"step_{total_steps}", best_model_final)
    logger.info(f"Copied best model to {best_model_final}")

    # Full Development Gate evaluation
    logger.info("=== Running Full Milestone 31 Development Gate Evaluation ===")
    dev_gate_results = evaluate_development_gate(best_model_final, device=device, output_dir=OUT_DIR)
    logger.info(f"Dev Gate Complete: Gate Passed = {dev_gate_results['milestone_31_gate_passed']}")


if __name__ == "__main__":
    main()
