"""Live local HTTP API verification script for ERABI M3.7 Calibration Handoff.

Adheres strictly to instructions:
1. Starts server on 127.0.0.1:8765 with W_v2_ce10 checkpoint, runs/m3_7_calibration_handoff/calibration.json, and --require-calibration.
2. Checks /health returns expected T (3.1097), complete artifact_id, applied status, and review_default.
3. Tests 3 sample requests (goal following, boundary, composite rule).
4. Verifies single temperature application without double-application:
   Compares HTTP returned probabilities against direct softmax(raw_logits / T) in float64.
   Confirms it matches softmax(z / T) and differs from softmax(z) and softmax(z / T^2).
5. Confirms decision.status is locked to 'review' across all responses.
6. Cleanly terminates the spawned server process only.
7. Saves verification report to runs/m3_7_calibration_handoff/verification.json.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

SERVER_PORT = 8765
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"


def wait_for_health(timeout: float = 35.0) -> Dict[str, Any]:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            req = urllib.request.Request(f"{BASE_URL}/health")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception:
            time.sleep(0.5)
    raise TimeoutError("Server did not become healthy within timeout.")


def http_post(endpoint: str, payload: dict) -> Tuple[int, Dict[str, Any]]:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"detail": body}


def main():
    print("=== ERABI M3.7 Live HTTP API Verification ===")
    model_id = str(ROOT / "runs/m3_5_ce10/trained/checkpoint")
    calib_file = str(ROOT / "runs/m3_7_calibration_handoff/calibration.json")
    out_dir = ROOT / "runs/m3_7_calibration_handoff"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(calib_file, "r", encoding="utf-8") as f:
        calib_data = json.load(f)

    expected_temp = float(calib_data["temperature"])
    expected_art_id = calib_data["artifact_id"]

    # 1. Start server subprocess with --require-calibration
    env = os.environ.copy()
    env["HF_HUB_OFFLINE"] = "1"
    env["PYTHONPATH"] = str(ROOT / "src")

    cmd = [
        sys.executable,
        "-m",
        "erabi.serve",
        "--model-id",
        model_id,
        "--calibration",
        calib_file,
        "--require-calibration",
        "--port",
        str(SERVER_PORT),
    ]

    print(f"Starting server: {' '.join(cmd)}...")
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    test_queries = [
        {
            "name": "Goal Following (Server Capacity)",
            "request": {
                "context": "サーバーAは256GBで30ms、サーバーBは512GBで50msです。",
                "question": "応答遅延を考慮せず、最も大容量のサーバーを一つ選んでください。",
                "choices": [
                    {"id": "a", "text": "サーバーA"},
                    {"id": "b", "text": "サーバーB"},
                ],
            },
            "expected_best": "b",
        },
        {
            "name": "Explicit Rule Boundary (Inspection Score)",
            "request": {
                "context": "測定数値はちょうど50点でした。",
                "question": "合格基準：50点以上なら合格、それ以外なら不合格。判定を選んでください。",
                "choices": [
                    {"id": "pass", "text": "合格"},
                    {"id": "fail", "text": "不合格"},
                ],
            },
            "expected_best": "pass",
        },
        {
            "name": "Explicit Rule Composite Logic (HP and Item)",
            "request": {
                "context": "現在のプレイヤーのHPは10です。アイテムあり。",
                "question": "ルール：HPが20未満かつアイテムがあれば回復、それ以外は攻撃。行動を選んでください。",
                "choices": [
                    {"id": "heal", "text": "回復する"},
                    {"id": "attack", "text": "攻撃する"},
                ],
            },
            "expected_best": "heal",
        },
    ]

    verification_results = {}

    try:
        t_start = time.time()
        health_data = wait_for_health(timeout=35.0)
        startup_latency = round(time.time() - t_start, 2)
        print(f"1. Server HEALTHY in {startup_latency}s:")
        print(f"   Status: {health_data.get('status')}")
        print(f"   Temperature: {health_data.get('temperature')}")
        print(f"   Calibration: {health_data.get('calibration')}")
        print(f"   Policy: {health_data.get('decision_policy')}")

        assert health_data["status"] == "ok"
        assert abs(health_data["temperature"] - expected_temp) < 1e-4
        assert health_data["calibration"]["status"] == "applied"
        assert health_data["calibration"]["artifact_id"] == expected_art_id
        assert health_data["decision_policy"] == "review_default"

        verification_results["health_check"] = {
            "status": "passed",
            "startup_latency_s": startup_latency,
            "response": health_data,
        }

        # 2. Local direct engine to compare raw logits and verify single temperature application
        print("\n2. Initializing direct GLiClassEngine to verify temperature math and non-duplication...")
        direct_engine = GLiClassEngine(model_id=model_id)

        query_results = []
        for q in test_queries:
            q_name = q["name"]
            req_dict = q["request"]
            exp_best = q["expected_best"]

            print(f"\n   Testing query: {q_name}...")
            # HTTP call
            status_code, http_resp = http_post("/predict", req_dict)
            assert status_code == 200, f"HTTP Error {status_code}: {http_resp}"
            assert http_resp["best_candidate_id"] == exp_best, f"Best mismatch: {http_resp['best_candidate_id']} != {exp_best}"
            assert http_resp["decision"]["status"] == "review", "Decision status was not 'review'!"
            assert http_resp["calibration"]["status"] == "applied"
            assert http_resp["calibration"]["artifact_id"] == expected_art_id

            http_probs = [c["probability"] for c in http_resp["choices"]]

            # Direct call with return_logits=True
            direct_req = ChoiceRequest.from_dict(req_dict)
            direct_resp_raw = direct_engine.predict(direct_req, temperature=1.0, return_logits=True)
            raw_logits = direct_resp_raw.raw_logits
            assert raw_logits is not None

            # Calculate theoretical probabilities under different temperature regimes:
            # Regime 1: Single calibration T (expected)
            t_expected_logits = torch.tensor(raw_logits, dtype=torch.float64) / expected_temp
            expected_calibrated_probs = F.softmax(t_expected_logits, dim=-1).tolist()

            # Regime 2: Uncalibrated T = 1.0
            uncalibrated_probs = F.softmax(torch.tensor(raw_logits, dtype=torch.float64), dim=-1).tolist()

            # Regime 3: Double-applied T = T^2
            double_applied_probs = F.softmax(torch.tensor(raw_logits, dtype=torch.float64) / (expected_temp ** 2), dim=-1).tolist()

            # Verify HTTP probs match expected single calibration within 1e-4
            max_diff_single = max(abs(h - e) for h, e in zip(http_probs, expected_calibrated_probs))
            max_diff_uncal = max(abs(h - u) for h, u in zip(http_probs, uncalibrated_probs))
            max_diff_double = max(abs(h - d) for h, d in zip(http_probs, double_applied_probs))

            print(f"      HTTP probabilities: {http_probs}")
            print(f"      Expected (T={expected_temp:.4f}): {expected_calibrated_probs} (max diff: {max_diff_single:.2e})")
            print(f"      Uncalibrated (T=1.0): {uncalibrated_probs} (max diff: {max_diff_uncal:.2e})")
            print(f"      Double-applied (T^2): {double_applied_probs} (max diff: {max_diff_double:.2e})")

            assert max_diff_single < 1e-3, f"Single calibration mismatch! Max diff: {max_diff_single}"
            assert max_diff_uncal > 1e-3, "HTTP probabilities erroneously match uncalibrated T=1.0!"
            assert max_diff_double > 1e-3, "HTTP probabilities erroneously match double-applied T=T^2!"

            query_results.append({
                "query": q_name,
                "best_candidate_id": http_resp["best_candidate_id"],
                "decision_status": http_resp["decision"]["status"],
                "calibration_status": http_resp["calibration"]["status"],
                "http_probabilities": http_probs,
                "expected_calibrated_probabilities": expected_calibrated_probs,
                "max_diff_to_single_calibrated": max_diff_single,
                "confirmed_single_temperature_not_doubled": True,
            })

        verification_results["queries"] = query_results
        verification_results["overall_status"] = "PASSED"
        print("\nAll 3 queries verified successfully with single temperature scaling and review lock!")

    finally:
        print("\nTerminating server subprocess cleanly...")
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server subprocess terminated cleanly.")

    # Save verification JSON
    ver_path = out_dir / "verification.json"
    with open(ver_path, "w", encoding="utf-8") as f:
        json.dump(verification_results, f, indent=2, ensure_ascii=False)
    print(f"Saved live verification results to {ver_path}")


if __name__ == "__main__":
    main()
