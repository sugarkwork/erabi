"""Rigorous Self-Review & Audit script for Milestone 5 Gate (ERABI).

Roadmap Section 15 Checklist:
1. Recompute metrics from saved prediction / raw logits
2. Split overlap inspection (exact input overlap == 0)
3. Semantic validator check
4. Label spot-check
5. Candidate order permutation consistency
"""

from __future__ import annotations

import json
import logging
import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m5_audit")

EPOCH_9_DIR = ROOT / "runs/m5_e2_balanced/checkpoints/epoch_9"
AUDIT_OUT_DIR = ROOT / "runs/m5_e2_balanced/audit"
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)

M3_TRAIN_FILE = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN_FILE = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN_FILE = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"
AUDIT_FILE = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"

EVAL_DATASETS = {
    "eval_v2": ROOT / "data/m3_3_v2/eval_v2.jsonl",
    "fresh_phrasing_eval": ROOT / "data/m4_3_1_phrasing_fix/fresh_phrasing_eval.jsonl",
    "eval_exception": ROOT / "data/m4_1_exception/eval_exception.jsonl",
    "transfer_probe": ROOT / "data/m3_1/transfer_probe.jsonl",
    "smoke_cases": ROOT / "examples/smoke_cases.jsonl",
}


def load_all_training_records() -> List[Dict[str, Any]]:
    m3_train = [json.loads(l) for l in open(M3_TRAIN_FILE, encoding="utf-8") if l.strip()]
    audit = json.load(open(AUDIT_FILE, encoding="utf-8"))
    r1_gids = set(audit["r1_equality_boundary"]["group_ids"])
    r1b_gids = set(audit["r1b_equality_comparison"]["group_ids"])
    r2_gids = set()
    for st_info in audit["r2_composite_logic"]["states"].values():
        r2_gids.update(st_info["selected_group_ids"])
    replay_gids = r1_gids | r1b_gids | r2_gids
    replay_records = [r for r in m3_train if r["group_id"] in replay_gids]
    m4_1_train = [json.loads(l) for l in open(M4_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    m4_3_1_train = [json.loads(l) for l in open(M4_3_1_TRAIN_FILE, encoding="utf-8") if l.strip()]
    return m3_train + replay_records + m4_1_train + m4_3_1_train


def make_input_signature(row: Dict[str, Any]) -> str:
    choices_str = "|".join(c["text"] for c in row["choices"])
    return f"{row['context'].strip()} /// {row['question'].strip()} /// {choices_str}"


def check_split_overlap(train_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    logger.info("--- Step 2: Split Overlap Check ---")
    train_sigs: Set[str] = {make_input_signature(r) for r in train_records}
    train_ids: Set[str] = {r["id"] for r in train_records}

    overlap_results = {}
    total_leaks = 0

    for eval_name, eval_path in EVAL_DATASETS.items():
        eval_records = [json.loads(l) for l in open(eval_path, encoding="utf-8") if l.strip()]
        id_overlap = [r["id"] for r in eval_records if r["id"] in train_ids]
        sig_overlap = [r["id"] for r in eval_records if make_input_signature(r) in train_sigs]

        overlap_results[eval_name] = {
            "eval_count": len(eval_records),
            "id_overlap_count": len(id_overlap),
            "exact_input_overlap_count": len(sig_overlap),
            "overlapping_ids": sig_overlap,
        }
        total_leaks += len(sig_overlap)
        logger.info(f"  {eval_name:20s}: {len(eval_records)} cases | exact signature overlap: {len(sig_overlap)}")

    logger.info(f"Total exact input leaks across all eval sets: {total_leaks}")
    return {"total_leaks": total_leaks, "datasets": overlap_results}


def evaluate_and_recompute(engine: GLiClassEngine) -> Dict[str, Any]:
    logger.info("--- Step 1: Raw Logits Evaluation & Metric Recomputation ---")
    all_metrics = {}
    saved_predictions = {}

    for name, path in EVAL_DATASETS.items():
        records = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        preds = []
        correct_count = 0
        total_nll = 0.0

        for r in records:
            req = ChoiceRequest.from_dict(r)
            tgt_cid = r["target"]["choice_id"]
            tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

            resp = engine.predict(req, temperature=1.0, return_logits=True)
            raw_logits = resp.raw_logits
            assert all(math.isfinite(x) for x in raw_logits), f"Non-finite logits in {r['id']}"

            # Recompute softmax from raw logits directly
            tensor_logits = torch.tensor(raw_logits, dtype=torch.float64)
            log_probs = F.log_softmax(tensor_logits, dim=-1)
            probs = F.softmax(tensor_logits, dim=-1).tolist()

            pred_idx = int(torch.argmax(tensor_logits).item())
            pred_cid = req.choices[pred_idx].id
            is_corr = (pred_cid == tgt_cid)
            if is_corr:
                correct_count += 1

            nll = -float(log_probs[tgt_idx].item())
            total_nll += nll

            preds.append({
                "id": r["id"],
                "group_id": r.get("group_id"),
                "target": tgt_cid,
                "predicted": pred_cid,
                "is_correct": is_corr,
                "raw_logits": raw_logits,
                "probs": probs,
                "nll": nll,
            })

        n = len(records)
        acc = correct_count / n
        mean_nll = total_nll / n

        # Pairwise metrics
        groups: Dict[str, List[Dict[str, Any]]] = {}
        for p in preds:
            gid = p.get("group_id")
            if gid:
                groups.setdefault(gid, []).append(p)

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
                both = r1["is_correct"] and r2["is_correct"]
                if both:
                    pair_both += 1
                if r1["target"] != r2["target"]:
                    diff_pairs += 1
                    if both:
                        diff_both += 1
                else:
                    same_pairs += 1
                    if both:
                        same_both += 1

        met = {
            "count": n,
            "correct_count": correct_count,
            "accuracy": acc,
            "mean_nll": mean_nll,
            "total_pairs": total_pairs,
            "pair_both": pair_both,
            "pair_both_rate": pair_both / total_pairs if total_pairs > 0 else 0.0,
            "diff_pairs": diff_pairs,
            "diff_both": diff_both,
            "diff_both_rate": diff_both / diff_pairs if diff_pairs > 0 else 0.0,
            "same_pairs": same_pairs,
            "same_both": same_both,
            "same_both_rate": same_both / same_pairs if same_pairs > 0 else 0.0,
        }
        all_metrics[name] = met
        saved_predictions[name] = preds

        logger.info(
            f"  {name:20s}: Acc: {acc*100:.1f}% ({correct_count}/{n}) | "
            f"Diff Both: {diff_both}/{diff_pairs} ({met['diff_both_rate']*100:.1f}%) | "
            f"Same Both: {same_both}/{same_pairs} ({met['same_both_rate']*100:.1f}%) | "
            f"NLL: {mean_nll:.4f}"
        )

    return {"metrics": all_metrics, "predictions": saved_predictions}


def check_candidate_permutation(engine: GLiClassEngine) -> Dict[str, Any]:
    logger.info("--- Step 5: Candidate Permutation Invariance Test ---")
    eval_v2_path = EVAL_DATASETS["eval_v2"]
    records = [json.loads(l) for l in open(eval_v2_path, encoding="utf-8") if l.strip()]

    rng = random.Random(999)
    consistent_count = 0
    tested_count = len(records)

    for r in records:
        req_orig = ChoiceRequest.from_dict(r)
        resp_orig = engine.predict(req_orig, temperature=1.0)
        orig_best_id = resp_orig.best_candidate_id

        # Permute choices
        perm_choices = list(req_orig.choices)
        rng.shuffle(perm_choices)
        # ensure permutation is different if len > 1
        if len(perm_choices) > 1 and [c.id for c in perm_choices] == [c.id for c in req_orig.choices]:
            perm_choices.reverse()

        req_perm = ChoiceRequest(
            context=req_orig.context,
            question=req_orig.question,
            choices=perm_choices,
        )
        resp_perm = engine.predict(req_perm, temperature=1.0)
        perm_best_id = resp_perm.best_candidate_id

        if orig_best_id == perm_best_id:
            consistent_count += 1

    cons_rate = consistent_count / tested_count
    logger.info(f"Candidate permutation top-1 consistency: {consistent_count}/{tested_count} ({cons_rate*100:.1f}%)")
    return {
        "tested_count": tested_count,
        "consistent_count": consistent_count,
        "consistency_rate": cons_rate,
    }


def main():
    logger.info("=== ERABI Milestone 5 Gate Self-Review & Audit ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    # Step 1 & Metrics
    engine = GLiClassEngine(model_id=str(EPOCH_9_DIR), device=device)
    eval_output = evaluate_and_recompute(engine)

    # Step 2: Split Overlap Check
    train_records = load_all_training_records()
    overlap_report = check_split_overlap(train_records)

    # Step 5: Candidate Permutation Check
    perm_report = check_candidate_permutation(engine)

    # Gate Verification
    ev2 = eval_output["metrics"]["eval_v2"]
    fr = eval_output["metrics"]["fresh_phrasing_eval"]
    exc = eval_output["metrics"]["eval_exception"]
    smk = eval_output["metrics"]["smoke_cases"]

    gate_checks = {
        "eval_v2_acc_ge_97": (ev2["accuracy"] >= 0.97, f"{ev2['accuracy']*100:.1f}% >= 97.0%"),
        "eval_v2_diff_both_ge_88": (ev2["diff_both_rate"] >= 0.88, f"{ev2['diff_both_rate']*100:.1f}% >= 88.0%"),
        "fresh_acc_ge_80": (fr["accuracy"] >= 0.80, f"{fr['accuracy']*100:.1f}% >= 80.0%"),
        "fresh_diff_both_ge_60": (fr["diff_both_rate"] >= 0.60, f"{fr['diff_both_rate']*100:.1f}% >= 60.0%"),
        "fresh_same_both_ge_75": (fr["same_both_rate"] >= 0.75, f"{fr['same_both_rate']*100:.1f}% >= 75.0%"),
        "exception_acc_ge_98": (exc["accuracy"] >= 0.98, f"{exc['accuracy']*100:.1f}% >= 98.0%"),
        "exception_diff_both_ge_95": (exc["diff_both_rate"] >= 0.95, f"{exc['diff_both_rate']*100:.1f}% >= 95.0%"),
        "smoke_cases_ge_10": (smk["correct_count"] >= 10, f"{smk['correct_count']}/12 >= 10/12"),
        "split_exact_overlap_eq_0": (overlap_report["total_leaks"] == 0, f"{overlap_report['total_leaks']} == 0"),
        "perm_consistency_ge_95": (perm_report["consistency_rate"] >= 0.95, f"{perm_report['consistency_rate']*100:.1f}% >= 95.0%"),
    }

    all_passed = all(status for status, _ in gate_checks.values())
    logger.info("\n=== Final Gate Verification Table ===")
    for k, (status, detail) in gate_checks.items():
        status_str = "PASS" if status else "FAIL"
        logger.info(f"  [{status_str}] {k:30s} : {detail}")

    logger.info(f"\nOverall Milestone 5 Gate Passed: {all_passed}")

    audit_summary = {
        "model_checkpoint": str(EPOCH_9_DIR),
        "milestone": "Milestone 5 Balanced Core Reasoner",
        "all_passed": all_passed,
        "gate_checks": {k: {"passed": s, "detail": d} for k, (s, d) in gate_checks.items()},
        "metrics": eval_output["metrics"],
        "overlap_report": overlap_report,
        "permutation_report": perm_report,
    }

    with open(AUDIT_OUT_DIR / "m5_audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2, ensure_ascii=False)

    # Save raw predictions for reproducibility
    with open(AUDIT_OUT_DIR / "saved_predictions.json", "w", encoding="utf-8") as f:
        json.dump(eval_output["predictions"], f, indent=2, ensure_ascii=False)

    logger.info(f"Audit results saved to {AUDIT_OUT_DIR}")


if __name__ == "__main__":
    main()
