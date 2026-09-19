"""Generate M3.7.1 contract fix artifacts in runs/m3_7_1_contract_fix/.

Responsibilities:
1. Copy/migrate calibration.json to runs/m3_7_1_contract_fix/ with strict contract precision and tokenizer hashes.
2. Regenerate sidecar manifests for raw_logits_calibration.jsonl and raw_logits_fresh_eval.jsonl with alignment_sha256.
3. Verify live HTTP API with --require-calibration on runs/m3_7_1_contract_fix/calibration.json.
4. Cleanly terminate server and output verification.json.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.__main__ import load_and_verify_calibration
from erabi.cache import load_logits_with_manifest, save_logits_with_manifest
from erabi.calibrate import build_calibration_artifact
from erabi.schema import FORMATTER_VERSION, RUNTIME_PRECISION_CONTRACT

OUT_DIR = ROOT / "runs/m3_7_1_contract_fix"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_DIR = ROOT / "runs/m3_5_ce10/trained/checkpoint"
CAL_DATA_PATH = ROOT / "data/m3_6_cal/calibration.jsonl"
FRESH_DATA_PATH = ROOT / "data/m3_6_cal/fresh_eval.jsonl"

M3_7_CAL_LOGITS = ROOT / "runs/m3_7_calibration_handoff/raw_logits_calibration.jsonl"
M3_7_FRESH_LOGITS = ROOT / "runs/m3_7_calibration_handoff/raw_logits_fresh_eval.jsonl"


def main():
    print("=== ERABI M3.7.1 Contract Fix Migration ===")

    # 1. Regenerate sidecars with alignment_sha256
    print("1. Regenerating sidecar manifests with alignment_sha256...")
    cal_records = [json.loads(line) for line in open(M3_7_CAL_LOGITS, encoding="utf-8") if line.strip()]
    fresh_records = [json.loads(line) for line in open(M3_7_FRESH_LOGITS, encoding="utf-8") if line.strip()]

    meta = {
        "migration_stage": "m3_7_1_contract_fix",
        "alignment_sha256_verified": True,
        "precision_contract": RUNTIME_PRECISION_CONTRACT,
    }

    cal_manifest = save_logits_with_manifest(
        logits_path=OUT_DIR / "raw_logits_calibration.jsonl",
        raw_records=cal_records,
        model_dir=MODEL_DIR,
        data_path=CAL_DATA_PATH,
        precision=RUNTIME_PRECISION_CONTRACT,
        formatter_version=FORMATTER_VERSION,
        extra_metadata=meta,
    )
    fresh_manifest = save_logits_with_manifest(
        logits_path=OUT_DIR / "raw_logits_fresh_eval.jsonl",
        raw_records=fresh_records,
        model_dir=MODEL_DIR,
        data_path=FRESH_DATA_PATH,
        precision=RUNTIME_PRECISION_CONTRACT,
        formatter_version=FORMATTER_VERSION,
        extra_metadata=meta,
    )

    # Verify loading with alignment digest
    loaded_cal = load_logits_with_manifest(
        logits_path=OUT_DIR / "raw_logits_calibration.jsonl",
        model_dir=MODEL_DIR,
        data_path=CAL_DATA_PATH,
    )
    assert len(loaded_cal) == 200
    print("   Verified loading calibration logits with alignment_sha256.")

    loaded_fresh = load_logits_with_manifest(
        logits_path=OUT_DIR / "raw_logits_fresh_eval.jsonl",
        model_dir=MODEL_DIR,
        data_path=FRESH_DATA_PATH,
    )
    assert len(loaded_fresh) == 200
    print("   Verified loading fresh_eval logits with alignment_sha256.")

    # 2. Build updated calibration artifact
    print("2. Building updated calibration.json with exact precision contract and required tokenizer hashes...")
    fixed_internal_temperature = 3.109686582278409
    fixed_rounded_temperature = 3.1097
    cal_artifact = build_calibration_artifact(
        temperature=fixed_rounded_temperature,
        status="applied",
        checkpoint_dir=str(MODEL_DIR),
        dataset_path=str(CAL_DATA_PATH),
        dataset_cases=len(cal_records),
        dataset_description="ERABI synthetic rule calibration set (100 pairs / 200 cases)",
        optimization_info={
            "initial_T": 1.0,
            "initial_nll": 0.3436121838662325,
            "optimal_T": fixed_internal_temperature,
            "optimal_T_rounded": fixed_rounded_temperature,
            "optimal_nll": 0.1572337202450454,
            "improvement": 0.1863784636211871,
            "eval_count": 12,
            "success": True,
            "is_at_boundary": False,
            "bounds": [0.05, 20.0],
            "boundary_status": "inside_bounds_not_reached",
        },
        adoption_decision="ACCEPT_SCOPED",
        adoption_reason="NLL improved by 0.186378 on calibration set. Fresh eval confirmed NLL improvement 0.348948 -> 0.167539.",
        scope="bounded_synthetic_rules_only (2-3 choices, validated synthetic templates and vocabularies)",
        precision=RUNTIME_PRECISION_CONTRACT,
        artifact_id="calib-m3-7-1-scoped-w-v2-ce10",
    )
    cal_artifact_path = OUT_DIR / "calibration.json"
    with open(cal_artifact_path, "w", encoding="utf-8") as f:
        json.dump(cal_artifact, f, indent=2, ensure_ascii=False)

    # Test load_and_verify_calibration
    t_val, cal_out, _ = load_and_verify_calibration(str(cal_artifact_path), str(MODEL_DIR))
    assert t_val == 3.1097
    assert cal_out.status == "applied"
    print("   load_and_verify_calibration PASSED for new artifact.")

    # 3. Live API Verification with --require-calibration
    print("3. Testing live HTTP API with --require-calibration...")
    env = os.environ.copy()
    env["HF_HUB_OFFLINE"] = "1"
    env["PYTHONPATH"] = str(ROOT / "src")

    server_port = 8766
    cmd = [
        sys.executable,
        "-m",
        "erabi.serve",
        "--model-id",
        str(MODEL_DIR),
        "--calibration",
        str(cal_artifact_path),
        "--require-calibration",
        "--port",
        str(server_port),
    ]

    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    base_url = f"http://127.0.0.1:{server_port}"
    api_report = {}

    try:
        # Wait for health
        t0 = time.time()
        healthy = False
        health_data = None
        while time.time() - t0 < 30.0:
            try:
                req = urllib.request.Request(f"{base_url}/health")
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    if resp.status == 200:
                        health_data = json.loads(resp.read().decode("utf-8"))
                        healthy = True
                        break
            except Exception:
                time.sleep(0.5)

        assert healthy, "Server did not become healthy!"
        print(f"   Server is HEALTHY in {round(time.time() - t0, 2)}s: {health_data}")
        assert health_data["temperature"] == 3.1097
        assert health_data["calibration"]["status"] == "applied"

        # Query 1
        q_payload = {
            "context": "サーバーAは256GBで30ms、サーバーBは512GBで50msです。",
            "question": "応答遅延を考慮せず、最も大容量のサーバーを一つ選んでください。",
            "choices": [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}],
        }
        data_bytes = json.dumps(q_payload).encode("utf-8")
        req_post = urllib.request.Request(
            f"{base_url}/predict",
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req_post, timeout=10.0) as resp:
            pred_resp = json.loads(resp.read().decode("utf-8"))

        assert pred_resp["best_candidate_id"] == "b"
        assert pred_resp["decision"]["status"] == "review"
        assert pred_resp["calibration"]["status"] == "applied"
        print(f"   Sample inference succeeded: best={pred_resp['best_candidate_id']}, decision={pred_resp['decision']['status']}")

        api_report["health"] = health_data
        api_report["sample_inference"] = pred_resp
        api_report["status"] = "PASSED"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("   Server cleanly terminated.")

    with open(OUT_DIR / "verification.json", "w", encoding="utf-8") as f:
        json.dump(api_report, f, indent=2, ensure_ascii=False)

    print("=== M3.7.1 Contract Fix Migration Complete ===")


if __name__ == "__main__":
    main()
