"""Milestone 7 Baseline Diagnostic (ERABI).

Evaluates the frozen Milestone 6 model (W_operator_v1) on the newly generated
fresh_robustness_eval benchmark (9 domains, 6 perturbation types, 54 contrastive pairs, 108 cases).

Measures:
- Overall accuracy, pair-both rate, mean NLL, Brier score
- Top-1 candidate permutation consistency
- Breakdown across unseen novel vs existing domains
- Breakdown across perturbation types: clean, distractor, sentence_swap, numerical_scale, choice_id_perturbation, three_choices

Outputs:
- runs/m7_baseline_diagnostic/baseline_report.json
- runs/m7_baseline_diagnostic/notes.md
"""

from __future__ import annotations

import json
import logging
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

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
logger = logging.getLogger("erabi.m7_baseline")

OUT_DIR = ROOT / "runs/m7_baseline_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "runs/m6_operator/checkpoint"
FRESH_ROB_PATH = ROOT / "data/m7_robustness/fresh_robustness_eval.jsonl"


def evaluate_robustness_benchmark(engine: GLiClassEngine, dataset_path: Path) -> Dict[str, Any]:
    records = [json.loads(l) for l in open(dataset_path, encoding="utf-8") if l.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0
    perm_consistent_count = 0

    for r in records:
        req = ChoiceRequest.from_dict(r)
        tgt_cid = r["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        # 1. Forward pass normal order
        resp = engine.predict(req, temperature=1.0, return_logits=True)
        raw_logits = resp.raw_logits
        assert all(math.isfinite(x) for x in raw_logits), f"Non-finite logits in {r['id']}"

        tensor_logits = torch.tensor(raw_logits, dtype=torch.float64)
        probs = F.softmax(tensor_logits, dim=-1).tolist()
        log_probs = F.log_softmax(tensor_logits, dim=-1).tolist()

        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        nll = -log_probs[tgt_idx]
        total_nll += nll

        # Brier score: sum_i (p_i - y_i)^2
        one_hot = [1.0 if i == tgt_idx else 0.0 for i in range(len(req.choices))]
        brier = sum((p - y) ** 2 for p, y in zip(probs, one_hot))
        total_brier += brier

        # 2. Candidate permutation test (reverse choices)
        rev_record = dict(r)
        rev_record["choices"] = list(reversed(r["choices"]))
        rev_req = ChoiceRequest.from_dict(rev_record)
        rev_resp = engine.predict(rev_req, temperature=1.0, return_logits=True)
        rev_pred_cid = rev_resp.best_candidate_id

        is_perm_consistent = (pred_cid == rev_pred_cid)
        if is_perm_consistent:
            perm_consistent_count += 1

        results.append({
            "id": r["id"],
            "group_id": r["group_id"],
            "task_family": r.get("task_family", "robustness"),
            "domain": r["domain"],
            "perturbation": r["perturbation"],
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "is_perm_consistent": is_perm_consistent,
            "raw_logits": raw_logits,
            "probs": probs,
            "nll": nll,
            "brier": brier,
        })

    n = len(records)
    acc = correct_count / n
    mean_nll = total_nll / n
    mean_brier = total_brier / n
    perm_consistency = perm_consistent_count / n

    # Group pairs
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for res in results:
        groups.setdefault(res["group_id"], []).append(res)

    total_pairs = len(groups)
    pair_both = sum(1 for g in groups.values() if g[0]["is_correct"] and g[1]["is_correct"])

    # Domain breakdown
    domains = sorted(list({r["domain"] for r in records}))
    domain_metrics = {}
    for d in domains:
        d_res = [r for r in results if r["domain"] == d]
        d_n = len(d_res)
        d_corr = sum(1 for r in d_res if r["is_correct"])
        d_perm = sum(1 for r in d_res if r["is_perm_consistent"])
        d_grps = [g for g in groups.values() if g[0]["domain"] == d]
        d_pairs = len(d_grps)
        d_both = sum(1 for g in d_grps if g[0]["is_correct"] and g[1]["is_correct"])
        domain_metrics[d] = {
            "count": d_n,
            "correct": d_corr,
            "accuracy": d_corr / d_n,
            "pairs": d_pairs,
            "pair_both": d_both,
            "pair_both_rate": d_both / d_pairs if d_pairs > 0 else 0.0,
            "perm_consistency": d_perm / d_n,
            "mean_nll": sum(r["nll"] for r in d_res) / d_n,
            "is_novel": d in ["medical", "finance", "factory", "smart_home"],
        }

    # Perturbation breakdown
    perturbations = sorted(list({r["perturbation"] for r in records}))
    pert_metrics = {}
    for p in perturbations:
        p_res = [r for r in results if r["perturbation"] == p]
        p_n = len(p_res)
        p_corr = sum(1 for r in p_res if r["is_correct"])
        p_perm = sum(1 for r in p_res if r["is_perm_consistent"])
        p_grps = [g for g in groups.values() if g[0]["perturbation"] == p]
        p_pairs = len(p_grps)
        p_both = sum(1 for g in p_grps if g[0]["is_correct"] and g[1]["is_correct"])
        pert_metrics[p] = {
            "count": p_n,
            "correct": p_corr,
            "accuracy": p_corr / p_n,
            "pairs": p_pairs,
            "pair_both": p_both,
            "pair_both_rate": p_both / p_pairs if p_pairs > 0 else 0.0,
            "perm_consistency": p_perm / p_n,
            "mean_nll": sum(r["nll"] for r in p_res) / p_n,
        }

    # Novel vs Existing breakdown
    novel_res = [r for r in results if r["domain"] in ["medical", "finance", "factory", "smart_home"]]
    existing_res = [r for r in results if r["domain"] not in ["medical", "finance", "factory", "smart_home"]]

    novel_acc = sum(1 for r in novel_res if r["is_correct"]) / len(novel_res)
    novel_perm = sum(1 for r in novel_res if r["is_perm_consistent"]) / len(novel_res)
    existing_acc = sum(1 for r in existing_res if r["is_correct"]) / len(existing_res)
    existing_perm = sum(1 for r in existing_res if r["is_perm_consistent"]) / len(existing_res)

    return {
        "count": n,
        "correct_count": correct_count,
        "accuracy": acc,
        "mean_nll": mean_nll,
        "mean_brier": mean_brier,
        "perm_consistency": perm_consistency,
        "total_pairs": total_pairs,
        "pair_both": pair_both,
        "pair_both_rate": pair_both / total_pairs if total_pairs > 0 else 0.0,
        "novel_vs_existing": {
            "novel_accuracy": novel_acc,
            "novel_perm_consistency": novel_perm,
            "existing_accuracy": existing_acc,
            "existing_perm_consistency": existing_perm,
        },
        "by_domain": domain_metrics,
        "by_perturbation": pert_metrics,
        "details": results,
    }


def main():
    logger.info("=== Milestone 7: Baseline Diagnostic on Fresh Robustness Eval ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading W_operator_v1 from {MODEL_DIR} on {device}")
    engine = GLiClassEngine(model_id=str(MODEL_DIR), device=device)

    eval_res = evaluate_robustness_benchmark(engine, FRESH_ROB_PATH)

    logger.info("\n=== Summary Results ===")
    logger.info(f"Overall Accuracy:       {eval_res['accuracy']*100:.1f}% ({eval_res['correct_count']}/{eval_res['count']}) [M7 Gate >= 85.0%]")
    logger.info(f"Pair Both Rate:         {eval_res['pair_both_rate']*100:.1f}% ({eval_res['pair_both']}/{eval_res['total_pairs']})")
    logger.info(f"Permutation Consistency:{eval_res['perm_consistency']*100:.1f}% [M7 Gate >= 95.0%]")
    logger.info(f"Mean NLL:               {eval_res['mean_nll']:.4f}")
    logger.info(f"Mean Brier:             {eval_res['mean_brier']:.4f}")

    logger.info("\n--- Novel vs Existing Domains ---")
    nve = eval_res["novel_vs_existing"]
    logger.info(f"Novel Domains (4):    Accuracy={nve['novel_accuracy']*100:.1f}%, Perm={nve['novel_perm_consistency']*100:.1f}%")
    logger.info(f"Existing Domains (5): Accuracy={nve['existing_accuracy']*100:.1f}%, Perm={nve['existing_perm_consistency']*100:.1f}%")

    logger.info("\n=== Domain Breakdown ===")
    md_domains = [
        "| Domain | Type | Count | Accuracy | Pair Both | Permutation | Gate (>=60%) |",
        "|:---|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for d, m in eval_res["by_domain"].items():
        dom_type = "Novel" if m["is_novel"] else "Existing"
        gate_ok = "PASS" if m["accuracy"] >= 0.60 else "**FAIL**"
        md_domains.append(
            f"| {d} | {dom_type} | {m['count']} | {m['accuracy']*100:.1f}% | "
            f"{m['pair_both_rate']*100:.1f}% ({m['pair_both']}/{m['pairs']}) | "
            f"{m['perm_consistency']*100:.1f}% | {gate_ok} |"
        )
        logger.info(f"  {d:<12} ({dom_type:<8}): Acc={m['accuracy']*100:.1f}%, PairBoth={m['pair_both_rate']*100:.1f}%, Perm={m['perm_consistency']*100:.1f}%")

    logger.info("\n=== Perturbation Breakdown ===")
    md_perts = [
        "| Perturbation | Count | Accuracy | Pair Both | Permutation |",
        "|:---|:---:|:---:|:---:|:---:|",
    ]
    for p, m in eval_res["by_perturbation"].items():
        md_perts.append(
            f"| {p} | {m['count']} | {m['accuracy']*100:.1f}% | "
            f"{m['pair_both_rate']*100:.1f}% ({m['pair_both']}/{m['pairs']}) | "
            f"{m['perm_consistency']*100:.1f}% |"
        )
        logger.info(f"  {p:<24}: Acc={m['accuracy']*100:.1f}%, PairBoth={m['pair_both_rate']*100:.1f}%, Perm={m['perm_consistency']*100:.1f}%")

    # Save JSON report
    report_path = OUT_DIR / "baseline_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_res, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved baseline report to {report_path}")

    # Generate notes.md
    notes_content = f"""# Milestone 7 Baseline Diagnostic Report

- **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Evaluated Model**: `W_operator_v1` (`runs/m6_operator/checkpoint`)
- **Benchmark**: `data/m7_robustness/fresh_robustness_eval.jsonl` (108 cases, 54 contrastive pairs)

## Overall Metrics
- **Accuracy**: {eval_res['accuracy']*100:.1f}% ({eval_res['correct_count']}/{eval_res['count']}) [M7 Gate: $\\ge 85.0\\%$]
- **Pair Both Rate**: {eval_res['pair_both_rate']*100:.1f}% ({eval_res['pair_both']}/{eval_res['total_pairs']})
- **Permutation Consistency**: {eval_res['perm_consistency']*100:.1f}% [M7 Gate: $\\ge 95.0\\%$]
- **Mean NLL**: {eval_res['mean_nll']:.4f}
- **Mean Brier**: {eval_res['mean_brier']:.4f}

## Unseen Novel Domains vs Existing Domains
- **Unseen Novel Domains** (`medical`, `finance`, `factory`, `smart_home`):
  - Accuracy: **{nve['novel_accuracy']*100:.1f}%**
  - Permutation Consistency: **{nve['novel_perm_consistency']*100:.1f}%**
- **Existing Domains** (`inventory`, `server`, `game`, `delivery`, `support`):
  - Accuracy: **{nve['existing_accuracy']*100:.1f}%**
  - Permutation Consistency: **{nve['existing_perm_consistency']*100:.1f}%**

## Domain Breakdown
{chr(10).join(md_domains)}

## Perturbation Breakdown
{chr(10).join(md_perts)}

## Diagnosis & Findings
"""
    # Analyze weaknesses
    fail_cases = [r for r in eval_res["details"] if not r["is_correct"]]
    perm_fails = [r for r in eval_res["details"] if not r["is_perm_consistent"]]

    notes_content += f"""
- Total Failures: {len(fail_cases)} / {eval_res['count']}
- Total Permutation Inconsistencies: {len(perm_fails)} / {eval_res['count']}

### Key Failure Analysis:
"""
    if len(fail_cases) > 0:
        notes_content += "Sample incorrect cases:\n"
        for fc in fail_cases[:10]:
            notes_content += f"- `{fc['id']}` ({fc['domain']}, {fc['perturbation']}): Target={fc['target']}, Pred={fc['predicted']}, Logits={fc['raw_logits']}\n"
    else:
        notes_content += "No failure cases observed!\n"

    notes_path = OUT_DIR / "notes.md"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(notes_content)
    logger.info(f"Saved notes to {notes_path}")


if __name__ == "__main__":
    main()
