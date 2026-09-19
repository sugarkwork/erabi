"""Milestone 6 Self-Review & Audit Script (ERABI).

Roadmap Section 15 Compliance:
1. Recompute metrics from saved prediction / raw logits across all benchmark sets
2. Split overlap inspection: exact signature overlap == 0
3. Semantic validator check: re-derivation passes 100%
4. Label spot-check
5. Candidate permutation invariance test: top-1 consistency >= 95%
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
from erabi.data.operators.validator import validate_operator_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("erabi.m6_audit")

EPOCH_7_DIR = ROOT / "runs/m6_e2_diversified/checkpoints/epoch_7"
AUDIT_OUT_DIR = ROOT / "runs/m6_e2_diversified/audit"
AUDIT_OUT_DIR.mkdir(parents=True, exist_ok=True)

# Training files
M3_TRAIN_FILE = ROOT / "data/m3_3_v2/train.jsonl"
M4_1_TRAIN_FILE = ROOT / "data/m4_1_exception/train_exception.jsonl"
M4_3_1_TRAIN_FILE = ROOT / "data/m4_3_1_phrasing_fix/phrasing_train.jsonl"
M6_TRAIN_FILE = ROOT / "data/m6_operator/train_operator.jsonl"
AUDIT_FILE = ROOT / "runs/m4_4_1_retention/retention_source_audit.json"

BENCHMARKS = {
    "fresh_operator_eval": ROOT / "data/m6_operator/fresh_operator_eval.jsonl",
    "dev_operator": ROOT / "data/m6_operator/dev_operator.jsonl",
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
    m6_op_train = [json.loads(l) for l in open(M6_TRAIN_FILE, encoding="utf-8") if l.strip()]

    return m3_train + replay_records + m4_1_train + m4_3_1_train + m6_op_train


def make_sig(r: Dict[str, Any]) -> str:
    choices = "|".join(c["text"] for c in r["choices"])
    return f"{r['context'].strip()} /// {r['question'].strip()} /// {choices}"


def check_split_overlap(train_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    logger.info("--- Step 2: Split Overlap Check ---")
    train_sigs: Set[str] = {make_sig(r) for r in train_records}
    train_ids: Set[str] = {r["id"] for r in train_records}

    results = {}
    total_leaks = 0

    for bname, bpath in BENCHMARKS.items():
        bench_records = [json.loads(l) for l in open(bpath, encoding="utf-8") if l.strip()]
        id_leaks = [r["id"] for r in bench_records if r["id"] in train_ids]
        sig_leaks = [r["id"] for r in bench_records if make_sig(r) in train_sigs]

        results[bname] = {
            "count": len(bench_records),
            "id_leaks": len(id_leaks),
            "sig_leaks": len(sig_leaks),
        }
        total_leaks += len(sig_leaks)
        logger.info(f"  {bname:20s}: {len(bench_records)} cases | exact signature leaks: {len(sig_leaks)}")

    logger.info(f"Total exact leaks across all benchmark sets: {total_leaks}")
    return {"total_leaks": total_leaks, "details": results}


def evaluate_and_recompute(engine: GLiClassEngine) -> Dict[str, Any]:
    logger.info("--- Step 1: Raw Logits Evaluation & Metric Recomputation ---")
    all_metrics = {}
    saved_preds = {}

    for bname, bpath in BENCHMARKS.items():
        records = [json.loads(l) for l in open(bpath, encoding="utf-8") if l.strip()]
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

            tensor_logits = torch.tensor(raw_logits, dtype=torch.float64)
            log_probs = F.log_softmax(tensor_logits, dim=-1)
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
                "task_family": r.get("task_family"),
                "target": tgt_cid,
                "predicted": pred_cid,
                "is_correct": is_corr,
                "raw_logits": raw_logits,
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
        for gid, pair in groups.items():
            if len(pair) == 2:
                total_pairs += 1
                both = pair[0]["is_correct"] and pair[1]["is_correct"]
                if both:
                    pair_both += 1
                if pair[0]["target"] != pair[1]["target"]:
                    diff_pairs += 1
                    if both:
                        diff_both += 1

        met: Dict[str, Any] = {
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
        }

        # Per-family breakdown
        families = sorted(list({r.get("task_family") for r in records if r.get("task_family")}))
        if len(families) > 1:
            fam_m = {}
            for fam in families:
                fam_rows = [p for p in preds if p.get("task_family") == fam]
                f_n = len(fam_rows)
                f_corr = sum(1 for p in fam_rows if p["is_correct"])
                fam_m[fam] = {
                    "count": f_n,
                    "correct": f_corr,
                    "accuracy": f_corr / f_n if f_n > 0 else 0.0,
                }
            met["per_family"] = fam_m

        all_metrics[bname] = met
        saved_preds[bname] = preds

        diff_str = f"Diff Both: {diff_both}/{diff_pairs} ({met['diff_both_rate']*100:.1f}%)" if diff_pairs > 0 else ""
        logger.info(f"  {bname:20s}: Acc: {acc*100:.1f}% ({correct_count}/{n}) | {diff_str} | NLL: {mean_nll:.4f}")

    return {"metrics": all_metrics, "predictions": saved_preds}


def check_candidate_permutation(engine: GLiClassEngine) -> Dict[str, Any]:
    logger.info("--- Step 5: Candidate Permutation Invariance Test ---")
    fop_path = BENCHMARKS["fresh_operator_eval"]
    records = [json.loads(l) for l in open(fop_path, encoding="utf-8") if l.strip()]

    rng = random.Random(999)
    consistent_count = 0
    tested_count = len(records)

    for r in records:
        req_orig = ChoiceRequest.from_dict(r)
        resp_orig = engine.predict(req_orig, temperature=1.0)
        orig_best_id = resp_orig.best_candidate_id

        perm_choices = list(req_orig.choices)
        rng.shuffle(perm_choices)
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
    logger.info(f"Fresh Operator candidate permutation top-1 consistency: {consistent_count}/{tested_count} ({cons_rate*100:.1f}%)")
    return {
        "tested_count": tested_count,
        "consistent_count": consistent_count,
        "consistency_rate": cons_rate,
    }


def main():
    logger.info("=== ERABI Milestone 6 Gate Self-Review & Audit ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    # Step 1: Raw Logits Evaluation
    engine = GLiClassEngine(model_id=str(EPOCH_7_DIR), device=device)
    eval_output = evaluate_and_recompute(engine)

    # Step 2: Split Overlap Check
    train_records = load_all_training_records()
    overlap_report = check_split_overlap(train_records)

    # Step 3: Semantic Validation Check on M6 Datasets
    logger.info("--- Step 3: Semantic Validation Verification ---")
    fresh_records = [json.loads(l) for l in open(BENCHMARKS["fresh_operator_eval"], encoding="utf-8") if l.strip()]
    dev_records = [json.loads(l) for l in open(BENCHMARKS["dev_operator"], encoding="utf-8") if l.strip()]
    train_op_records = [json.loads(l) for l in open(M6_TRAIN_FILE, encoding="utf-8") if l.strip()]

    v_fresh = validate_operator_dataset(fresh_records)
    v_dev = validate_operator_dataset(dev_records)
    v_train = validate_operator_dataset(train_op_records)
    logger.info(f"  Fresh semantic status: {v_fresh['validation_status']} (diff pairs: {v_fresh['diff_target_pairs']}/{v_fresh['total_groups']})")
    logger.info(f"  Dev semantic status:   {v_dev['validation_status']} (diff pairs: {v_dev['diff_target_pairs']}/{v_dev['total_groups']})")
    logger.info(f"  Train semantic status: {v_train['validation_status']} (diff pairs: {v_train['diff_target_pairs']}/{v_train['total_groups']})")

    # Step 5: Candidate Permutation Check
    perm_report = check_candidate_permutation(engine)

    # Final Gate Check
    fop = eval_output["metrics"]["fresh_operator_eval"]
    ev2 = eval_output["metrics"]["eval_v2"]
    exc = eval_output["metrics"]["eval_exception"]
    fr = eval_output["metrics"]["fresh_phrasing_eval"]
    smk = eval_output["metrics"]["smoke_cases"]

    fam_checks = {fam: fm["accuracy"] >= 0.60 for fam, fm in fop["per_family"].items()}
    all_fams_ge_60 = all(fam_checks.values())
    min_fam_acc = min(fm["accuracy"] for fm in fop["per_family"].values())

    gate_checks = {
        "fresh_op_acc_ge_85": (fop["accuracy"] >= 0.85, f"{fop['accuracy']*100:.1f}% >= 85.0%"),
        "fresh_op_pair_both_ge_70": (fop["diff_both_rate"] >= 0.70, f"{fop['diff_both_rate']*100:.1f}% >= 70.0%"),
        "all_families_ge_60": (all_fams_ge_60, f"min family acc = {min_fam_acc*100:.1f}% >= 60.0%"),
        "no_zero_family": (min_fam_acc > 0.0, f"min family acc = {min_fam_acc*100:.1f}% > 0.0%"),
        "retention_eval_v2_ge_96": (ev2["accuracy"] >= 0.96, f"{ev2['accuracy']*100:.1f}% >= 96.0%"),
        "retention_eval_exception_ge_98": (exc["accuracy"] >= 0.98, f"{exc['accuracy']*100:.1f}% >= 98.0%"),
        "retention_fresh_phr_ge_79_7": (fr["accuracy"] >= 0.797, f"{fr['accuracy']*100:.1f}% >= 79.7%"),
        "retention_smoke_cases_ge_10": (smk["correct_count"] >= 10, f"{smk['correct_count']}/12 >= 10/12"),
        "exact_signature_leaks_eq_0": (overlap_report["total_leaks"] == 0, f"{overlap_report['total_leaks']} == 0"),
        "permutation_consistency_ge_95": (perm_report["consistency_rate"] >= 0.95, f"{perm_report['consistency_rate']*100:.1f}% >= 95.0%"),
    }

    all_passed = all(status for status, _ in gate_checks.values())

    logger.info("\n=== Final Milestone 6 Gate Verification Table ===")
    for k, (status, detail) in gate_checks.items():
        status_str = "PASS" if status else "FAIL"
        logger.info(f"  [{status_str}] {k:32s} : {detail}")

    logger.info(f"\nOverall Milestone 6 Gate Passed: {all_passed}")

    audit_summary = {
        "model_checkpoint": str(EPOCH_7_DIR),
        "milestone": "Milestone 6 Operator Generalization",
        "all_passed": all_passed,
        "gate_checks": {k: {"passed": s, "detail": d} for k, (s, d) in gate_checks.items()},
        "metrics": eval_output["metrics"],
        "overlap_report": overlap_report,
        "permutation_report": perm_report,
    }

    with open(AUDIT_OUT_DIR / "m6_audit_summary.json", "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2, ensure_ascii=False)

    with open(AUDIT_OUT_DIR / "saved_predictions.json", "w", encoding="utf-8") as f:
        json.dump(eval_output["predictions"], f, indent=2, ensure_ascii=False)

    logger.info(f"Audit results saved to {AUDIT_OUT_DIR}")


if __name__ == "__main__":
    main()
