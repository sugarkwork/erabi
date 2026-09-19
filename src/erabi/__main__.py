"""ERABI CLI entrypoint for doctor, predict, and evaluate commands."""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
import platform
import shutil
import sys
import time
from typing import Any, Dict, List, Optional


def get_environment_info() -> Dict[str, Any]:
    """Collect OS, Python, PyTorch, CUDA, GPU, and disk information."""
    info: Dict[str, Any] = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "platform": platform.platform(),
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": sys.version,
        "python_executable": sys.executable,
    }

    # PyTorch and CUDA
    try:
        import torch

        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        info["cuda_version"] = torch.version.cuda
        if torch.cuda.is_available():
            info["gpu_count"] = torch.cuda.device_count()
            info["gpu_name"] = torch.cuda.get_device_name(0)
            free_bytes, total_bytes = torch.cuda.mem_get_info(0)
            info["gpu_vram_total_mb"] = round(total_bytes / (1024 * 1024), 2)
            info["gpu_vram_free_mb"] = round(free_bytes / (1024 * 1024), 2)
            info["gpu_vram_used_mb"] = round((total_bytes - free_bytes) / (1024 * 1024), 2)
        else:
            info["gpu_name"] = None
    except ImportError:
        info["torch_version"] = None
        info["cuda_available"] = False
        info["cuda_version"] = None

    # Disk usage
    cwd_disk = os.path.splitdrive(os.getcwd())[0] or "/"
    total, used, free = shutil.disk_usage(os.getcwd())
    info["disk_cwd"] = {
        "drive": cwd_disk,
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
    }

    return info


def run_doctor(args: argparse.Namespace):
    """Execute the 'doctor' diagnostic command."""
    print("=== ERABI System Doctor ===")
    info = get_environment_info()

    print(f"OS: {info['platform']}")
    print(f"Python: {info['python_version'].splitlines()[0]}")
    print(f"Python Executable: {info['python_executable']}")
    print(f"PyTorch: {info.get('torch_version', 'Not installed')}")
    print(f"CUDA Available: {info.get('cuda_available')}")
    print(f"CUDA Version: {info.get('cuda_version')}")

    if info.get("cuda_available"):
        print(f"GPU: {info.get('gpu_name')}")
        print(
            f"VRAM: Free {info.get('gpu_vram_free_mb')} MB / Total {info.get('gpu_vram_total_mb')} MB "
            f"(Used: {info.get('gpu_vram_used_mb')} MB)"
        )
    else:
        print("GPU: None detected by PyTorch")

    disk = info["disk_cwd"]
    print(f"Disk ({disk['drive']}): Free {disk['free_gb']} GB / Total {disk['total_gb']} GB")

    if args.save:
        save_path = args.save
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        print(f"\nSaved environment info to: {save_path}")


def run_predict(args: argparse.Namespace):
    """Execute the 'predict' command for a single request."""
    from erabi.inference import GLiClassEngine
    from erabi.schema import ChoiceRequest

    # Parse request JSON from argument or file
    if os.path.exists(args.request):
        with open(args.request, "r", encoding="utf-8") as f:
            raw_content = f.read()
            raw_data = json.loads(raw_content)
            byte_len = len(raw_content.encode("utf-8"))
    else:
        raw_content = args.request
        raw_data = json.loads(raw_content)
        byte_len = len(raw_content.encode("utf-8"))

    request = ChoiceRequest.from_dict(raw_data, raw_bytes_len=byte_len)

    engine = GLiClassEngine(
        model_id=args.model_id,
        device=args.device,
        revision=args.revision,
    )

    t0 = time.perf_counter()
    response = engine.predict(request, temperature=args.temperature)
    latency_ms = round((time.perf_counter() - t0) * 1000, 2)

    resp_dict = response.to_dict()
    resp_dict["usage"]["latency_ms"] = latency_ms

    print(json.dumps(resp_dict, indent=2, ensure_ascii=False))


def load_and_verify_calibration(calib_path: str, model_id: str):
    """Load calibration artifact and verify file hashes and runtime contract against target model checkpoint."""
    from erabi.schema import (
        ALLOWED_CALIBRATION_STATUSES,
        CalibrationOutput,
        FORMATTER_VERSION,
        MAX_TOKENS,
        SCHEMA_VERSION,
        compute_file_sha256,
    )

    if not os.path.isfile(calib_path):
        raise FileNotFoundError(f"Calibration artifact not found at '{calib_path}'")

    with open(calib_path, "r", encoding="utf-8") as f:
        calib_data = json.load(f)

    if "temperature" not in calib_data:
        raise ValueError("Calibration artifact missing 'temperature' field.")
    temp = float(calib_data["temperature"])
    if not math.isfinite(temp) or temp <= 0.0:
        raise ValueError(f"Calibration temperature must be positive and finite, got {temp}")

    status = calib_data.get("status", "none")
    if status not in ALLOWED_CALIBRATION_STATUSES:
        raise ValueError(
            f"Invalid calibration status '{status}'. Must be one of {sorted(ALLOWED_CALIBRATION_STATUSES)}."
        )

    if status == "applied":
        # 1. Enforce local checkpoint directory presence
        if not os.path.isdir(model_id):
            raise FileNotFoundError(
                f"Calibration target model directory '{model_id}' does not exist or is not a directory."
            )

        target_model = calib_data.get("target_model")
        if not target_model or not isinstance(target_model, dict):
            raise ValueError("Calibration status is 'applied' but 'target_model' information is missing.")
        target_files = target_model.get("files")
        if not target_files or not isinstance(target_files, dict):
            raise ValueError("Calibration status is 'applied' but 'target_model.files' is empty or invalid.")

        # Check required files for baseline checkpoint
        required_checkpoint_files = [
            "model.safetensors",
            "config.json",
            "tokenizer.json",
            "tokenizer_config.json",
        ]
        for required_file in required_checkpoint_files:
            if required_file not in target_files:
                raise ValueError(
                    f"Required model file '{required_file}' missing from calibration target_model.files."
                )

        for fname, expected_hash in target_files.items():
            fpath = os.path.join(model_id, fname)
            if not os.path.isfile(fpath):
                raise FileNotFoundError(f"Calibration target model file missing from checkpoint: {fname}")
            actual_hash = compute_file_sha256(fpath)
            if actual_hash != expected_hash:
                raise ValueError(
                    f"Calibration hash mismatch for '{fname}': expected {expected_hash}, got {actual_hash}"
                )

        # 2. Verify runtime contract
        contract = calib_data.get("contract")
        if not contract or not isinstance(contract, dict):
            raise ValueError("Calibration artifact missing 'contract' object.")

        cal_schema = str(contract.get("schema_version", ""))
        if cal_schema != SCHEMA_VERSION:
            raise ValueError(
                f"Calibration contract schema mismatch: expected '{SCHEMA_VERSION}', got '{cal_schema}'"
            )

        cal_max_tokens = contract.get("max_tokens")
        if cal_max_tokens != MAX_TOKENS:
            raise ValueError(
                f"Calibration contract max_tokens mismatch: expected {MAX_TOKENS}, got {cal_max_tokens}"
            )

        cal_formatter = contract.get("formatter_version")
        if not cal_formatter or cal_formatter != FORMATTER_VERSION:
            raise ValueError(
                f"Calibration contract formatter_version mismatch: expected '{FORMATTER_VERSION}', got '{cal_formatter}'"
            )

        from erabi.schema import RUNTIME_PRECISION_CONTRACT

        precision = contract.get("precision")
        if precision != RUNTIME_PRECISION_CONTRACT:
            raise ValueError(
                f"Calibration contract precision mismatch: expected '{RUNTIME_PRECISION_CONTRACT}', got '{precision}'"
            )

    artifact_id = calib_data.get("artifact_id")
    calib_out = CalibrationOutput(status=status, artifact_id=artifact_id)
    return temp, calib_out, calib_data


def run_evaluate(args: argparse.Namespace):
    """Execute the 'evaluate' command on a JSONL benchmark dataset."""
    from erabi.evaluate import compute_metrics
    from erabi.inference import GLiClassEngine
    from erabi.schema import ChoiceRequest, CalibrationOutput

    input_file = args.input
    if not os.path.exists(input_file):
        print(f"Error: input file '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Prepare output directory
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"eval_{timestamp_str}"
    output_dir = args.output_dir or os.path.join("runs", run_id)
    os.makedirs(output_dir, exist_ok=True)

    calib_out = CalibrationOutput(status="none", artifact_id=None)
    eval_temp = args.temperature
    calib_info = None

    if args.calibration:
        if not os.path.exists(args.calibration):
            print(f"Error: calibration file '{args.calibration}' not found.", file=sys.stderr)
            sys.exit(1)
        eval_temp, calib_out, calib_info = load_and_verify_calibration(args.calibration, args.model_id)
        print(f"Loaded calibration from {args.calibration}: T={eval_temp:.4f}, status={calib_out.status}")

    print(f"=== ERABI Evaluation ===")
    print(f"Input: {input_file}")
    print(f"Output Directory: {output_dir}")
    print(f"Loading model: {args.model_id}...")

    engine = GLiClassEngine(
        model_id=args.model_id,
        device=args.device,
        revision=args.revision,
    )

    records = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    print(f"Loaded {len(records)} test cases.")

    predictions = []
    targets = []
    log_rows = []
    latencies = []

    # Warmup on first item
    print("Running warmup pass...")
    first_req = ChoiceRequest.from_dict(records[0])
    engine.predict(first_req)

    print("Evaluating test cases...")
    for idx, row in enumerate(records):
        req = ChoiceRequest.from_dict(row)
        target_kind = row.get("target", {}).get("kind", "hard")
        target_choice_id = row.get("target", {}).get("choice_id")

        t0 = time.perf_counter()
        resp = engine.predict(
            req,
            temperature=eval_temp,
            return_logits=True,
            calibration=calib_out,
        )
        lat = (time.perf_counter() - t0) * 1000
        latencies.append(lat)

        pred_dict = resp.to_dict()
        predictions.append(pred_dict)
        targets.append(target_choice_id)

        is_match = (resp.best_candidate_id == target_choice_id)
        log_row = {
            "id": row.get("id", f"case-{idx+1}"),
            "group_id": row.get("group_id"),
            "task_family": row.get("task_family"),
            "target": target_choice_id,
            "predicted": resp.best_candidate_id,
            "is_correct": is_match,
            "probabilities": {c["id"]: c["probability"] for c in pred_dict["choices"]},
            "raw_logits": pred_dict.get("raw_logits"),
            "latency_ms": round(lat, 2),
            "input_tokens": resp.usage.input_tokens,
        }
        log_rows.append(log_row)

    metrics = compute_metrics(predictions, targets, metadata=records, temperature=eval_temp)
    metrics["latency_p50_ms"] = round(sorted(latencies)[len(latencies) // 2], 2)
    metrics["latency_p95_ms"] = round(sorted(latencies)[int(len(latencies) * 0.95)], 2)
    metrics["latency_mean_ms"] = round(sum(latencies) / len(latencies), 2)
    metrics["applied_temperature"] = eval_temp
    metrics["calibration_status"] = calib_out.status

    # Save artifacts in runs/<run_id>/
    # 1. environment.json
    env_info = get_environment_info()
    with open(os.path.join(output_dir, "environment.json"), "w", encoding="utf-8") as f:
        json.dump(env_info, f, indent=2, ensure_ascii=False)

    # 2. config.json
    config_data = {
        "model_id": args.model_id,
        "revision": args.revision,
        "device": engine.device,
        "temperature": eval_temp,
        "calibration_artifact": args.calibration,
        "calibration_status": calib_out.status,
        "input_file": input_file,
    }
    with open(os.path.join(output_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)

    # 3. metrics.json
    with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # 4. predictions.jsonl
    with open(os.path.join(output_dir, "predictions.jsonl"), "w", encoding="utf-8") as f:
        for r in log_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 5. notes.md
    with open(os.path.join(output_dir, "notes.md"), "w", encoding="utf-8") as f:
        f.write(f"# Evaluation Notes: {run_id}\n\n")
        f.write(f"- Model: {args.model_id}\n")
        f.write(f"- Device: {engine.device}\n")
        f.write(f"- Accuracy: {metrics['accuracy']:.4f}\n")
        f.write(f"- Mean NLL: {metrics['mean_nll']:.4f}\n")
        f.write(f"- Mean Brier: {metrics['mean_brier']:.4f}\n")
        f.write(f"- Latency p50: {metrics['latency_p50_ms']} ms\n")
        f.write(f"- Latency p95: {metrics['latency_p95_ms']} ms\n")
        if "pair_metrics" in metrics:
            f.write(f"- Pair Both Correct Rate: {metrics['pair_metrics']['both_correct_rate']:.4f} ({metrics['pair_metrics']['both_correct_pairs']}/{metrics['pair_metrics']['total_pairs']})\n")

    # Print summary
    print("\n--- Evaluation Summary ---")
    print(f"Total Cases: {metrics['count']}")
    print(f"Accuracy: {metrics['accuracy'] * 100:.2f}% ({metrics['correct_count']}/{metrics['count']})")
    print(f"Mean NLL: {metrics['mean_nll']:.4f}")
    print(f"Mean Brier: {metrics['mean_brier']:.4f}")
    if "pair_metrics" in metrics:
        pm = metrics["pair_metrics"]
        print(f"Pair Both Correct: {pm['both_correct_rate']*100:.2f}% ({pm['both_correct_pairs']}/{pm['total_pairs']})")
    if "task_family_breakdown" in metrics:
        print("Task Family Breakdown:")
        for tf, stat in metrics["task_family_breakdown"].items():
            print(f"  {tf}: {stat['accuracy']*100:.1f}% ({stat['correct']}/{stat['count']})")
    if "template_family_breakdown" in metrics:
        print("Template Family Breakdown:")
        for tpl, stat in metrics["template_family_breakdown"].items():
            print(f"  {tpl}: {stat['accuracy']*100:.1f}% ({stat['correct']}/{stat['count']})")
    print(f"Latency p50: {metrics['latency_p50_ms']} ms | p95: {metrics['latency_p95_ms']} ms")
    print("\nReliability Bins:")
    for b in metrics["reliability_bins"]:
        acc_str = f"{b['accuracy'] * 100:.1f}%" if b['accuracy'] is not None else "N/A"
        conf_str = f"{b['avg_confidence']:.3f}" if b['avg_confidence'] is not None else "N/A"
        print(f"  {b['bin']}: count={b['count']}, avg_conf={conf_str}, acc={acc_str}")

    print(f"\nArtifacts saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        prog="python -m erabi",
        description="ERABI - Local probability distribution engine for variable choices.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # doctor
    parser_doctor = subparsers.add_parser("doctor", help="Inspect system and environment.")
    parser_doctor.add_argument("--save", type=str, default=None, help="Path to save environment JSON.")

    # predict
    parser_predict = subparsers.add_parser("predict", help="Run inference on a single request.")
    parser_predict.add_argument("--request", type=str, required=True, help="JSON string or path to JSON file.")
    parser_predict.add_argument("--model-id", type=str, default="knowledgator/gliclass-multilang-mini", help="Hugging Face model ID.")
    parser_predict.add_argument("--revision", type=str, default=None, help="Model revision or commit hash.")
    parser_predict.add_argument("--device", type=str, default=None, help="Device to use (e.g. cuda:0 or cpu).")
    parser_predict.add_argument("--temperature", type=float, default=1.0, help="Temperature for softmax.")

    # evaluate
    parser_eval = subparsers.add_parser("evaluate", help="Run evaluation on a JSONL benchmark.")
    parser_eval.add_argument("--input", type=str, required=True, help="Path to JSONL input file.")
    parser_eval.add_argument("--output-dir", type=str, default=None, help="Directory to save evaluation artifacts.")
    parser_eval.add_argument("--model-id", type=str, default="knowledgator/gliclass-multilang-mini", help="Hugging Face model ID.")
    parser_eval.add_argument("--revision", type=str, default=None, help="Model revision or commit hash.")
    parser_eval.add_argument("--device", type=str, default=None, help="Device to use (e.g. cuda:0 or cpu).")
    parser_eval.add_argument("--temperature", type=float, default=1.0, help="Temperature for softmax.")
    parser_eval.add_argument("--calibration", type=str, default=None, help="Path to calibration.json.")

    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor(args)
    elif args.command == "predict":
        run_predict(args)
    elif args.command == "evaluate":
        run_evaluate(args)


if __name__ == "__main__":
    main()
