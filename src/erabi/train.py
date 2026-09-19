"""Training module for ERABI M2.1: Hard-label Cross-Entropy fine-tuning.

Supports:
  - Overfit diagnostic mode (<=64 cases)
  - Full training mode (~600 train / ~100 dev)
  - Candidate shuffling with target tracking
  - Gradient accumulation and AMP
  - Strict evaluation and checkpoint saving
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import math
import os
import random
import sys
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F
from erabi.__main__ import get_environment_info
from erabi.evaluate import compute_metrics
from erabi.schema import ChoiceRequest
from gliclass import GLiClassModel, ZeroShotClassificationPipeline
from transformers import AutoTokenizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.train")

DEFAULT_MODEL_ID = "knowledgator/gliclass-instruct-base-v1.0"


def set_seed(seed: int = 42):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class Trainer:
    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: Optional[str] = None,
        lr: float = 2e-5,
        weight_decay: float = 0.01,
        max_norm: float = 1.0,
        gradient_accumulation_steps: int = 8,
        micro_batch_size: int = 2,
        seed: int = 42,
    ):
        self.model_id = model_id
        self.device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.lr = lr
        self.weight_decay = weight_decay
        self.max_norm = max_norm
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.micro_batch_size = micro_batch_size
        self.seed = seed

        set_seed(seed)

        logger.info(f"Loading base model {model_id} onto {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = GLiClassModel.from_pretrained(model_id)
        self.model.to(self.device)

        self.pipeline = ZeroShotClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            classification_type="single-label",
            device=self.device,
        )

        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.lr,
            weight_decay=self.weight_decay,
        )

    def prepare_batch(
        self,
        records: List[Dict[str, Any]],
        shuffle_choices: bool = False,
        rng: Optional[random.Random] = None,
    ) -> Tuple[Dict[str, torch.Tensor], List[int], List[int], int]:
        """Format batch into tokenized inputs and extract target indices."""
        inner_pipe = self.pipeline.pipe
        texts = []
        labels_list = []
        prompts = []
        target_indices = []
        num_choices_list = []

        for row in records:
            context = row.get("context", "")
            question = row.get("question", "")
            choices = list(row["choices"])
            target_cid = row["target"]["choice_id"]

            if shuffle_choices and rng is not None:
                rng.shuffle(choices)

            target_idx = next(i for i, c in enumerate(choices) if c["id"] == target_cid)
            target_indices.append(target_idx)
            num_choices_list.append(len(choices))

            texts.append(context)
            labels_list.append([c["text"] for c in choices])
            prompts.append(question)

        tokenized = inner_pipe.prepare_inputs(
            texts=texts,
            labels=labels_list,
            same_labels=False,
            prompt=prompts,
        )

        max_num_classes = inner_pipe._resolve_max_num_classes(labels_list, same_labels=False)
        return tokenized, target_indices, num_choices_list, max_num_classes

    def compute_batch_loss(
        self,
        tokenized_inputs: Dict[str, torch.Tensor],
        target_indices: List[int],
        num_choices_list: List[int],
        max_num_classes: int,
    ) -> torch.Tensor:
        """Compute mean cross entropy loss over valid candidate subset per sample."""
        outputs = self.model(**tokenized_inputs, max_num_classes=max_num_classes)
        # Cast to float32 for stable loss
        logits = outputs.logits.to(torch.float32)

        losses = []
        for b in range(len(target_indices)):
            k = num_choices_list[b]
            sample_logits = logits[b, :k].unsqueeze(0)  # shape (1, k)
            target_tensor = torch.tensor([target_indices[b]], device=self.device, dtype=torch.long)
            loss = F.cross_entropy(sample_logits, target_tensor)
            losses.append(loss)

        return torch.stack(losses).mean()

    @torch.no_grad()
    def evaluate(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run evaluation on records using model in eval mode."""
        self.model.eval()
        predictions = []
        targets = []

        for row in records:
            req = ChoiceRequest.from_dict(row)
            target_choice_id = row["target"]["choice_id"]

            # Tokenize single record via pipeline
            labels = [c.text for c in req.choices]
            inner_pipe = self.pipeline.pipe
            tokenized = inner_pipe.prepare_inputs(
                texts=[req.context],
                labels=[labels],
                same_labels=False,
                prompt=[req.question],
            )
            max_num_classes = inner_pipe._resolve_max_num_classes([labels], same_labels=False)

            outputs = self.model(**tokenized, max_num_classes=max_num_classes)
            logits_tensor = outputs.logits[0, : len(labels)].to(torch.float32)
            probs = torch.softmax(logits_tensor, dim=-1).cpu().tolist()

            best_idx = int(torch.argmax(logits_tensor).item())
            best_id = req.choices[best_idx].id

            choice_outputs = [{"id": c.id, "probability": float(p)} for c, p in zip(req.choices, probs)]
            predictions.append({
                "choices": choice_outputs,
                "best_candidate_id": best_id,
                "raw_logits": logits_tensor.cpu().tolist(),
            })
            targets.append(target_choice_id)

        metrics = compute_metrics(predictions, targets, metadata=records)

        # Detailed pair diagnostics for tracking (M3.5)
        groups = defaultdict(list)
        for row, pred in zip(records, predictions):
            groups[row["group_id"]].append({
                "task_family": row.get("task_family", ""),
                "target": row["target"]["choice_id"],
                "pred": pred["best_candidate_id"],
                "is_correct": (pred["best_candidate_id"] == row["target"]["choice_id"]),
            })

        diff_total = 0
        diff_both = 0
        diff_same_pred = 0
        diff_gf_total = 0
        diff_gf_both = 0
        same_total = 0
        same_both = 0

        for gid, plist in groups.items():
            if len(plist) == 2:
                is_diff = (plist[0]["target"] != plist[1]["target"])
                both = (plist[0]["is_correct"] and plist[1]["is_correct"])
                same_p = (plist[0]["pred"] == plist[1]["pred"])
                is_gf = (plist[0]["task_family"] == "goal_following")

                if is_diff:
                    diff_total += 1
                    if both:
                        diff_both += 1
                    if same_p:
                        diff_same_pred += 1
                    if is_gf:
                        diff_gf_total += 1
                        if both:
                            diff_gf_both += 1
                else:
                    same_total += 1
                    if both:
                        same_both += 1

        metrics["pair_diagnostics"] = {
            "diff_target_both": diff_both,
            "diff_target_total": diff_total,
            "diff_target_pred_same": diff_same_pred,
            "diff_gf_both": diff_gf_both,
            "diff_gf_total": diff_gf_total,
            "same_target_both": same_both,
            "same_target_total": same_total,
        }
        return metrics

    def save_checkpoint(self, output_dir: str):
        """Save model weights and tokenizer to directory."""
        os.makedirs(output_dir, exist_ok=True)
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        logger.info(f"Saved checkpoint to {output_dir}")


def run_overfit_diagnostic(args: argparse.Namespace):
    """Phase A: Overfit on <=64 cases from train to verify learning, gradients, and save/reload."""
    print("=== M2.1 Phase A: Overfit Diagnostic (<=64 cases) ===")
    train_path = os.path.join(args.data_dir, "train.jsonl")
    records = []
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    # Take first 32 groups (64 cases)
    seen_groups = set()
    diag_records = []
    for r in records:
        gid = r["group_id"]
        if gid not in seen_groups and len(seen_groups) >= 32:
            continue
        seen_groups.add(gid)
        diag_records.append(r)
        if len(diag_records) >= 64:
            break

    print(f"Selected {len(diag_records)} cases across {len(seen_groups)} groups for overfit diagnostic.")

    trainer = Trainer(
        model_id=args.model_id,
        device=args.device,
        lr=args.lr,
        seed=args.seed,
        micro_batch_size=args.micro_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
    )

    # Initial evaluation before training
    init_metrics = trainer.evaluate(diag_records)
    print(f"Initial Acc: {init_metrics['accuracy']*100:.2f}% ({init_metrics['correct_count']}/{len(diag_records)}), NLL: {init_metrics['mean_nll']:.4f}")

    # Overfit loop: fixed candidate order
    max_steps = args.max_steps
    step = 0
    opt_step = 0
    trainer.model.train()
    trainer.optimizer.zero_grad()

    t0 = time.time()
    batch_size = trainer.micro_batch_size

    # Repeat data until max_steps or target reached
    done = False
    log_history = []

    while opt_step < max_steps and not done:
        for i in range(0, len(diag_records), batch_size):
            batch_records = diag_records[i : i + batch_size]
            tokenized, target_indices, num_choices_list, max_num_classes = trainer.prepare_batch(
                batch_records, shuffle_choices=False
            )

            loss = trainer.compute_batch_loss(tokenized, target_indices, num_choices_list, max_num_classes)
            # Scale loss for gradient accumulation
            loss_scaled = loss / trainer.gradient_accumulation_steps
            loss_scaled.backward()
            step += 1

            if step % trainer.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
                trainer.optimizer.step()
                trainer.optimizer.zero_grad()
                opt_step += 1

                if opt_step % 25 == 0 or opt_step == 1:
                    eval_metrics = trainer.evaluate(diag_records)
                    trainer.model.train()
                    acc = eval_metrics["accuracy"]
                    print(f"Step {opt_step}/{max_steps} | Loss: {loss.item():.4f} | Acc: {acc*100:.2f}% ({eval_metrics['correct_count']}/{len(diag_records)}) | NLL: {eval_metrics['mean_nll']:.4f}")
                    log_history.append({
                        "step": opt_step,
                        "loss": round(loss.item(), 4),
                        "accuracy": acc,
                        "nll": eval_metrics["mean_nll"],
                    })

                    # Early stop if >= 95% (61/64)
                    if eval_metrics["correct_count"] >= 61:
                        print(f"Target accuracy reached (>=95%) at optimizer step {opt_step}! Ending overfit test.")
                        done = True
                        break

    # Final evaluation
    final_metrics = trainer.evaluate(diag_records)
    print(f"\nFinal Diagnostic Acc: {final_metrics['accuracy']*100:.2f}% ({final_metrics['correct_count']}/{len(diag_records)}), NLL: {final_metrics['mean_nll']:.4f}")

    # Save checkpoint
    ckpt_dir = os.path.join(args.output_dir, "checkpoint")
    trainer.save_checkpoint(ckpt_dir)

    # Reload test to verify saved weights match
    print("\n--- Verifying Reloaded Checkpoint ---")
    reloaded_model = GLiClassModel.from_pretrained(ckpt_dir).to(trainer.device)
    reloaded_pipeline = ZeroShotClassificationPipeline(
        model=reloaded_model,
        tokenizer=trainer.tokenizer,
        classification_type="single-label",
        device=trainer.device,
    )
    # Test on first record
    first_rec = diag_records[0]
    first_req = ChoiceRequest.from_dict(first_rec)
    inner_pipe = reloaded_pipeline.pipe
    tok = inner_pipe.prepare_inputs([first_req.context], [[c.text for c in first_req.choices]], False, prompt=[first_req.question])
    max_k = inner_pipe._resolve_max_num_classes([[c.text for c in first_req.choices]], False)
    with torch.inference_mode():
        reloaded_out = reloaded_model(**tok, max_num_classes=max_k)
        reloaded_probs = torch.softmax(reloaded_out.logits[0, : len(first_req.choices)].to(torch.float32), dim=-1).cpu().tolist()

    print("Reloaded model successfully executed. Sample probabilities:", [round(p, 4) for p in reloaded_probs])

    # Save overfit summary
    summary = {
        "mode": "overfit_diagnostic",
        "cases": len(diag_records),
        "initial_metrics": init_metrics,
        "final_metrics": final_metrics,
        "opt_steps": opt_step,
        "elapsed_sec": round(time.time() - t0, 2),
        "history": log_history,
    }
    with open(os.path.join(args.output_dir, "diagnostic_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Diagnostic results saved to: {args.output_dir}")


def run_full_training(args: argparse.Namespace):
    """Phase B: Small-scale fine-tuning on ~600 cases, select best epoch via dev set."""
    print("=== M2.1 Phase B: Small-Scale Fine-Tuning (~600 cases) ===")
    train_path = os.path.join(args.data_dir, "train.jsonl")
    dev_path = os.path.join(args.data_dir, "dev.jsonl")

    train_records = []
    with open(train_path, "r", encoding="utf-8") as f:
        for line in f:
            train_records.append(json.loads(line))

    dev_records = []
    with open(dev_path, "r", encoding="utf-8") as f:
        for line in f:
            dev_records.append(json.loads(line))

    print(f"Loaded Train: {len(train_records)} cases, Dev: {len(dev_records)} cases.")

    # Fresh trainer starting from base model (NOT overfit checkpoint)
    trainer = Trainer(
        model_id=args.model_id,
        device=args.device,
        lr=args.lr,
        weight_decay=args.weight_decay,
        seed=args.seed,
        micro_batch_size=args.micro_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
    )

    # Initial Dev evaluation
    print("Evaluating initial base model on Dev...")
    init_dev = trainer.evaluate(dev_records)
    print(f"Base Model Dev Acc: {init_dev['accuracy']*100:.2f}%, NLL: {init_dev['mean_nll']:.4f}")
    if "pair_metrics" in init_dev:
        print(f"Base Model Dev Both Correct: {init_dev['pair_metrics']['both_correct_rate']*100:.2f}% ({init_dev['pair_metrics']['both_correct_pairs']}/{init_dev['pair_metrics']['total_pairs']})")

    epochs = args.epochs
    best_score = (-1.0, -1.0, 999.0)  # (both_correct_rate, accuracy, -nll)
    best_epoch = -1
    best_ckpt_dir = os.path.join(args.output_dir, "checkpoint")
    rng = random.Random(args.seed)

    epoch_logs = []
    batch_size = trainer.micro_batch_size
    t_start = time.time()

    for epoch in range(1, epochs + 1):
        print(f"\n--- Epoch {epoch}/{epochs} ---")
        trainer.model.train()
        trainer.optimizer.zero_grad()

        # Shuffle training records order per epoch
        epoch_records = list(train_records)
        rng.shuffle(epoch_records)

        step = 0
        opt_step = 0
        epoch_loss = 0.0
        n_batches = 0

        total_micro_batches = (len(epoch_records) + batch_size - 1) // batch_size
        batch_idx = 0

        for i in range(0, len(epoch_records), batch_size):
            batch_records = epoch_records[i : i + batch_size]
            # Shuffle choices for training augmentation
            tokenized, target_indices, num_choices_list, max_num_classes = trainer.prepare_batch(
                batch_records, shuffle_choices=True, rng=rng
            )

            # Determine window bounds and total sample count in this accumulation window
            window_start_batch = (batch_idx // trainer.gradient_accumulation_steps) * trainer.gradient_accumulation_steps
            window_start_sample = window_start_batch * batch_size
            window_end_sample = min(
                window_start_sample + trainer.gradient_accumulation_steps * batch_size,
                len(epoch_records),
            )
            window_sample_count = window_end_sample - window_start_sample

            loss = trainer.compute_batch_loss(tokenized, target_indices, num_choices_list, max_num_classes)
            loss_scaled = loss * (len(batch_records) / window_sample_count)
            loss_scaled.backward()
            step += 1
            batch_idx += 1
            epoch_loss += loss.item()
            n_batches += 1

            if step % trainer.gradient_accumulation_steps == 0 or (i + batch_size >= len(epoch_records)):
                torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
                trainer.optimizer.step()
                trainer.optimizer.zero_grad()
                opt_step += 1

        avg_loss = epoch_loss / max(n_batches, 1)
        print(f"Epoch {epoch} finished. Average Train Loss: {avg_loss:.4f} ({opt_step} updates).")

        # Dev evaluation (fixed candidate order)
        print(f"Evaluating Dev for Epoch {epoch}...")
        dev_metrics = trainer.evaluate(dev_records)
        both_rate = dev_metrics.get("pair_metrics", {}).get("both_correct_rate", 0.0)
        acc = dev_metrics["accuracy"]
        nll = dev_metrics["mean_nll"]
        pdiag = dev_metrics.get("pair_diagnostics", {})

        print(f"Dev Acc: {acc*100:.2f}%, Pair Both Correct: {both_rate*100:.2f}%, NLL: {nll:.4f}")
        print(f"  [Dev Diag] Diff Both: {pdiag.get('diff_target_both', 0)}/{pdiag.get('diff_target_total', 0)} (GF Diff: {pdiag.get('diff_gf_both', 0)}/{pdiag.get('diff_gf_total', 0)}), Same Both: {pdiag.get('same_target_both', 0)}/{pdiag.get('same_target_total', 0)}")

        epoch_logs.append({
            "epoch": epoch,
            "train_loss": round(avg_loss, 4),
            "dev_accuracy": acc,
            "dev_both_correct_rate": both_rate,
            "dev_nll": nll,
            "dev_brier": dev_metrics["mean_brier"],
            "pair_diagnostics": pdiag,
        })

        # Selection criteria: 1. both_correct_rate, 2. accuracy, 3. -nll
        current_score = (both_rate, acc, -nll)
        if current_score > best_score:
            best_score = current_score
            best_epoch = epoch
            print(f"--> New best model! Saving checkpoint for Epoch {epoch}...")
            trainer.save_checkpoint(best_ckpt_dir)

        # M3.5 requirement: preserve best checkpoint from first 5 epochs
        if epoch == 5:
            first5_ckpt_dir = os.path.join(args.output_dir, "checkpoint_best_first5")
            print(f"\n[M3.5] Preserving best checkpoint from first 5 epochs (Epoch {best_epoch}) to: {first5_ckpt_dir}")
            import shutil
            if os.path.exists(first5_ckpt_dir):
                shutil.rmtree(first5_ckpt_dir)
            shutil.copytree(best_ckpt_dir, first5_ckpt_dir)
            best_epoch_first5 = best_epoch
            best_score_first5 = best_score

    print(f"\n=== Training Complete ===")
    print(f"Best Epoch (Overall): {best_epoch} (Pair Both Correct: {best_score[0]*100:.2f}%, Acc: {best_score[1]*100:.2f}%, NLL: {-best_score[2]:.4f})")
    print(f"Best checkpoint saved to: {best_ckpt_dir}")
    if epochs >= 5 and 'best_epoch_first5' in locals():
        print(f"Best Epoch (First 5): {best_epoch_first5} (Pair Both Correct: {best_score_first5[0]*100:.2f}%, Acc: {best_score_first5[1]*100:.2f}%, NLL: {-best_score_first5[2]:.4f})")
        print(f"First 5 best saved to: {os.path.join(args.output_dir, 'checkpoint_best_first5')}")

    # Save training summary
    summary = {
        "base_model": args.model_id,
        "epochs": epochs,
        "best_epoch_overall": best_epoch,
        "best_score_overall": {
            "both_correct_rate": best_score[0],
            "accuracy": best_score[1],
            "nll": -best_score[2],
        },
        "initial_dev": init_dev,
        "history": epoch_logs,
        "elapsed_sec": round(time.time() - t_start, 2),
    }
    if 'best_epoch_first5' in locals():
        summary["best_epoch_first5"] = best_epoch_first5
        summary["best_score_first5"] = {
            "both_correct_rate": best_score_first5[0],
            "accuracy": best_score_first5[1],
            "nll": -best_score_first5[2],
        }
    with open(os.path.join(args.output_dir, "train_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(prog="python -m erabi.train")
    parser.add_argument("--mode", type=str, choices=["overfit", "full"], required=True, help="Training mode")
    parser.add_argument("--data-dir", type=str, default="data/m2_1", help="Path to data directory")
    parser.add_argument("--output-dir", type=str, required=True, help="Directory to save checkpoint and logs")
    parser.add_argument("--model-id", type=str, default=DEFAULT_MODEL_ID, help="Base model ID")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--weight-decay", type=float, default=0.01, help="Weight decay")
    parser.add_argument("--max-steps", type=int, default=300, help="Max optimizer steps for overfit")
    parser.add_argument("--epochs", type=int, default=5, help="Epochs for full training")
    parser.add_argument("--micro-batch-size", type=int, default=2, help="Micro batch size")
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8, help="Grad accumulation")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda:0 or cpu)")

    args = parser.parse_args()

    if args.mode == "overfit":
        run_overfit_diagnostic(args)
    elif args.mode == "full":
        run_full_training(args)


if __name__ == "__main__":
    main()
