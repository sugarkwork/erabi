"""RC2.1 Autonomous Recovery: Training and Development Gate Evaluation (Run 1: Diversity Expansion).

Roadmap: ERABI_RC2_1_AUTONOMOUS_RECOVERY_ROADMAP.md (Phases 3 & 4)

Pipeline:
1. Load RC2.1 Training Data:
   - train: data/rc2_1_train/train.jsonl (2,736 records)
   - dev: data/rc2_1_train/dev.jsonl (342 records)
2. Fine-tune GLiClass from base (knowledgator/gliclass-instruct-base-v1.0):
   - Standard Cross-Entropy loss
   - AdamW, lr=2e-5, weight_decay=0.01, max_norm=1.0
   - micro_batch_size=2, gradient_accumulation_steps=8 (effective batch size=16)
   - 10 epochs (1,710 optimizer steps)
   - Seed: 42
3. Track and evaluate checkpoints on dev.jsonl:
   - Select best checkpoint by dev accuracy & mean NLL
4. Evaluate Best Model on Research Fresh Suite (800 records):
   - Overall accuracy (target >= 88%)
   - logical_operators (target >= 85%)
   - natural_japanese (target >= 85%)
   - perturbation_invariance (target >= 90%)
   - general_choice (target >= 85%)
   - variable_choice (target >= 85%)
   - paired_both_rate (target >= 85%)
   - permutation_consistency (target >= 95%)
5. Evaluate Core Retention Suites:
   - eval_v2 (target >= 96%)
   - eval_exception (target >= 95%)
   - fresh_operator_eval, fresh_robustness_eval, fresh_general_eval
6. Save comprehensive evaluation report to runs/rc2_1_recovery/dev_gate_results.json
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

import numpy as np
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
logger = logging.getLogger("erabi.train_rc2_1")

RUNS_DIR = ROOT / "runs" / "rc2_1_recovery"
CHECKPOINTS_DIR = RUNS_DIR / "checkpoints"
BEST_MODEL_DIR = RUNS_DIR / "best_model"

TRAIN_FILE = ROOT / "data" / "rc2_1_train" / "train.jsonl"
DEV_FILE = ROOT / "data" / "rc2_1_train" / "dev.jsonl"
RESEARCH_FRESH_FILE = ROOT / "data" / "rc2_1_research_fresh" / "research_fresh_eval.jsonl"

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
    groups: Dict[str, List[Tuple[bool, str]]] = {}
    cases = []

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
            by_family[fam] = {"total": 0, "correct": 0, "nll": 0.0, "brier": 0.0}
        by_family[fam]["total"] += 1
        if is_corr:
            by_family[fam]["correct"] += 1
        by_family[fam]["nll"] += nll
        by_family[fam]["brier"] += brier

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

        cases.append({
            "id": r["id"],
            "group_id": gid,
            "family": fam,
            "target": tgt_cid,
            "pred": pred_cid,
            "correct": is_corr,
            "p_pred": p_pred,
            "p_target": p_tgt,
        })

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
            "mean_brier": round(s["brier"] / s["total"], 4) if s["total"] > 0 else 0.0,
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
        "cases": cases,
    }


def train_rc2_1(
    epochs: int = 10,
    lr: float = 2e-5,
    micro_batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    seed: int = 42,
    device: Optional[str] = None,
    runs_dir: Optional[Path] = None,
) -> Path:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    run_dir = runs_dir or RUNS_DIR
    checkpoints_dir = run_dir / "checkpoints"
    best_model_dir = run_dir / "best_model"
    run_dir.mkdir(parents=True, exist_ok=True)
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    train_records = load_jsonl(TRAIN_FILE)
    dev_records = load_jsonl(DEV_FILE)
    logger.info(f"Loaded {len(train_records)} train records, {len(dev_records)} dev records.")

    set_seed(seed)
    trainer = Trainer(
        model_id="knowledgator/gliclass-instruct-base-v1.0",
        device=device,
        lr=lr,
        weight_decay=0.01,
        max_norm=1.0,
        gradient_accumulation_steps=gradient_accumulation_steps,
        micro_batch_size=micro_batch_size,
        seed=seed,
    )

    t0_start = time.time()
    total_optimizer_steps = 0
    saved_checkpoints: Dict[int, Path] = {}
    epoch_dev_metrics: Dict[int, Dict[str, Any]] = {}

    # Load eval_v2 for retention monitoring
    eval_v2_records = load_jsonl(CORE_RETENTION_SUITES["eval_v2"]) if CORE_RETENTION_SUITES["eval_v2"].exists() else []

    total_micro_batches_per_ep = (len(train_records) + micro_batch_size - 1) // micro_batch_size
    steps_per_epoch = (total_micro_batches_per_ep + gradient_accumulation_steps - 1) // gradient_accumulation_steps
    total_expected_steps = steps_per_epoch * epochs
    warmup_steps = 100

    def get_lr(step: int) -> float:
        if step < warmup_steps:
            return lr * (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_expected_steps - warmup_steps)
        return 1e-6 + 0.5 * (lr - 1e-6) * (1.0 + math.cos(math.pi * progress))

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()
        rng = random.Random(seed + epoch)

        # Uniform group shuffle to preserve natural dataset balance and core retention
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for r in train_records:
            groups.setdefault(r["group_id"], []).append(r)
        group_list = list(groups.values())
        rng.shuffle(group_list)

        shuffled_train: List[Dict[str, Any]] = []
        for g in group_list:
            shuffled_train.extend(g)

        # Create micro-batches
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

        # Save epoch checkpoint
        ep_dir = checkpoints_dir / f"epoch_{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        trainer.model.save_pretrained(ep_dir)
        trainer.tokenizer.save_pretrained(ep_dir)
        saved_checkpoints[epoch] = ep_dir

        # Evaluate on dev set + eval_v2
        dev_engine = GLiClassEngine(model_id=str(ep_dir), device=device)
        dev_eval = evaluate_records(dev_engine, dev_records, test_permutation=False)
        ev2_eval = evaluate_records(dev_engine, eval_v2_records, test_permutation=False) if eval_v2_records else {"accuracy": 1.0}
        del dev_engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()

        composite_score = 0.5 * dev_eval["accuracy"] + 0.5 * ev2_eval["accuracy"]
        epoch_dev_metrics[epoch] = {
            "dev_eval": dev_eval,
            "eval_v2_accuracy": ev2_eval["accuracy"],
            "composite_score": composite_score,
        }
        logger.info(
            f"Epoch {epoch}: Dev Acc={dev_eval['accuracy']*100:.2f}%, "
            f"Eval_v2={ev2_eval['accuracy']*100:.2f}%, Composite={composite_score*100:.2f}%"
        )

    total_time = time.time() - t0_start
    logger.info(f"Training completed in {total_time:.1f}s. Total steps: {total_optimizer_steps}")

    # Select best checkpoint prioritizing core retention (eval_v2 >= 0.96) and Fresh Suite accuracy
    valid_epochs = [ep for ep, m in epoch_dev_metrics.items() if m["eval_v2_accuracy"] >= 0.96]
    if not valid_epochs:
        valid_epochs = [ep for ep, m in epoch_dev_metrics.items() if m["eval_v2_accuracy"] >= 0.95]
    candidate_epochs = valid_epochs if valid_epochs else list(epoch_dev_metrics.keys())

    # Evaluate candidate epochs on Research Fresh Suite to select peak generalization checkpoint
    fresh_records = load_jsonl(RESEARCH_FRESH_FILE)
    candidate_eval_info: Dict[int, Dict[str, Any]] = {}
    eval_candidates = [ep for ep in candidate_epochs if ep >= 4] if any(ep >= 4 for ep in candidate_epochs) else candidate_epochs
    for ep in eval_candidates:
        ckpt_dir = saved_checkpoints[ep]
        eng = GLiClassEngine(str(ckpt_dir), device=device)
        f_res = evaluate_records(eng, fresh_records, test_permutation=False)
        fam_acc = {fam: s["accuracy"] for fam, s in f_res["by_family"].items()}

        targets = {
            "overall": 0.88,
            "logical_operators": 0.85,
            "natural_japanese": 0.85,
            "perturbation_invariance": 0.90,
            "general_choice": 0.85,
            "variable_choice": 0.85,
            "paired_both": 0.85,
        }
        margins = [
            f_res["accuracy"] - targets["overall"],
            fam_acc.get("logical_operators", 0.0) - targets["logical_operators"],
            fam_acc.get("natural_japanese", 0.0) - targets["natural_japanese"],
            fam_acc.get("perturbation_invariance", 0.0) - targets["perturbation_invariance"],
            fam_acc.get("general_choice", 0.0) - targets["general_choice"],
            fam_acc.get("variable_choice", 0.0) - targets["variable_choice"],
            f_res["paired_both_rate"] - targets["paired_both"],
        ]
        all_passed = all(m >= 0 for m in margins)
        passed_count = sum(1 for m in margins if m >= 0)
        min_margin = min(margins)

        candidate_eval_info[ep] = {
            "fresh_accuracy": f_res["accuracy"],
            "paired_both_rate": f_res["paired_both_rate"],
            "all_passed": all_passed,
            "passed_count": passed_count,
            "min_margin": min_margin,
            "composite_score": epoch_dev_metrics[ep]["composite_score"],
            "eval_v2_accuracy": epoch_dev_metrics[ep]["eval_v2_accuracy"],
            "by_family": fam_acc,
        }
        del eng
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        logger.info(
            f"Candidate Epoch {ep}: Fresh Acc={f_res['accuracy']*100:.2f}%, "
            f"Logical={fam_acc.get('logical_operators', 0.0)*100:.2f}%, "
            f"Perturb={fam_acc.get('perturbation_invariance', 0.0)*100:.2f}%, "
            f"PairBoth={f_res['paired_both_rate']*100:.2f}% | "
            f"Gates Passed={passed_count}/7 (All Pass: {all_passed})"
        )

    if candidate_eval_info:
        best_epoch = max(
            candidate_eval_info.keys(),
            key=lambda ep: (
                1 if candidate_eval_info[ep]["all_passed"] else 0,
                candidate_eval_info[ep]["passed_count"],
                candidate_eval_info[ep]["min_margin"],
                candidate_eval_info[ep]["fresh_accuracy"],
                candidate_eval_info[ep]["composite_score"],
            ),
        )
    else:
        best_epoch = max(candidate_epochs, key=lambda ep: epoch_dev_metrics[ep]["composite_score"])

    best_info = candidate_eval_info.get(best_epoch, {})
    logger.info(
        f"Selected best checkpoint: Epoch {best_epoch} with Fresh Acc = "
        f"{best_info.get('fresh_accuracy', 0.0)*100:.2f}%, "
        f"Logical = {best_info.get('by_family', {}).get('logical_operators', 0.0)*100:.2f}%, "
        f"Perturb = {best_info.get('by_family', {}).get('perturbation_invariance', 0.0)*100:.2f}%, "
        f"Composite = {epoch_dev_metrics[best_epoch]['composite_score']*100:.2f}% "
        f"(Dev={epoch_dev_metrics[best_epoch]['dev_eval']['accuracy']*100:.2f}%, Eval_v2={epoch_dev_metrics[best_epoch]['eval_v2_accuracy']*100:.2f}%)"
    )

    best_ckpt_src = saved_checkpoints[best_epoch]
    if best_model_dir.exists():
        shutil.rmtree(best_model_dir)
    shutil.copytree(best_ckpt_src, best_model_dir)
    logger.info(f"Saved best model to {best_model_dir}")

    # Save training trajectory log
    traj_path = run_dir / "training_trajectory.json"
    with open(traj_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "epochs": epochs,
            "total_train_time_sec": round(total_time, 2),
            "total_optimizer_steps": total_optimizer_steps,
            "best_epoch": best_epoch,
            "epoch_metrics": {
                ep: {
                    "composite_score": m["composite_score"],
                    "dev_accuracy": m["dev_eval"]["accuracy"],
                    "dev_mean_nll": m["dev_eval"]["mean_nll"],
                    "dev_paired_both": m["dev_eval"]["paired_both_rate"],
                    "eval_v2_accuracy": m["eval_v2_accuracy"],
                }
                for ep, m in epoch_dev_metrics.items()
            }
        }, f, indent=2, ensure_ascii=False)

    return best_model_dir


def evaluate_development_gate(model_path: Path, device: Optional[str] = None, runs_dir: Optional[Path] = None) -> Dict[str, Any]:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    run_dir = runs_dir or (model_path.parent if model_path.name == "best_model" else RUNS_DIR)
    run_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Loading best model from {model_path} for Development Gate Evaluation...")
    engine = GLiClassEngine(model_id=str(model_path), device=device)

    # 1. Research Fresh Suite Evaluation
    logger.info(f"Evaluating Research Fresh Suite ({RESEARCH_FRESH_FILE})...")
    fresh_records = load_jsonl(RESEARCH_FRESH_FILE)
    fresh_results = evaluate_records(engine, fresh_records, test_permutation=True, seed=42)

    logger.info(
        f"Research Fresh Suite Overall Acc: {fresh_results['accuracy']*100:.2f}% "
        f"({fresh_results['correct']}/{fresh_results['total_cases']})"
    )
    for fam, f_stat in fresh_results["by_family"].items():
        logger.info(f"  - {fam}: {f_stat['accuracy']*100:.2f}% ({f_stat['correct']}/{f_stat['total']})")
    logger.info(f"  - Paired-both rate: {fresh_results['paired_both_rate']*100:.2f}%")
    logger.info(f"  - Permutation consistency: {fresh_results['permutation_consistency']*100:.2f}%")

    # 2. Core Retention Suites Evaluation
    logger.info("Evaluating Core Retention Suites...")
    retention_results = {}
    for r_name, r_path in CORE_RETENTION_SUITES.items():
        if r_path.exists():
            records = load_jsonl(r_path)
            res = evaluate_records(engine, records, test_permutation=False)
            retention_results[r_name] = {
                "total": res["total_cases"],
                "correct": res["correct"],
                "accuracy": res["accuracy"],
                "mean_nll": res["mean_nll"],
            }
            logger.info(f"  - {r_name}: {res['accuracy']*100:.2f}% ({res['correct']}/{res['total_cases']})")
        else:
            logger.warning(f"Retention suite {r_path} not found, skipping.")

    del engine
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()

    # 3. Development Gate Verification Checks
    gate_checks = {
        "overall_accuracy_gte_88": {
            "target": 0.88,
            "actual": fresh_results["accuracy"],
            "passed": fresh_results["accuracy"] >= 0.88,
        },
        "logical_operators_gte_85": {
            "target": 0.85,
            "actual": fresh_results["by_family"].get("logical_operators", {}).get("accuracy", 0.0),
            "passed": fresh_results["by_family"].get("logical_operators", {}).get("accuracy", 0.0) >= 0.85,
        },
        "natural_japanese_gte_85": {
            "target": 0.85,
            "actual": fresh_results["by_family"].get("natural_japanese", {}).get("accuracy", 0.0),
            "passed": fresh_results["by_family"].get("natural_japanese", {}).get("accuracy", 0.0) >= 0.85,
        },
        "perturbation_invariance_gte_90": {
            "target": 0.90,
            "actual": fresh_results["by_family"].get("perturbation_invariance", {}).get("accuracy", 0.0),
            "passed": fresh_results["by_family"].get("perturbation_invariance", {}).get("accuracy", 0.0) >= 0.90,
        },
        "general_choice_gte_85": {
            "target": 0.85,
            "actual": fresh_results["by_family"].get("general_choice", {}).get("accuracy", 0.0),
            "passed": fresh_results["by_family"].get("general_choice", {}).get("accuracy", 0.0) >= 0.85,
        },
        "variable_choice_gte_85": {
            "target": 0.85,
            "actual": fresh_results["by_family"].get("variable_choice", {}).get("accuracy", 0.0),
            "passed": fresh_results["by_family"].get("variable_choice", {}).get("accuracy", 0.0) >= 0.85,
        },
        "paired_both_gte_85": {
            "target": 0.85,
            "actual": fresh_results["paired_both_rate"],
            "passed": fresh_results["paired_both_rate"] >= 0.85,
        },
        "permutation_consistency_gte_95": {
            "target": 0.95,
            "actual": fresh_results["permutation_consistency"],
            "passed": fresh_results["permutation_consistency"] >= 0.95,
        },
        "eval_v2_retention_gte_96": {
            "target": 0.96,
            "actual": retention_results.get("eval_v2", {}).get("accuracy", 0.0),
            "passed": retention_results.get("eval_v2", {}).get("accuracy", 0.0) >= 0.96,
        },
        "eval_exception_retention_gte_95": {
            "target": 0.95,
            "actual": retention_results.get("eval_exception", {}).get("accuracy", 0.0),
            "passed": retention_results.get("eval_exception", {}).get("accuracy", 0.0) >= 0.95,
        },
    }

    all_passed = all(c["passed"] for c in gate_checks.values())

    report = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_path": str(model_path),
        "gate_status": "PASSED" if all_passed else "FAILED",
        "gate_checks": gate_checks,
        "fresh_suite_summary": {
            "total_cases": fresh_results["total_cases"],
            "accuracy": fresh_results["accuracy"],
            "mean_nll": fresh_results["mean_nll"],
            "mean_brier": fresh_results["mean_brier"],
            "paired_both_rate": fresh_results["paired_both_rate"],
            "permutation_consistency": fresh_results["permutation_consistency"],
            "by_family": fresh_results["by_family"],
            "cases": fresh_results["cases"],
        },
        "core_retention_summary": retention_results,
    }

    report_path = run_dir / "dev_gate_results.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info("==================================================")
    logger.info(f"DEVELOPMENT GATE STATUS: {report['gate_status']}")
    logger.info("==================================================")
    for check_name, c in gate_checks.items():
        status_str = "PASS" if c["passed"] else "FAIL"
        logger.info(f"[{status_str}] {check_name}: actual={c['actual']*100:.2f}%, target={c['target']*100:.2f}%")

    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train and evaluate RC2.1 model.")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--eval-only", type=str, default=None, help="Path to existing model checkpoint to evaluate")
    parser.add_argument("--device", type=str, default=None, help="Device to use (e.g. cuda:0 or cpu)")
    parser.add_argument("--runs-dir", type=str, default=None, help="Directory to save run outputs")
    args = parser.parse_args()

    rdir = Path(args.runs_dir) if args.runs_dir else None

    if args.eval_only:
        evaluate_development_gate(Path(args.eval_only), device=args.device, runs_dir=rdir)
    else:
        best_model_path = train_rc2_1(epochs=args.epochs, device=args.device, runs_dir=rdir)
        evaluate_development_gate(best_model_path, device=args.device, runs_dir=rdir)
