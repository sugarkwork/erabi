"""RC3 Continual Fine-Tuning from Frozen RC2.1 Backbone.

Builds upon the frozen RC2.1 checkpoint (release/rc2_1/model, which achieved
76.04% Bridge accuracy and 97.90% core retention) by applying gentle
continual fine-tuning (lr=5e-6) on the RC3 training dataset.

Targets the root causes identified in Milestones 26 & 27:
- Lexical overlap hard negatives (Factorial Exp C)
- Propositional inversion & biconditional fallbacks (Cluster 2)
- Variable cardinality scaling K=4..16 (Cluster 1)
- Core retention preservation on eval_v2 (>= 96%)

Evaluates Bridge Benchmark (480 cases) and Core Retention at each epoch.
"""

from __future__ import annotations

import copy
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
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest
from erabi.train import Trainer, set_seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.train_rc3_continual")

RUNS_DIR = ROOT / "runs" / "rc3_continual"
CHECKPOINTS_DIR = RUNS_DIR / "checkpoints"
BEST_MODEL_DIR = RUNS_DIR / "best_model"

RC2_1_MODEL = ROOT / "release" / "rc2_1" / "model"
TRAIN_FILE = ROOT / "data" / "rc3_train" / "train.jsonl"
DEV_FILE = ROOT / "data" / "rc3_train" / "dev.jsonl"
BRIDGE_BENCHMARK_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"

CORE_RETENTION_SUITES = {
    "eval_v2": ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl",
    "eval_exception": ROOT / "data" / "m4_1_exception" / "eval_exception.jsonl",
    "fresh_operator_eval": ROOT / "data" / "m6_operator" / "fresh_operator_eval.jsonl",
    "fresh_robustness_eval": ROOT / "data" / "m7_robustness" / "fresh_robustness_eval.jsonl",
    "fresh_general_eval": ROOT / "data" / "m8_general_choice" / "fresh_general_eval.jsonl",
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def evaluate_records(
    engine: GLiClassEngine,
    records: List[Dict[str, Any]],
    test_permutation: bool = False,
    seed: int = 42,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    total = len(records)
    correct = 0
    total_nll = 0.0
    total_brier = 0.0
    high_conf_wrong = 0
    permuted_matches = 0

    by_family: Dict[str, Dict[str, Any]] = {}
    by_k: Dict[int, Dict[str, Any]] = {}
    groups: Dict[str, List[Tuple[bool, str]]] = {}

    for r in records:
        req = ChoiceRequest.from_dict(r)
        tgt_cid = r["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)
        one_hot = [1.0 if i == tgt_idx else 0.0 for i in range(len(req.choices))]

        resp = engine.predict(req, temperature=1.0, return_logits=True)
        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)

        if is_corr:
            correct += 1

        probs = [c.probability for c in resp.choices]
        pred_idx = next(i for i, c in enumerate(req.choices) if c.id == pred_cid)
        p_pred = probs[pred_idx]
        p_tgt = max(probs[tgt_idx], 1e-15)

        nll = -math.log(p_tgt)
        brier = sum((p - y) ** 2 for p, y in zip(probs, one_hot))

        total_nll += nll
        total_brier += brier

        if not is_corr and p_pred >= 0.90:
            high_conf_wrong += 1

        fam = r.get("family", "unknown")
        if fam not in by_family:
            by_family[fam] = {"total": 0, "correct": 0, "nll": 0.0}
        by_family[fam]["total"] += 1
        if is_corr:
            by_family[fam]["correct"] += 1
        by_family[fam]["nll"] += nll

        k = len(req.choices)
        if k not in by_k:
            by_k[k] = {"total": 0, "correct": 0}
        by_k[k]["total"] += 1
        if is_corr:
            by_k[k]["correct"] += 1

        gid = r.get("group_id", r.get("id"))
        if gid:
            groups.setdefault(gid, []).append((is_corr, tgt_cid))

        if test_permutation:
            r_perm = copy.deepcopy(r)
            choices_perm = list(r_perm["choices"])
            rng.shuffle(choices_perm)
            r_perm["choices"] = choices_perm
            req_perm = ChoiceRequest.from_dict(r_perm)
            resp_perm = engine.predict(req_perm, temperature=1.0)
            if resp_perm.best_candidate_id == pred_cid:
                permuted_matches += 1

    paired_total = 0
    paired_both = 0
    for gid, pair in groups.items():
        if len(pair) == 2:
            paired_total += 1
            if pair[0][0] and pair[1][0]:
                paired_both += 1

    family_stats = {}
    for fam, s in by_family.items():
        family_stats[fam] = {
            "total": s["total"],
            "correct": s["correct"],
            "accuracy": round(s["correct"] / s["total"], 4) if s["total"] > 0 else 0.0,
            "mean_nll": round(s["nll"] / s["total"], 4) if s["total"] > 0 else 0.0,
        }

    k_stats = {}
    for k, s in sorted(by_k.items()):
        k_stats[str(k)] = {
            "total": s["total"],
            "correct": s["correct"],
            "accuracy": round(s["correct"] / s["total"], 4) if s["total"] > 0 else 0.0,
        }

    return {
        "total_cases": total,
        "correct": correct,
        "accuracy": round(correct / total, 4) if total > 0 else 0.0,
        "mean_nll": round(total_nll / total, 4) if total > 0 else 0.0,
        "mean_brier": round(total_brier / total, 4) if total > 0 else 0.0,
        "paired_total": paired_total,
        "paired_both": paired_both,
        "paired_both_rate": round(paired_both / paired_total, 4) if paired_total > 0 else 0.0,
        "high_confidence_wrong_count": high_conf_wrong,
        "high_confidence_wrong_rate": round(high_conf_wrong / total, 4) if total > 0 else 0.0,
        "permutation_consistency": round(permuted_matches / total, 4) if test_permutation and total > 0 else None,
        "by_family": family_stats,
        "by_k": k_stats,
    }


def train_rc3_continual(
    epochs: int = 5,
    lr: float = 5e-6,
    micro_batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    seed: int = 42,
    device: Optional[str] = None,
    runs_dir: Optional[Path] = None,
) -> Path:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    r_dir = Path(runs_dir) if runs_dir else RUNS_DIR
    checkpoints_dir = r_dir / "checkpoints"
    best_model_dir = r_dir / "best_model"

    r_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    train_records = load_jsonl(TRAIN_FILE)
    dev_records = load_jsonl(DEV_FILE)
    bridge_records = load_jsonl(BRIDGE_BENCHMARK_FILE)
    eval_v2_records = load_jsonl(CORE_RETENTION_SUITES["eval_v2"])

    logger.info(
        f"=== Starting Continual Fine-Tuning from {RC2_1_MODEL} ===\n"
        f"Output Dir: {r_dir}\n"
        f"Train: {len(train_records)} | Dev: {len(dev_records)} | Bridge: {len(bridge_records)} | eval_v2: {len(eval_v2_records)}"
    )

    set_seed(seed)
    trainer = Trainer(
        model_id=str(RC2_1_MODEL),
        device=device,
        lr=lr,
        weight_decay=0.01,
        max_norm=1.0,
        gradient_accumulation_steps=gradient_accumulation_steps,
        micro_batch_size=micro_batch_size,
        seed=seed,
    )

    total_micro_batches_per_ep = (len(train_records) + micro_batch_size - 1) // micro_batch_size
    steps_per_epoch = (total_micro_batches_per_ep + gradient_accumulation_steps - 1) // gradient_accumulation_steps
    total_expected_steps = steps_per_epoch * epochs
    warmup_steps = 50

    def get_lr(step: int) -> float:
        if step < warmup_steps:
            return lr * (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_expected_steps - warmup_steps)
        return 1e-7 + 0.5 * (lr - 1e-7) * (1.0 + math.cos(math.pi * progress))

    t0_start = time.time()
    total_optimizer_steps = 0
    epoch_results: Dict[int, Dict[str, Any]] = {}

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()
        rng = random.Random(seed + epoch)

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in train_records:
            groups.setdefault(r["group_id"], []).append(r)
        group_list = list(groups.values())
        rng.shuffle(group_list)

        shuffled_train: List[Dict[str, Any]] = []
        for g in group_list:
            shuffled_train.extend(g)

        micro_batches = []
        for i in range(0, len(shuffled_train), micro_batch_size):
            micro_batches.append(shuffled_train[i:i + micro_batch_size])

        total_loss = 0.0
        num_windows = (len(micro_batches) + gradient_accumulation_steps - 1) // gradient_accumulation_steps

        for w_idx in range(num_windows):
            w_start = w_idx * gradient_accumulation_steps
            w_end = min(w_start + gradient_accumulation_steps, len(micro_batches))
            w_batches = micro_batches[w_start:w_end]
            w_total_samples = sum(len(b) for b in w_batches)

            cur_lr = get_lr(total_optimizer_steps)
            for param_group in trainer.optimizer.param_groups:
                param_group["lr"] = cur_lr

            trainer.optimizer.zero_grad()
            for b in w_batches:
                tokenized, target_indices, _, _ = trainer.prepare_batch(b, shuffle_choices=True, rng=rng)
                labels_count = [len(r["choices"]) for r in b]
                max_classes = max(labels_count)

                outputs = trainer.model(**tokenized, max_num_classes=max_classes)
                batch_loss = torch.tensor(0.0, device=trainer.device)
                for i, (tgt, l_cnt) in enumerate(zip(target_indices, labels_count)):
                    logits = outputs.logits[i, :l_cnt]
                    batch_loss = batch_loss + F.cross_entropy(logits.unsqueeze(0), torch.tensor([tgt], device=trainer.device))

                weighted_loss = batch_loss / w_total_samples
                weighted_loss.backward()
                total_loss += batch_loss.item()

            torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
            trainer.optimizer.step()
            total_optimizer_steps += 1

        ep_duration = time.time() - t0_ep
        avg_loss = total_loss / len(shuffled_train)
        logger.info(f"Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.4f} | LR: {cur_lr:.2e} | Steps: {total_optimizer_steps:4d} | Time: {ep_duration:.1f}s")

        # Save checkpoint
        ep_dir = checkpoints_dir / f"epoch_{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        trainer.model.save_pretrained(ep_dir)
        trainer.tokenizer.save_pretrained(ep_dir)

        # Evaluate on Bridge Benchmark + eval_v2 + dev set
        ep_engine = GLiClassEngine(model_id=str(ep_dir), device=device)
        dev_eval = evaluate_records(ep_engine, dev_records, test_permutation=False)
        ev2_eval = evaluate_records(ep_engine, eval_v2_records, test_permutation=False)
        bridge_eval = evaluate_records(ep_engine, bridge_records, test_permutation=True)
        del ep_engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        epoch_results[epoch] = {
            "checkpoint": str(ep_dir),
            "loss": avg_loss,
            "dev_acc": dev_eval["accuracy"],
            "eval_v2_acc": ev2_eval["accuracy"],
            "bridge_acc": bridge_eval["accuracy"],
            "bridge_paired": bridge_eval["paired_both_rate"],
            "bridge_perm": bridge_eval["permutation_consistency"],
            "bridge_families": bridge_eval["by_family"],
        }
        logger.info(
            f"Epoch {epoch:2d} EVAL -> Bridge Acc: {bridge_eval['accuracy']*100:.2f}% (Paired: {bridge_eval['paired_both_rate']*100:.2f}%, Perm: {bridge_eval['permutation_consistency']*100:.2f}%) | "
            f"eval_v2: {ev2_eval['accuracy']*100:.2f}% | Dev: {dev_eval['accuracy']*100:.2f}%"
        )

    total_time = time.time() - t0_start
    logger.info(f"Continual training completed in {total_time:.1f}s.")

    # Select best epoch by Bridge accuracy while ensuring eval_v2 >= 0.96
    qualifying = [ep for ep, m in epoch_results.items() if m["eval_v2_acc"] >= 0.96]
    if not qualifying:
        qualifying = [ep for ep, m in epoch_results.items() if m["eval_v2_acc"] >= 0.95]
    if not qualifying:
        qualifying = list(epoch_results.keys())

    best_ep = max(qualifying, key=lambda ep: (epoch_results[ep]["bridge_acc"], epoch_results[ep]["bridge_paired"]))
    best_cp = Path(epoch_results[best_ep]["checkpoint"])
    logger.info(f"Best Continual Checkpoint: Epoch {best_ep} ({best_cp}) with Bridge Acc = {epoch_results[best_ep]['bridge_acc']*100:.2f}%")

    if best_model_dir.exists():
        shutil.rmtree(best_model_dir)
    shutil.copytree(best_cp, best_model_dir)

    # Save summary
    summary_path = r_dir / "continual_training_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "base_checkpoint": str(RC2_1_MODEL),
            "best_epoch": best_ep,
            "best_bridge_acc": epoch_results[best_ep]["bridge_acc"],
            "epoch_results": epoch_results,
        }, f, indent=2, ensure_ascii=False)

    # Run full Milestone 31 Development Gate evaluation
    logger.info("=== Running Full Milestone 31 Development Gate Evaluation ===")
    from scripts.train_rc3 import evaluate_development_gate
    dev_gate_results = evaluate_development_gate(best_model_dir, device=device, output_dir=r_dir)
    logger.info(f"Dev Gate Complete: Gate Passed = {dev_gate_results['milestone_31_gate_passed']}")

    return best_model_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RC3 Continual Fine-Tuning")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--lr", type=float, default=4e-6, help="Peak learning rate")
    parser.add_argument("--runs-dir", type=str, default="runs/rc3_run3_curriculum", help="Directory to save runs")
    parser.add_argument("--device", type=str, default=None, help="Device to use")
    args = parser.parse_args()

    train_rc3_continual(
        epochs=args.epochs,
        lr=args.lr,
        runs_dir=Path(args.runs_dir) if args.runs_dir else None,
        device=args.device,
    )
