"""Generate summary_report.json for M4.1 Exception Priority Experiment."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "runs/m4_1_exception"
COMP_FILE = OUT_DIR / "comparisons/comparisons_summary.json"

def main():
    comp_data = json.load(open(COMP_FILE, encoding="utf-8"))

    summary = {
        "experiment_title": "ERABI M4.1 Exception Priority Experiment",
        "baseline_model": {
            "path": comp_data["models"]["baseline"],
            "description": "W_v2_ce10 (M3.5 10-epoch checkpoint, baseline standard CE)",
        },
        "experiment_model": {
            "path": comp_data["models"]["experiment"],
            "description": "W_m4_1 (M4.1 10-epoch checkpoint trained on 600 M3 + 240 Exception cases)",
        },
        "evaluation_temperature": 1.0,
        "temperature_policy": "strictly_uncalibrated_T1 (existing calibration not reused for new weights)",
        "datasets_evaluated": {
            "eval_exception": {
                "description": "New Exception Priority evaluation dataset (60 pairs / 120 cases)",
                "baseline": comp_data["datasets"]["eval_exception"]["baseline"],
                "experiment": comp_data["datasets"]["eval_exception"]["experiment"],
                "gain": {
                    "accuracy": comp_data["datasets"]["eval_exception"]["accuracy_diff"],
                    "nll": comp_data["datasets"]["eval_exception"]["nll_diff"],
                    "brier": comp_data["datasets"]["eval_exception"]["brier_diff"],
                },
            },
            "smoke_cases": {
                "description": "Standard 12 diagnostic cases (regression & smoke-06 recovery check)",
                "baseline": comp_data["datasets"]["smoke_cases"]["baseline"],
                "experiment": comp_data["datasets"]["smoke_cases"]["experiment"],
                "smoke_06_recovery": {
                    "target": "continue",
                    "baseline_pred": "heal (incorrect, pmax ~0.9965)",
                    "experiment_pred": "continue (correct)",
                    "status": "recovered",
                },
                "individual_transitions": comp_data["datasets"]["smoke_cases"]["individual_transitions"],
            },
            "eval_v2": {
                "description": "M3 synthetic rule benchmark (200 cases / 100 pairs)",
                "baseline": comp_data["datasets"]["eval_v2"]["baseline"],
                "experiment": comp_data["datasets"]["eval_v2"]["experiment"],
                "gain": {
                    "accuracy": comp_data["datasets"]["eval_v2"]["accuracy_diff"],
                    "nll": comp_data["datasets"]["eval_v2"]["nll_diff"],
                    "brier": comp_data["datasets"]["eval_v2"]["brier_diff"],
                },
            },
            "transfer_probe": {
                "description": "Transfer and generalization diagnostic probe (32 cases / 16 pairs)",
                "baseline": comp_data["datasets"]["transfer_probe"]["baseline"],
                "experiment": comp_data["datasets"]["transfer_probe"]["experiment"],
                "gain": {
                    "accuracy": comp_data["datasets"]["transfer_probe"]["accuracy_diff"],
                    "nll": comp_data["datasets"]["transfer_probe"]["nll_diff"],
                    "brier": comp_data["datasets"]["transfer_probe"]["brier_diff"],
                },
                "regression_note": "Observed 5-case regression (25/32 -> 20/32) due to domain transfer sensitivity on negation/reverse probes.",
            },
        },
        "findings": {
            "new_capability": "Acquired near-perfect exception priority resolution: eval_exception accuracy rose from 32.5% to 99.2%, and diff_target_pairs from 0.0% to 100.0%.",
            "smoke_cases": "smoke-06 (long-standing exception priority failure) fully recovered to continue; smoke accuracy reached 12/12 (100.0%).",
            "retention": "M3 synthetic rule performance maintained at 97.0% (194/200, only 1 question difference from baseline 97.5%).",
            "tradeoff": "transfer_probe showed regression from 78.1% to 62.5% on out-of-domain negation/reverse prompts.",
        },
    }

    out_file = OUT_DIR / "summary_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Saved summary_report.json to {out_file}")

if __name__ == "__main__":
    main()
