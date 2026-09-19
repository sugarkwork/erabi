"""Milestone 6 Baseline Diagnostic (ERABI).

Evaluates the frozen Milestone 5 model (W_core_v1) on the newly generated
fresh_operator_eval benchmark (10 operator families, 50 contrastive pairs, 100 cases).

Outputs:
- runs/m6_baseline_diagnostic/baseline_report.json
- runs/m6_baseline_diagnostic/notes.md
- Per-family accuracy, pair both rate, NLL, and failure breakdown.
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
logger = logging.getLogger("erabi.m6_baseline")

OUT_DIR = ROOT / "runs/m6_baseline_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "runs/m5_core/checkpoint"
FRESH_OP_PATH = ROOT / "data/m6_operator/fresh_operator_eval.jsonl"


def evaluate_operator_benchmark(engine: GLiClassEngine, dataset_path: Path) -> Dict[str, Any]:
    records = [json.loads(l) for l in open(dataset_path, encoding="utf-8") if l.strip()]
    results = []
    total_nll = 0.0
    correct_count = 0

    for r in records:
        req = ChoiceRequest.from_dict(r)
        tgt_cid = r["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

        resp = engine.predict(req, temperature=1.0, return_logits=True)
        raw_logits = resp.raw_logits
        assert all(math.isfinite(x) for x in raw_logits), f"Non-finite logits in {r['id']}"

        tensor_logits = torch.tensor(raw_logits, dtype=torch.float64)
        log_probs = F.log_softmax(tensor_logits, dim=-1)

        pred_cid = resp.best_candidate_id
        is_corr = (pred_cid == tgt_cid)
        if is_corr:
            correct_count += 1

        nll = -float(log_probs[tgt_idx].item())
        total_nll += nll

        results.append({
            "id": r["id"],
            "group_id": r["group_id"],
            "task_family": r["task_family"],
            "domain": r["domain"],
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "raw_logits": raw_logits,
            "nll": nll,
        })

    n = len(records)
    acc = correct_count / n
    mean_nll = total_nll / n

    # Group pairs
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for res in results:
        groups.setdefault(res["group_id"], []).append(res)

    total_pairs = len(groups)
    pair_both = sum(1 for g in groups.values() if g[0]["is_correct"] and g[1]["is_correct"])

    # Per-family breakdown
    families = sorted(list({r["task_family"] for r in records}))
    fam_metrics = {}

    for fam in families:
        fam_res = [r for r in results if r["task_family"] == fam]
        fam_n = len(fam_res)
        fam_corr = sum(1 for r in fam_res if r["is_correct"])
        fam_acc = fam_corr / fam_n if fam_n > 0 else 0.0

        fam_grps = [g for g in groups.values() if g[0]["task_family"] == fam]
        fam_pairs = len(fam_grps)
        fam_both = sum(1 for g in fam_grps if g[0]["is_correct"] and g[1]["is_correct"])

        fam_metrics[fam] = {
            "count": fam_n,
            "correct": fam_corr,
            "accuracy": fam_acc,
            "pairs": fam_pairs,
            "pair_both": fam_both,
            "pair_both_rate": fam_both / fam_pairs if fam_pairs > 0 else 0.0,
            "mean_nll": sum(r["nll"] for r in fam_res) / fam_n if fam_n > 0 else 0.0,
        }

    return {
        "count": n,
        "correct_count": correct_count,
        "accuracy": acc,
        "mean_nll": mean_nll,
        "total_pairs": total_pairs,
        "pair_both": pair_both,
        "pair_both_rate": pair_both / total_pairs if total_pairs > 0 else 0.0,
        "per_family": fam_metrics,
        "details": results,
    }


def main():
    logger.info("=== Milestone 6: Baseline Diagnostic on Fresh Operator Eval ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading W_core_v1 from {MODEL_DIR} on {device}")
    engine = GLiClassEngine(model_id=str(MODEL_DIR), device=device)

    eval_res = evaluate_operator_benchmark(engine, FRESH_OP_PATH)

    logger.info("\n=== Summary Results ===")
    logger.info(f"Overall Accuracy: {eval_res['accuracy']*100:.1f}% ({eval_res['correct_count']}/{eval_res['count']})")
    logger.info(f"Pair Both Rate:   {eval_res['pair_both_rate']*100:.1f}% ({eval_res['pair_both']}/{eval_res['total_pairs']})")
    logger.info(f"Mean NLL:         {eval_res['mean_nll']:.4f}")

    logger.info("\n=== Per-Family Breakdown ===")
    md_table = [
        "| Operator Family | Count | Accuracy | Pair Both Rate | Mean NLL | M6 Gate (>=60%) |",
        "|:---|:---:|:---:|:---:|:---:|:---:|",
    ]

    for fam, m in eval_res["per_family"].items():
        gate_status = "PASS" if m["accuracy"] >= 0.60 else "**FAIL**"
        logger.info(
            f"  {fam:20s}: Acc: {m['accuracy']*100:.1f}% ({m['correct']}/{m['count']}) | "
            f"Pair Both: {m['pair_both']}/{m['pairs']} ({m['pair_both_rate']*100:.1f}%) | "
            f"NLL: {m['mean_nll']:.4f} | {gate_status}"
        )
        md_table.append(
            f"| `{fam}` | {m['count']} | {m['accuracy']*100:.1f}% | {m['pair_both']}/{m['pairs']} ({m['pair_both_rate']*100:.1f}%) | {m['mean_nll']:.4f} | {gate_status} |"
        )

    # Save outputs
    with open(OUT_DIR / "baseline_report.json", "w", encoding="utf-8") as f:
        json.dump(eval_res, f, indent=2, ensure_ascii=False)

    md_content = f"""# Milestone 6 Baseline Diagnostic Report

**Model**: `W_core_v1` (`runs/m5_core/checkpoint`)
**Benchmark**: `fresh_operator_eval` (100 cases, 50 contrastive pairs, 10 families)
**Generated at**: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Overall Performance
- **Accuracy**: {eval_res['accuracy']*100:.1f}% ({eval_res['correct_count']}/{eval_res['count']}) (Gate: >= 85.0%)
- **Contrast Pair Both Rate**: {eval_res['pair_both_rate']*100:.1f}% ({eval_res['pair_both']}/{eval_res['total_pairs']}) (Gate: >= 70.0%)
- **Mean NLL**: {eval_res['mean_nll']:.4f}

## Per-Operator Family Breakdown
{chr(10).join(md_table)}

## Baseline Gate Verdict
- Overall Acc >= 85%: {'PASS' if eval_res['accuracy'] >= 0.85 else 'FAIL'}
- Pair Both >= 70%: {'PASS' if eval_res['pair_both_rate'] >= 0.70 else 'FAIL'}
- Each family >= 60%: {'PASS' if all(m['accuracy'] >= 0.60 for m in eval_res['per_family'].values()) else 'FAIL'}
- No 0% family: {'PASS' if all(m['accuracy'] > 0.0 for m in eval_res['per_family'].values()) else 'FAIL'}
"""

    with open(OUT_DIR / "notes.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    logger.info(f"\nBaseline diagnostic report saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
