"""Export the private Exam-QA fine-tune to public ONNX layouts and audit parity.

The input checkpoint and validation data remain local.  Only model artifacts are
written below the selected output directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from scripts.export_rc3_onnx import export_fp16_model, export_fp32_model


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def audit_parity(checkpoint: Path, fp32_dir: Path, fp16_dir: Path, valid_path: Path, max_tokens: int = 1024) -> dict:
    from erabi.inference import GLiClassEngine
    from erabi.onnx_engine import ERABIONNXEngine
    from erabi.schema import ChoiceRequest

    engines = {
        "pytorch": GLiClassEngine(str(checkpoint), device="cuda:0", max_tokens=max_tokens),
        "onnx_fp32": ERABIONNXEngine(fp32_dir, device="cpu", max_tokens=max_tokens),
        "onnx_fp16": ERABIONNXEngine(fp16_dir, device="cuda:0", max_tokens=max_tokens),
    }
    for engine in engines.values():
        preparer = engine.pipe.pipe if hasattr(engine, "pipe") else engine.preparer
        preparer.max_length = max_tokens

    rows = []
    for source in read_jsonl(valid_path):
        request = ChoiceRequest.from_dict(source)
        predictions = {
            name: engine.predict(request, return_logits=True)
            for name, engine in engines.items()
        }
        base = predictions["pytorch"]
        rows.append({
            "id": source["id"],
            "target": source["target"]["choice_id"],
            "input_tokens": base.usage.input_tokens,
            "pytorch": base.best_candidate_id,
            "onnx_fp32": predictions["onnx_fp32"].best_candidate_id,
            "onnx_fp16": predictions["onnx_fp16"].best_candidate_id,
            "fp32_max_logit_delta": max(
                abs(a - b) for a, b in zip(base.raw_logits, predictions["onnx_fp32"].raw_logits)
            ),
            "fp16_max_logit_delta": max(
                abs(a - b) for a, b in zip(base.raw_logits, predictions["onnx_fp16"].raw_logits)
            ),
            "fp16_max_probability_delta": max(
                abs(a.probability - b.probability)
                for a, b in zip(base.choices, predictions["onnx_fp16"].choices)
            ),
            "pytorch_top2_probability_margin": sorted(
                (choice.probability for choice in base.choices), reverse=True
            )[0] - sorted((choice.probability for choice in base.choices), reverse=True)[1],
        })

    count = len(rows)
    result = {
        "count": count,
        "max_tokens": max_tokens,
        "max_observed_input_tokens": max(row["input_tokens"] for row in rows),
        "top1_agreement": {
            "onnx_fp32": sum(row["pytorch"] == row["onnx_fp32"] for row in rows),
            "onnx_fp16": sum(row["pytorch"] == row["onnx_fp16"] for row in rows),
        },
        "max_logit_delta": {
            "onnx_fp32": max(row["fp32_max_logit_delta"] for row in rows),
            "onnx_fp16": max(row["fp16_max_logit_delta"] for row in rows),
        },
        "rows": rows,
        "correct_count": {name: sum(row[name] == row["target"] for row in rows)
                          for name in engines},
        "fp16_max_probability_delta": max(row["fp16_max_probability_delta"] for row in rows),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=ROOT / "runs/exam_qa_erabi_v1_finetune_20260923/checkpoint",
    )
    parser.add_argument(
        "--valid",
        type=Path,
        default=ROOT / "data/exam_qa_erabi_v1/valid.jsonl",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "runs/exam_qa_erabi_v1_finetune_20260923/onnx",
    )
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--allow-fp16-top1-differences", type=int, default=0,
                        help="Allow bounded near-tie FP16 differences; FP32 must still agree exactly")
    args = parser.parse_args()
    import torch
    torch.set_num_threads(args.threads)
    if args.allow_fp16_top1_differences < 0:
        parser.error("allowed differences must be nonnegative")

    fp32_dir = args.output_dir / "fp32"
    fp16_dir = args.output_dir / "fp16"
    fp32_model = export_fp32_model(args.checkpoint, fp32_dir)
    fp16_model = export_fp16_model(args.checkpoint, fp16_dir)
    parity = audit_parity(args.checkpoint, fp32_dir, fp16_dir, args.valid, args.max_tokens)
    report = {
        "checkpoint": {
            "path": str(args.checkpoint),
            "sha256": sha256(args.checkpoint / "model.safetensors"),
        },
        "onnx": {
            "fp32": {"path": str(fp32_model), "sha256": sha256(fp32_model)},
            "fp16": {"path": str(fp16_model), "sha256": sha256(fp16_model)},
        },
        "validation": parity,
    }
    report_path = args.output_dir / "parity_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**report, "validation": {k: v for k, v in parity.items() if k != "rows"}}, ensure_ascii=False, indent=2))
    differences = [row for row in parity["rows"] if row["pytorch"] != row["onnx_fp16"]]
    passed = (parity["top1_agreement"]["onnx_fp32"] == parity["count"]
              and len(differences) <= args.allow_fp16_top1_differences
              and parity["fp16_max_probability_delta"] <= .01
              and all(row["pytorch_top2_probability_margin"] <= .01 for row in differences))
    if not passed:
        raise RuntimeError(f"ONNX parity gate failed; inspect {report_path}")


if __name__ == "__main__":
    main()
