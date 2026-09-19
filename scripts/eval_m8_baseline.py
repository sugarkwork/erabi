"""Milestone 8 Baseline Diagnostic (ERABI).

Evaluates the frozen Milestone 7 model (W_robustness_v1) on the newly generated
fresh_general_eval benchmark (6 families, 60 contrastive pairs, 120 cases).

Outputs:
- runs/m8_baseline_diagnostic/baseline_report.json
- runs/m8_baseline_diagnostic/notes.md
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
logger = logging.getLogger("erabi.m8_baseline")

OUT_DIR = ROOT / "runs/m8_baseline_diagnostic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "runs/m7_robustness/checkpoint"
FRESH_GEN_PATH = ROOT / "data/m8_general_choice/fresh_general_eval.jsonl"


def evaluate_general_benchmark(engine: GLiClassEngine, dataset_path: Path) -> Dict[str, Any]:
    records = [json.loads(l) for l in open(dataset_path, encoding="utf-8") if l.strip()]
    results = []
    total_nll = 0.0
    total_brier = 0.0
    correct_count = 0

    for r in records:
        req = ChoiceRequest.from_dict(r)
        tgt_cid = r["target"]["choice_id"]
        tgt_idx = next(i for i, c in enumerate(req.choices) if c.id == tgt_cid)

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

        one_hot = [1.0 if i == tgt_idx else 0.0 for i in range(len(req.choices))]
        brier = sum((p - y) ** 2 for p, y in zip(probs, one_hot))
        total_brier += brier

        results.append({
            "id": r["id"],
            "group_id": r["group_id"],
            "task_family": r["task_family"],
            "target": tgt_cid,
            "predicted": pred_cid,
            "is_correct": is_corr,
            "raw_logits": raw_logits,
            "probs": probs,
            "nll": nll,
            "brier": brier,
        })

    n = len(records)
    acc = correct_count / n
    mean_nll = total_nll / n
    mean_brier = total_brier / n

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
        fam_grps = [g for g in groups.values() if g[0]["task_family"] == fam]
        fam_pairs = len(fam_grps)
        fam_both = sum(1 for g in fam_grps if g[0]["is_correct"] and g[1]["is_correct"])
        fam_metrics[fam] = {
            "count": fam_n,
            "correct": fam_corr,
            "accuracy": fam_corr / fam_n,
            "pairs": fam_pairs,
            "pair_both": fam_both,
            "pair_both_rate": fam_both / fam_pairs if fam_pairs > 0 else 0.0,
            "mean_nll": sum(r["nll"] for r in fam_res) / fam_n,
        }

    return {
        "count": n,
        "correct_count": correct_count,
        "accuracy": acc,
        "mean_nll": mean_nll,
        "mean_brier": mean_brier,
        "total_pairs": total_pairs,
        "pair_both": pair_both,
        "pair_both_rate": pair_both / total_pairs if total_pairs > 0 else 0.0,
        "by_family": fam_metrics,
        "details": results,
    }


def main():
    logger.info("=== Milestone 8: Baseline Diagnostic on Fresh General Eval ===")
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    logger.info(f"Loading W_robustness_v1 from {MODEL_DIR} on {device}")
    engine = GLiClassEngine(model_id=str(MODEL_DIR), device=device)

    eval_res = evaluate_general_benchmark(engine, FRESH_GEN_PATH)

    logger.info("\n=== Summary Results ===")
    logger.info(f"Overall Accuracy: {eval_res['accuracy']*100:.1f}% ({eval_res['correct_count']}/{eval_res['count']}) [M8 Gate >= 82.0%]")
    logger.info(f"Pair Both Rate:   {eval_res['pair_both_rate']*100:.1f}% ({eval_res['pair_both']}/{eval_res['total_pairs']})")
    logger.info(f"Mean NLL:         {eval_res['mean_nll']:.4f}")
    logger.info(f"Mean Brier:       {eval_res['mean_brier']:.4f}")

    logger.info("\n=== Per-Family Breakdown ===")
    md_fams = [
        "| Task Family | Count | Accuracy | Pair Both | Mean NLL | Gate (>=70%) |",
        "|:---|:---:|:---:|:---:|:---:|:---:|",
    ]
    for fam, m in eval_res["by_family"].items():
        gate_ok = "PASS" if m["accuracy"] >= 0.70 else "**FAIL**"
        md_fams.append(
            f"| {fam} | {m['count']} | {m['accuracy']*100:.1f}% | "
            f"{m['pair_both_rate']*100:.1f}% ({m['pair_both']}/{m['pairs']}) | "
            f"{m['mean_nll']:.4f} | {gate_ok} |"
        )
        logger.info(f"  {fam:<24}: Acc={m['accuracy']*100:.1f}%, PairBoth={m['pair_both_rate']*100:.1f}%, NLL={m['mean_nll']:.4f}")

    # Save JSON report
    report_path = OUT_DIR / "baseline_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_res, f, indent=2, ensure_ascii=False)
    logger.info(f"\nSaved baseline report to {report_path}")

    # Notes
    notes_content = f"""# Milestone 8 Baseline Diagnostic Report

- **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Evaluated Model**: `W_robustness_v1` (`runs/m7_robustness/checkpoint`)
- **Benchmark**: `data/m8_general_choice/fresh_general_eval.jsonl` (120 cases, 60 contrastive pairs)

## Overall Metrics
- **Accuracy**: {eval_res['accuracy']*100:.1f}% ({eval_res['correct_count']}/{eval_res['count']}) [M8 Gate: $\\ge 82.0\\%$]
- **Pair Both Rate**: {eval_res['pair_both_rate']*100:.1f}% ({eval_res['pair_both']}/{eval_res['total_pairs']})
- **Mean NLL**: {eval_res['mean_nll']:.4f}
- **Mean Brier**: {eval_res['mean_brier']:.4f}

## Task Family Breakdown
{chr(10).join(md_fams)}
"""
    notes_path = OUT_DIR / "notes.md"
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(notes_content)
    logger.info(f"Saved notes to {notes_path}")


if __name__ == "__main__":
    main()
