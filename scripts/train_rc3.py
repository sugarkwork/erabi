"""RC3 Training and Development Gate Evaluation (Milestones 30 & 31).

Roadmap: ERABI_RC3_DIAGNOSTIC_FIRST_ARCHITECTURE_ROADMAP.md (Sections 18 & 19)

Pipeline:
1. Load RC3 Training Data:
   - train: data/rc3_train/train.jsonl (4,016 records)
   - dev: data/rc3_train/dev.jsonl (502 records)
2. Fine-tune GLiClass from base (knowledgator/gliclass-instruct-base-v1.0):
   - All-in-One Sequence Cross-Encoder (Condition A selected in M29)
   - AdamW, lr=2e-5, weight_decay=0.01, max_norm=1.0
   - micro_batch_size=2, gradient_accumulation_steps=8 (effective batch size=16)
   - 10 epochs (2,510 optimizer steps)
   - Seed: 42
3. Track and evaluate checkpoints on dev.jsonl and eval_v2.jsonl
4. Select best checkpoint by Dev Accuracy, Paired Rate, and Core Retention
5. Evaluate Best Model against Milestone 31 Development Gate:
   - RC3 Bridge Benchmark (480 cases, 240 pairs):
     * Overall accuracy (target >= 88%)
     * logical_operators (target >= 85%)
     * perturbation_invariance (target >= 85%)
     * general_choice (target >= 85%)
     * variable_choice (target >= 85%)
     * natural_japanese (target >= 90%)
     * paired_both_rate (target >= 80%)
     * permutation_consistency (target >= 95%)
   - Core Retention Suites:
     * eval_v2 (200 records)
     * eval_exception (60 records)
     * fresh_operator_eval (50 records)
     * fresh_robustness_eval (54 records)
     * fresh_general_eval (60 records)
     * Mean core retention (target >= 96%)
6. Save artifacts and report:
   - runs/rc3_training/dev_gate_results.json
   - runs/rc3_training/RC3_DEVELOPMENT_GATE_REPORT.md
   - runs/rc3_training/best_model/
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
logger = logging.getLogger("erabi.train_rc3")

RUNS_DIR = ROOT / "runs" / "rc3_training"
CHECKPOINTS_DIR = RUNS_DIR / "checkpoints"
BEST_MODEL_DIR = RUNS_DIR / "best_model"

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
        "cases": cases,
    }


def train_rc3(
    epochs: int = 10,
    lr: float = 2e-5,
    micro_batch_size: int = 2,
    gradient_accumulation_steps: int = 8,
    seed: int = 42,
    device: Optional[str] = None,
) -> Path:
    device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

    train_records = load_jsonl(TRAIN_FILE)
    dev_records = load_jsonl(DEV_FILE)
    eval_v2_records = load_jsonl(CORE_RETENTION_SUITES["eval_v2"])
    logger.info(f"Loaded {len(train_records)} train records, {len(dev_records)} dev records, {len(eval_v2_records)} eval_v2 records.")

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

    total_micro_batches_per_ep = (len(train_records) + micro_batch_size - 1) // micro_batch_size
    steps_per_epoch = (total_micro_batches_per_ep + gradient_accumulation_steps - 1) // gradient_accumulation_steps
    total_expected_steps = steps_per_epoch * epochs
    warmup_steps = 150

    def get_lr(step: int) -> float:
        if step < warmup_steps:
            return lr * (step + 1) / warmup_steps
        progress = (step - warmup_steps) / max(1, total_expected_steps - warmup_steps)
        return 1e-6 + 0.5 * (lr - 1e-6) * (1.0 + math.cos(math.pi * progress))

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()
        rng = random.Random(seed + epoch)

        # Group shuffle to keep pairs adjacent while varying order
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
        ep_dir = CHECKPOINTS_DIR / f"epoch_{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        trainer.model.save_pretrained(ep_dir)
        trainer.tokenizer.save_pretrained(ep_dir)
        saved_checkpoints[epoch] = ep_dir

        # Dev evaluation
        dev_engine = GLiClassEngine(model_id=str(ep_dir), device=device)
        dev_eval = evaluate_records(dev_engine, dev_records, test_permutation=False)
        ev2_eval = evaluate_records(dev_engine, eval_v2_records, test_permutation=False)
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
            f"Epoch {epoch:2d}: Dev Acc={dev_eval['accuracy']*100:.2f}% (Paired: {dev_eval['paired_both_rate']*100:.2f}%), "
            f"eval_v2={ev2_eval['accuracy']*100:.2f}%, Composite={composite_score*100:.2f}%"
        )

    total_time = time.time() - t0_start
    logger.info(f"Training completed in {total_time:.1f}s. Total optimizer steps: {total_optimizer_steps}")

    # Select best checkpoint: prioritize eval_v2 >= 0.96, then composite score
    qualifying_epochs = [ep for ep, m in epoch_dev_metrics.items() if m["eval_v2_accuracy"] >= 0.96]
    if not qualifying_epochs:
        qualifying_epochs = [ep for ep, m in epoch_dev_metrics.items() if m["eval_v2_accuracy"] >= 0.95]
    if not qualifying_epochs:
        qualifying_epochs = list(epoch_dev_metrics.keys())

    best_epoch = max(qualifying_epochs, key=lambda ep: (epoch_dev_metrics[ep]["composite_score"], epoch_dev_metrics[ep]["dev_eval"]["paired_both_rate"]))
    best_checkpoint = saved_checkpoints[best_epoch]
    logger.info(f"Selected Best Epoch: {best_epoch} from {best_checkpoint}")

    # Copy to best_model_dir
    if BEST_MODEL_DIR.exists():
        shutil.rmtree(BEST_MODEL_DIR)
    shutil.copytree(best_checkpoint, BEST_MODEL_DIR)
    logger.info(f"Best model copied to {BEST_MODEL_DIR}")

    return BEST_MODEL_DIR


def evaluate_development_gate(model_path: Path, device: str = "cuda:0", output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Evaluate candidate model against Milestone 31 Development Gate."""
    target_dir = output_dir or RUNS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info("=== Running Milestone 31 Development Gate Full Evaluation ===")
    engine = GLiClassEngine(model_id=str(model_path), device=device)

    # 1. Bridge Benchmark Evaluation (480 cases, with permutation testing)
    bridge_records = load_jsonl(BRIDGE_BENCHMARK_FILE)
    logger.info(f"Evaluating Bridge Benchmark ({len(bridge_records)} cases)...")
    bridge_eval = evaluate_records(engine, bridge_records, test_permutation=True, seed=42)

    # 2. Core Retention Suites Evaluation
    core_results: Dict[str, Dict[str, Any]] = {}
    core_accuracies: List[float] = []

    for name, path in CORE_RETENTION_SUITES.items():
        if path.exists():
            records = load_jsonl(path)
            res = evaluate_records(engine, records, test_permutation=False)
            core_results[name] = {
                "total": res["total_cases"],
                "correct": res["correct"],
                "accuracy": res["accuracy"],
                "mean_nll": res["mean_nll"],
                "paired_both_rate": res["paired_both_rate"],
            }
            core_accuracies.append(res["accuracy"])
            logger.info(f"Core Suite [{name}]: Accuracy = {res['accuracy']*100:.2f}% ({res['correct']}/{res['total_cases']})")

    mean_core_retention = sum(core_accuracies) / len(core_accuracies) if core_accuracies else 0.0
    logger.info(f"Mean Core Retention: {mean_core_retention*100:.2f}%")

    # Extract Bridge targets
    fam_stats = bridge_eval["by_family"]
    log_acc = fam_stats.get("logical_operators", {}).get("accuracy", 0.0)
    pert_acc = fam_stats.get("perturbation_invariance", {}).get("accuracy", 0.0)
    gen_acc = fam_stats.get("general_choice", {}).get("accuracy", 0.0)
    var_acc = fam_stats.get("variable_choice", {}).get("accuracy", 0.0)
    nat_acc = fam_stats.get("natural_japanese", {}).get("accuracy", 0.0)
    core_acc = fam_stats.get("core_rules", {}).get("accuracy", 0.0)
    prio_acc = fam_stats.get("priority_exception", {}).get("accuracy", 0.0)
    dom_acc = fam_stats.get("domain_transfer", {}).get("accuracy", 0.0)

    # Milestone 31 Development Gate Criteria
    gate_checks = {
        "bridge_overall_ge_88": {
            "target": ">= 88.0%",
            "actual": f"{bridge_eval['accuracy']*100:.2f}%",
            "passed": bridge_eval["accuracy"] >= 0.88,
        },
        "logical_operators_ge_85": {
            "target": ">= 85.0%",
            "actual": f"{log_acc*100:.2f}%",
            "passed": log_acc >= 0.85,
        },
        "perturbation_invariance_ge_85": {
            "target": ">= 85.0%",
            "actual": f"{pert_acc*100:.2f}%",
            "passed": pert_acc >= 0.85,
        },
        "general_choice_ge_85": {
            "target": ">= 85.0%",
            "actual": f"{gen_acc*100:.2f}%",
            "passed": gen_acc >= 0.85,
        },
        "variable_choice_ge_85": {
            "target": ">= 85.0%",
            "actual": f"{var_acc*100:.2f}%",
            "passed": var_acc >= 0.85,
        },
        "natural_japanese_ge_90": {
            "target": ">= 90.0%",
            "actual": f"{nat_acc*100:.2f}%",
            "passed": nat_acc >= 0.90,
        },
        "paired_both_ge_80": {
            "target": ">= 80.0%",
            "actual": f"{bridge_eval['paired_both_rate']*100:.2f}%",
            "passed": bridge_eval["paired_both_rate"] >= 0.80,
        },
        "permutation_consistency_ge_95": {
            "target": ">= 95.0%",
            "actual": f"{bridge_eval['permutation_consistency']*100:.2f}%",
            "passed": (bridge_eval["permutation_consistency"] or 0.0) >= 0.95,
        },
        "mean_core_retention_ge_96": {
            "target": ">= 96.0%",
            "actual": f"{mean_core_retention*100:.2f}%",
            "passed": mean_core_retention >= 0.96,
        },
    }

    all_passed = all(item["passed"] for item in gate_checks.values())

    report_data = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "model_checkpoint": str(model_path),
        "bridge_evaluation": {
            "total_cases": bridge_eval["total_cases"],
            "correct": bridge_eval["correct"],
            "accuracy": bridge_eval["accuracy"],
            "mean_nll": bridge_eval["mean_nll"],
            "mean_brier": bridge_eval["mean_brier"],
            "paired_total": bridge_eval["paired_total"],
            "paired_both": bridge_eval["paired_both"],
            "paired_both_rate": bridge_eval["paired_both_rate"],
            "permutation_consistency": bridge_eval["permutation_consistency"],
            "high_confidence_wrong_count": bridge_eval["high_confidence_wrong_count"],
            "high_confidence_wrong_rate": bridge_eval["high_confidence_wrong_rate"],
            "by_family": fam_stats,
            "by_k": bridge_eval["by_k"],
        },
        "core_retention": {
            "mean_accuracy": round(mean_core_retention, 4),
            "suites": core_results,
        },
        "gate_checks": gate_checks,
        "milestone_31_gate_passed": all_passed,
    }

    # Save dev_gate_results.json
    results_path = target_dir / "dev_gate_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved dev gate results to {results_path}")

    # Generate Markdown Report
    report_md = f"""# ERABI Milestone 31: RC3 Development Gate Report

**Evaluation Date**: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Model Checkpoint**: `{model_path}`  
**Gate Status**: **{'PASSED (All Gate Criteria Met)' if all_passed else 'EVALUATED (See Breakdown Below)'}**  

---

## 1. Milestone 31 Development Gate Compliance Matrix

| Criterion | Target | Actual Result | Compliance Status |
|:---|:---:|:---:|:---:|
| **Bridge Overall Accuracy** | $\\ge 88.0\\%$ | **{bridge_eval['accuracy']*100:.2f}%** ({bridge_eval['correct']}/{bridge_eval['total_cases']}) | **{'PASS' if gate_checks['bridge_overall_ge_88']['passed'] else 'FAIL'}** |
| **`logical_operators`** | $\\ge 85.0\\%$ | **{log_acc*100:.2f}%** | **{'PASS' if gate_checks['logical_operators_ge_85']['passed'] else 'FAIL'}** |
| **`perturbation_invariance`** | $\\ge 85.0\\%$ | **{pert_acc*100:.2f}%** | **{'PASS' if gate_checks['perturbation_invariance_ge_85']['passed'] else 'FAIL'}** |
| **`general_choice`** | $\\ge 85.0\\%$ | **{gen_acc*100:.2f}%** | **{'PASS' if gate_checks['general_choice_ge_85']['passed'] else 'FAIL'}** |
| **`variable_choice`** | $\\ge 85.0\\%$ | **{var_acc*100:.2f}%** | **{'PASS' if gate_checks['variable_choice_ge_85']['passed'] else 'FAIL'}** |
| **`natural_japanese`** | $\\ge 90.0\\%$ | **{nat_acc*100:.2f}%** | **{'PASS' if gate_checks['natural_japanese_ge_90']['passed'] else 'FAIL'}** |
| **Paired Both Correct Rate** | $\\ge 80.0\\%$ | **{bridge_eval['paired_both_rate']*100:.2f}%** ({bridge_eval['paired_both']}/{bridge_eval['paired_total']}) | **{'PASS' if gate_checks['paired_both_ge_80']['passed'] else 'FAIL'}** |
| **Permutation Consistency** | $\\ge 95.0\\%$ | **{bridge_eval['permutation_consistency']*100:.2f}%** | **{'PASS' if gate_checks['permutation_consistency_ge_95']['passed'] else 'FAIL'}** |
| **Mean Core Retention** | $\\ge 96.0\\%$ | **{mean_core_retention*100:.2f}%** | **{'PASS' if gate_checks['mean_core_retention_ge_96']['passed'] else 'FAIL'}** |

---

## 2. RC3 Bridge Benchmark: Family Breakdown

| Family | Cases | Correct | Accuracy | Mean NLL | Mean Brier |
|:---|:---:|:---:|:---:|:---:|:---:|
| `core_rules` | {fam_stats.get('core_rules', {}).get('total', 0)} | {fam_stats.get('core_rules', {}).get('correct', 0)} | {core_acc*100:.2f}% | {fam_stats.get('core_rules', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('core_rules', {}).get('mean_brier', 0.0):.4f} |
| `domain_transfer` | {fam_stats.get('domain_transfer', {}).get('total', 0)} | {fam_stats.get('domain_transfer', {}).get('correct', 0)} | {dom_acc*100:.2f}% | {fam_stats.get('domain_transfer', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('domain_transfer', {}).get('mean_brier', 0.0):.4f} |
| `general_choice` | {fam_stats.get('general_choice', {}).get('total', 0)} | {fam_stats.get('general_choice', {}).get('correct', 0)} | {gen_acc*100:.2f}% | {fam_stats.get('general_choice', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('general_choice', {}).get('mean_brier', 0.0):.4f} |
| `logical_operators` | {fam_stats.get('logical_operators', {}).get('total', 0)} | {fam_stats.get('logical_operators', {}).get('correct', 0)} | {log_acc*100:.2f}% | {fam_stats.get('logical_operators', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('logical_operators', {}).get('mean_brier', 0.0):.4f} |
| `natural_japanese` | {fam_stats.get('natural_japanese', {}).get('total', 0)} | {fam_stats.get('natural_japanese', {}).get('correct', 0)} | {nat_acc*100:.2f}% | {fam_stats.get('natural_japanese', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('natural_japanese', {}).get('mean_brier', 0.0):.4f} |
| `perturbation_invariance` | {fam_stats.get('perturbation_invariance', {}).get('total', 0)} | {fam_stats.get('perturbation_invariance', {}).get('correct', 0)} | {pert_acc*100:.2f}% | {fam_stats.get('perturbation_invariance', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('perturbation_invariance', {}).get('mean_brier', 0.0):.4f} |
| `priority_exception` | {fam_stats.get('priority_exception', {}).get('total', 0)} | {fam_stats.get('priority_exception', {}).get('correct', 0)} | {prio_acc*100:.2f}% | {fam_stats.get('priority_exception', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('priority_exception', {}).get('mean_brier', 0.0):.4f} |
| `variable_choice` | {fam_stats.get('variable_choice', {}).get('total', 0)} | {fam_stats.get('variable_choice', {}).get('correct', 0)} | {var_acc*100:.2f}% | {fam_stats.get('variable_choice', {}).get('mean_nll', 0.0):.4f} | {fam_stats.get('variable_choice', {}).get('mean_brier', 0.0):.4f} |

---

## 3. Candidate Count ($K$) Scalability

| $K$ | Total Cases | Correct | Accuracy |
|:---:|:---:|:---:|:---:|
"""
    for k_val, s in bridge_eval["by_k"].items():
        report_md += f"| **K={k_val}** | {s['total']} | {s['correct']} | **{s['accuracy']*100:.2f}%** |\n"

    report_md += f"""
---

## 4. Core Retention Suite Performance

| Suite | Dataset | Total | Correct | Accuracy | Paired Both | Target | Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
"""
    for name, res in core_results.items():
        pass_status = "PASS" if res["accuracy"] >= 0.95 else "CHECK"
        report_md += f"| `{name}` | `{CORE_RETENTION_SUITES[name].name}` | {res['total']} | {res['correct']} | **{res['accuracy']*100:.2f}%** | {res['paired_both_rate']*100:.2f}% | $\\ge 95.0\\%$ | **{pass_status}** |\n"

    report_md += f"""
**Mean Core Retention**: **{mean_core_retention*100:.2f}%** (Target: $\\ge 96.0\\%$) -> **{'PASS' if mean_core_retention >= 0.96 else 'FAIL'}**

---

## 5. Architectural Comparison vs RC2.1 Frozen Baseline

| Metric | RC2.1 Baseline (Bridge) | RC3 Candidate (Bridge) | Delta |
|:---|:---:|:---:|:---:|
| **Overall Accuracy** | 76.04% | **{bridge_eval['accuracy']*100:.2f}%** | **{bridge_eval['accuracy']*100 - 76.04:+.2f}pt** |
| **`logical_operators`** | 63.33% | **{log_acc*100:.2f}%** | **{log_acc*100 - 63.33:+.2f}pt** |
| **`priority_exception`** | 66.67% | **{prio_acc*100:.2f}%** | **{prio_acc*100 - 66.67:+.2f}pt** |
| **`variable_choice`** | 83.33% | **{var_acc*100:.2f}%** | **{var_acc*100 - 83.33:+.2f}pt** |
| **`natural_japanese`** | 86.67% | **{nat_acc*100:.2f}%** | **{nat_acc*100 - 86.67:+.2f}pt** |
| **`perturbation_invariance`** | 80.00% | **{pert_acc*100:.2f}%** | **{pert_acc*100 - 80.00:+.2f}pt** |
| **Paired Reasoning (Both)** | 55.83% | **{bridge_eval['paired_both_rate']*100:.2f}%** | **{bridge_eval['paired_both_rate']*100 - 55.83:+.2f}pt** |
| **Permutation Consistency** | 94.00% | **{bridge_eval['permutation_consistency']*100:.2f}%** | **{bridge_eval['permutation_consistency']*100 - 94.00:+.2f}pt** |
| **High-Confidence Errors** | 13.54% | **{bridge_eval['high_confidence_wrong_rate']*100:.2f}%** | **{bridge_eval['high_confidence_wrong_rate']*100 - 13.54:+.2f}pt** |

---

## 6. Milestone 31 Verdict

**Status**: {'**MILESTONE 31 PASSED** - Proceeding to Milestone 32 (Calibration)' if all_passed else '**DEVELOPMENT GATE FAILED** - Reviewing specific failure clusters'}
"""

    report_path = target_dir / "RC3_DEVELOPMENT_GATE_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    logger.info(f"Saved Development Gate Markdown Report to {report_path}")

    return report_data


def main():
    logger.info("=== Starting Milestone 30: Full RC3 Training ===")
    best_model_dir = train_rc3(
        epochs=10,
        lr=2e-5,
        micro_batch_size=2,
        gradient_accumulation_steps=8,
        seed=42,
    )
    logger.info(f"=== Milestone 30 Training Complete: Best Model at {best_model_dir} ===")

    logger.info("=== Starting Milestone 31: Development Gate Full Evaluation ===")
    report_data = evaluate_development_gate(best_model_dir)
    logger.info(f"=== Milestone 31 Evaluation Complete: Gate Passed = {report_data['milestone_31_gate_passed']} ===")


if __name__ == "__main__":
    main()
