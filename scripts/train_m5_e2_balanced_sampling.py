"""Milestone 5 Experiment 2: Task-Balanced Sampling Training Script (ERABI).

Roadmap Reference:
Section 18: "全eligible epochでretention低い → task-balanced sampling / curriculumを試す。"
Budget: Experiment 2 of 3 for Milestone 5.

Pre-registered Hypothesis:
Under uniform random shuffling, the model frequently experiences consecutive batches
dominated by M4 priority override rules, inducing gradient drift toward heuristic shortcuts
(e.g., HP/item tokens immediately trigger action), overriding M3 inclusive/exclusive comparison
and composite AND/OR logic. By strictly pairing 1 Core Logic/Retention record with 1 Priority/Phrasing
record in every micro-batch of 2 (guaranteeing exact 50/50 balance in every gradient accumulation
window), the optimizer simultaneously penalizes priority shortcut violations on core logic at every step,
allowing eval_v2 to reach >= 97.0% while maintaining fresh phrasing generalization >= 60%.

Data streams:
- Stream A (Core Logic & Retention): 712 records (600 M3 train + 112 Retention Replay)
- Stream B (Priority & Phrasing): 480 records (240 M4.1 exception + 240 M4.3.1 phrasing)
Every micro-batch: [1 from Stream A, 1 from Stream B].
Every gradient accumulation window (8 micro-batches = 16 samples): exactly 8 Core + 8 Priority.

Outputs:
- runs/m5_e2_balanced/checkpoints/
- runs/m5_e2_balanced/training_summary.json
- runs/m5_e2_balanced/evaluation_report.json
- runs/m5_e2_balanced/notes.md
"""

from __future__ import annotations

import json
import logging
import os
import random
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.train import Trainer, set_seed
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m5_e2_balanced")

OUT_DIR = ROOT / "runs/m5_e2_balanced"
CKPT_DIR = OUT_DIR / "checkpoints"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CKPT_DIR.mkdir(parents=True, exist_ok=True)

M3_TRAIN_FILE = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN_FILE = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN_FILE = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"
AUDIT_FILE = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"

DEV_FILE = ROOT / "data/m4_3_1_phrasing_fix/combined_dev.jsonl"

DATASETS = {
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "fresh_phrasing_eval": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
}


def load_balanced_data_streams() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    # 1. Load M3 train (600)
    m3_train = [json.loads(l) for l in open(M3_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m3_by_id = {r["id"]: r for r in m3_train}

    # Load replay IDs from M4.4.1 audit
    audit = json.load(open(AUDIT_FILE, encoding="utf-8"))
    r1_gids = set(audit["r1_equality_boundary"]["group_ids"])
    r1b_gids = set(audit["r1b_equality_comparison"]["group_ids"])

    r2_gids = set()
    for st_info in audit["r2_composite_logic"]["states"].values():
        r2_gids.update(st_info["selected_group_ids"])

    replay_gids = r1_gids | r1b_gids | r2_gids
    replay_records = [r for r in m3_train if r["group_id"] in replay_gids]
    assert len(replay_records) == 112, f"Expected 112 replay records, got {len(replay_records)}"

    # Stream A: Core Logic & Retention (600 + 112 = 712)
    stream_a = m3_train + replay_records
    assert len(stream_a) == 712, f"Expected 712 in Stream A, got {len(stream_a)}"

    # Stream B: Priority & Phrasing (240 + 240 = 480)
    m4_1_train = [json.loads(l) for l in open(M4_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m4_3_1_train = [json.loads(l) for l in open(M4_3_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    stream_b = m4_1_train + m4_3_1_train
    assert len(stream_b) == 480, f"Expected 480 in Stream B, got {len(stream_b)}"

    return stream_a, stream_b


def evaluate_dev(trainer: Trainer, dev_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    trainer.model.eval()
    inner_pipe = trainer.pipeline.pipe

    results = []
    with torch.inference_mode():
        for row in dev_records:
            req = ChoiceRequest.from_dict(row)
            labels = [c.text for c in req.choices]
            target_cid = row["target"]["choice_id"]
            target_idx = next(i for i, c in enumerate(req.choices) if c.id == target_cid)

            tokenized = inner_pipe.prepare_inputs(
                texts=[req.context],
                labels=[labels],
                same_labels=False,
                prompt=[req.question],
            )
            max_num_classes = inner_pipe._resolve_max_num_classes([labels], same_labels=False)
            outputs = trainer.model(**tokenized, max_num_classes=max_num_classes)
            sample_logits = outputs.logits[0, : len(labels)].to(torch.float32)

            pred_idx = int(torch.argmax(sample_logits).item())
            is_corr = (pred_idx == target_idx)

            log_probs = F.log_softmax(sample_logits.to(torch.float64), dim=-1)
            nll_val = -float(log_probs[target_idx].item())

            results.append({
                "id": row.get("id"),
                "group_id": row.get("group_id"),
                "is_correct": is_corr,
                "target_cid": target_cid,
                "task_family": row.get("task_family"),
                "nll": nll_val,
            })

    # M3 subset (100)
    m3_res = [r for r in results if r.get("task_family") in ["explicit_rule", "goal_following"]]
    m3_acc = sum(1 for r in m3_res if r["is_correct"]) / len(m3_res) if m3_res else 0.0

    # M4.1 subset (40)
    m41_res = [r for r in results if r.get("task_family") == "exception_priority"]
    m41_acc = sum(1 for r in m41_res if r["is_correct"]) / len(m41_res) if m41_res else 0.0

    # Phrasing subset (80)
    phr_res = [r for r in results if r.get("task_family") in ["phrasing_diversification", "phrasing_diversification_fix"]]
    phr_acc = sum(1 for r in phr_res if r["is_correct"]) / len(phr_res) if phr_res else 0.0
    phr_nll = sum(r["nll"] for r in phr_res) / len(phr_res) if phr_res else 0.0

    phr_groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in phr_res:
        gid = r.get("group_id")
        if gid:
            phr_groups.setdefault(gid, []).append(r)

    phr_diff_both = 0
    phr_diff_pairs = 0
    for gid, pair in phr_groups.items():
        if len(pair) == 2:
            if pair[0]["target_cid"] != pair[1]["target_cid"]:
                phr_diff_pairs += 1
                if pair[0]["is_correct"] and pair[1]["is_correct"]:
                    phr_diff_both += 1

    return {
        "m3_accuracy": m3_acc,
        "m4_1_accuracy": m41_acc,
        "phrasing_accuracy": phr_acc,
        "phrasing_nll": phr_nll,
        "phrasing_diff_both": phr_diff_both,
        "phrasing_diff_pairs": phr_diff_pairs,
    }


def evaluate_dataset_with_engine(engine: GLiClassEngine, dataset_path: Path) -> Dict[str, Any]:
    records = [json.loads(line) for line in open(dataset_path, encoding="utf-8") if line.strip()]
    results = []
    total_nll = 0.0
    correct_count = 0

    for row in records:
        req = ChoiceRequest.from_dict(row)
        tgt_cid = row["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        resp = engine.predict(req, temperature=1.0, return_logits=True)
        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        log_probs = F.log_softmax(torch.tensor(resp.raw_logits, dtype=torch.float64), dim=-1)
        total_nll += -float(log_probs[tgt_idx].item())

        results.append({
            "id": row.get("id"),
            "group_id": row.get("group_id"),
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
        })

    n = len(records)
    metrics: Dict[str, Any] = {
        "count": n,
        "correct_count": correct_count,
        "accuracy": correct_count / n,
        "mean_nll": total_nll / n,
    }

    groups: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        gid = r.get("group_id")
        if gid:
            groups.setdefault(gid, []).append(r)

    total_pairs = 0
    pair_both = 0
    diff_pairs = 0
    diff_both = 0
    same_pairs = 0
    same_both = 0

    for gid, pair in groups.items():
        if len(pair) == 2:
            total_pairs += 1
            r1, r2 = pair[0], pair[1]
            is_both = (r1["is_correct"] and r2["is_correct"])
            if is_both:
                pair_both += 1
            if r1["target"] != r2["target"]:
                diff_pairs += 1
                if is_both:
                    diff_both += 1
            else:
                same_pairs += 1
                if is_both:
                    same_both += 1

    if total_pairs > 0:
        metrics["total_pairs"] = total_pairs
        metrics["pair_both"] = pair_both
        metrics["pair_both_rate"] = pair_both / total_pairs
        metrics["diff_pairs"] = diff_pairs
        metrics["diff_both"] = diff_both
        metrics["diff_both_rate"] = (diff_both / diff_pairs) if diff_pairs > 0 else 0.0
        metrics["same_pairs"] = same_pairs
        metrics["same_both"] = same_both
        metrics["same_both_rate"] = (same_both / same_pairs) if same_pairs > 0 else 0.0

    return metrics


def check_m5_gate(eval_res: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    passed = True
    reasons = []

    # 1. eval_v2
    ev2 = eval_res.get("eval_v2", {})
    ev2_acc = ev2.get("accuracy", 0.0)
    ev2_diff = ev2.get("diff_both_rate", 0.0)
    if ev2_acc < 0.97:
        passed = False
        reasons.append(f"eval_v2 accuracy {ev2_acc*100:.1f}% < 97.0%")
    if ev2_diff < 0.88:
        passed = False
        reasons.append(f"eval_v2 diff both {ev2_diff*100:.1f}% < 88.0%")

    # 2. fresh_phrasing_eval
    fr = eval_res.get("fresh_phrasing_eval", {})
    fr_acc = fr.get("accuracy", 0.0)
    fr_diff = fr.get("diff_both_rate", 0.0)
    fr_same = fr.get("same_both_rate", 0.0)
    if fr_acc < 0.80:
        passed = False
        reasons.append(f"fresh phrasing accuracy {fr_acc*100:.1f}% < 80.0%")
    if fr_diff < 0.60:
        passed = False
        reasons.append(f"fresh phrasing diff both {fr_diff*100:.1f}% < 60.0%")
    if fr_same < 0.75:
        passed = False
        reasons.append(f"fresh phrasing same both {fr_same*100:.1f}% < 75.0%")

    # 3. eval_exception
    exc = eval_res.get("eval_exception", {})
    exc_acc = exc.get("accuracy", 0.0)
    exc_diff = exc.get("diff_both_rate", 0.0)
    if exc_acc < 0.98:
        passed = False
        reasons.append(f"eval_exception accuracy {exc_acc*100:.1f}% < 98.0%")
    if exc_diff < 0.95:
        passed = False
        reasons.append(f"eval_exception diff both {exc_diff*100:.1f}% < 95.0%")

    # 4. smoke_cases
    smk = eval_res.get("smoke_cases", {})
    smk_corr = smk.get("correct_count", 0)
    if smk_corr < 10:
        passed = False
        reasons.append(f"smoke cases {smk_corr}/12 < 10/12")

    return passed, reasons


def main():
    set_seed(42)
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info("=== ERABI Milestone 5 Experiment 2: Task-Balanced Sampling ===")
    logger.info(f"Using device: {device}")

    stream_a, stream_b = load_balanced_data_streams()
    logger.info(f"Stream A (Core Logic & Retention): {len(stream_a)} records")
    logger.info(f"Stream B (Priority & Phrasing):    {len(stream_b)} records")

    dev_records = [json.loads(line) for line in open(DEV_FILE, encoding="utf-8") if line.strip()]
    logger.info(f"Loaded {len(dev_records)} dev records.")

    trainer = Trainer(
        model_id="knowledgator/gliclass-instruct-base-v1.0",
        device=device,
        lr=2e-5,
        weight_decay=0.01,
        max_norm=1.0,
        gradient_accumulation_steps=8,
        micro_batch_size=2,
        seed=42,
    )

    epochs = 10
    SAVE_EPOCHS = [6, 7, 8, 9, 10]
    saved_paths: Dict[int, Path] = {}

    t0_train = time.time()

    for epoch in range(1, epochs + 1):
        t0_ep = time.time()
        trainer.model.train()

        rng = random.Random(42 + epoch)

        # Shuffle each stream independently
        shuffled_a = list(stream_a)
        shuffled_b = list(stream_b)
        rng.shuffle(shuffled_a)
        rng.shuffle(shuffled_b)

        # Build 1-to-1 task-balanced micro-batches:
        # Each micro-batch has [1 Core sample, 1 Priority sample]
        # Iterate over all 712 Core samples, cycle through 480 Priority samples
        micro_batches = []
        n_a = len(shuffled_a)  # 712
        n_b = len(shuffled_b)  # 480

        for i in range(n_a):
            rec_a = shuffled_a[i]
            rec_b = shuffled_b[i % n_b]
            # Randomize within-pair order
            if rng.random() < 0.5:
                pair = [rec_a, rec_b]
            else:
                pair = [rec_b, rec_a]
            micro_batches.append(pair)

        # Shuffle the sequence of micro-batches across the epoch
        rng.shuffle(micro_batches)

        total_loss = 0.0
        num_windows = (len(micro_batches) + trainer.gradient_accumulation_steps - 1) // trainer.gradient_accumulation_steps

        for w_idx in range(num_windows):
            w_start = w_idx * trainer.gradient_accumulation_steps
            w_end = min(w_start + trainer.gradient_accumulation_steps, len(micro_batches))
            w_batches = micro_batches[w_start:w_end]

            w_total_samples = sum(len(b) for b in w_batches)
            trainer.optimizer.zero_grad()

            for b in w_batches:
                tokenized, target_indices, _, _ = trainer.prepare_batch(b, shuffle_choices=False, rng=rng)
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

        ep_duration = time.time() - t0_ep
        avg_loss = total_loss / (len(micro_batches) * 2)

        # Dev evaluation
        dev_m = evaluate_dev(trainer, dev_records)
        logger.info(
            f"Epoch {epoch:2d}/{epochs} | Loss: {avg_loss:.4f} | "
            f"M3 Acc: {dev_m['m3_accuracy']*100:.1f}% | "
            f"M4.1 Acc: {dev_m['m4_1_accuracy']*100:.1f}% | "
            f"Phr Acc: {dev_m['phrasing_accuracy']*100:.1f}% | "
            f"Phr Diff Both: {dev_m['phrasing_diff_both']}/{dev_m['phrasing_diff_pairs']} | "
            f"Phr NLL: {dev_m['phrasing_nll']:.4f} | {ep_duration:.1f}s"
        )

        if epoch in SAVE_EPOCHS:
            ep_dir = CKPT_DIR / f"epoch_{epoch}"
            ep_dir.mkdir(parents=True, exist_ok=True)
            trainer.model.save_pretrained(ep_dir)
            trainer.tokenizer.save_pretrained(ep_dir)
            saved_paths[epoch] = ep_dir
            logger.info(f"--> Saved checkpoint for Epoch {epoch} to {ep_dir}")

    train_time = time.time() - t0_train
    logger.info(f"Training finished in {train_time/60:.2f} minutes.")

    # Free trainer model memory
    del trainer
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # Evaluation Phase across all saved epochs
    logger.info("\n=== Evaluating Saved Epochs on M5 Gate Benchmark Suite ===")
    eval_results = {}
    best_m5_epoch = None
    best_m5_passed = False

    for ep in SAVE_EPOCHS:
        ckpt_path = saved_paths[ep]
        logger.info(f"\nEvaluating Epoch {ep} ({ckpt_path})...")
        engine = GLiClassEngine(model_id=str(ckpt_path), device=device)

        ep_metrics = {}
        for dname, dpath in DATASETS.items():
            met = evaluate_dataset_with_engine(engine, dpath)
            ep_metrics[dname] = met
            acc_str = f"Acc: {met['accuracy']*100:.1f}%"
            diff_str = f"Diff Both: {met.get('diff_both', 0)}/{met.get('diff_pairs', 0)} ({met.get('diff_both_rate', 0)*100:.1f}%)" if "diff_both" in met else ""
            logger.info(f"  {dname:20s} | {acc_str:15s} | {diff_str}")

        del engine
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        is_m5_pass, gate_reasons = check_m5_gate(ep_metrics)
        logger.info(f"Epoch {ep} M5 Gate Pass: {is_m5_pass} | Reasons: {gate_reasons if not is_m5_pass else 'ALL PASSED'}")

        eval_results[ep] = {
            "metrics": ep_metrics,
            "is_m5_pass": is_m5_pass,
            "gate_reasons": gate_reasons,
        }

        if is_m5_pass and not best_m5_passed:
            best_m5_passed = True
            best_m5_epoch = ep

    # Save evaluation summary
    report = {
        "experiment_name": "Milestone 5 Experiment 2: Task-Balanced Sampling",
        "saved_epochs": SAVE_EPOCHS,
        "best_m5_passed": best_m5_passed,
        "best_m5_epoch": best_m5_epoch,
        "results": eval_results,
    }
    with open(OUT_DIR / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Build Markdown report
    md_lines = [
        "# Milestone 5 Experiment 2: Task-Balanced Sampling Report\n",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## Multi-Epoch Benchmark Results\n",
        "| Epoch | eval_v2 Acc | eval_v2 Diff Both | fresh Acc | fresh Diff Both | eval_exception Acc | transfer_probe | smoke | M5 Gate |",
        "|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]

    for ep in SAVE_EPOCHS:
        m = eval_results[ep]["metrics"]
        ev2_acc = f"{m['eval_v2']['accuracy']*100:.1f}%"
        ev2_db = f"{m['eval_v2'].get('diff_both', 0)}/{m['eval_v2'].get('diff_pairs', 0)} ({m['eval_v2'].get('diff_both_rate', 0)*100:.1f}%)"
        fr_acc = f"{m['fresh_phrasing_eval']['accuracy']*100:.1f}%"
        fr_db = f"{m['fresh_phrasing_eval'].get('diff_both', 0)}/{m['fresh_phrasing_eval'].get('diff_pairs', 0)} ({m['fresh_phrasing_eval'].get('diff_both_rate', 0)*100:.1f}%)"
        exc_acc = f"{m['eval_exception']['accuracy']*100:.1f}%"
        tp_acc = f"{m['transfer_probe']['correct_count']}/32 ({m['transfer_probe']['accuracy']*100:.1f}%)"
        smk = f"{m['smoke_cases']['correct_count']}/12"
        gate_status = "**PASS**" if eval_results[ep]["is_m5_pass"] else "FAIL"

        md_lines.append(f"| Epoch {ep} | {ev2_acc} | {ev2_db} | {fr_acc} | {fr_db} | {exc_acc} | {tp_acc} | {smk} | {gate_status} |")

    md_lines.append(f"\n**M5 Gate Passed**: {best_m5_passed}")
    if best_m5_passed:
        md_lines.append(f"**Selected Passing Epoch**: Epoch {best_m5_epoch}")

    with open(OUT_DIR / "notes.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")


if __name__ == "__main__":
    main()
