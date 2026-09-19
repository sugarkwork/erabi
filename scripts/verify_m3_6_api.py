"""Live local HTTP API verification script for ERABI M3.6.

Verifies:
- Starting server on 127.0.0.1:8765 with W_v2_ce10 and calibration.json.
- Verifying calibration.status == 'applied' and artifact_id matches.
- Verifying decision.status == 'review' (always enforced).
- Executing 2 sample requests (one goal_following, one explicit_rule).
- Graceful shutdown of server process.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER_PORT = 8765
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"
ROOT = Path(__file__).resolve().parent.parent


def wait_for_health(timeout: float = 30.0) -> dict:
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


def http_post(endpoint: str, payload: dict) -> tuple[int, dict]:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10.0) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"detail": body}


def main():
    model_id = str(ROOT / "runs/m3_5_ce10/trained/checkpoint")
    calib_file = str(ROOT / "runs/m3_6_calibration/calibration.json")

    env = os.environ.copy()
    env["HF_HUB_OFFLINE"] = "1"

    cmd = [
        sys.executable,
        "-m",
        "erabi.serve",
        "--model-id",
        model_id,
        "--calibration",
        calib_file,
        "--port",
        str(SERVER_PORT),
    ]

    print(f"Starting server subprocess: {' '.join(cmd)}...")
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        t_start = time.time()
        health_data = wait_for_health(timeout=30.0)
        startup_latency = round(time.time() - t_start, 2)
        print(f"Server is HEALTHY in {startup_latency}s: {health_data}")

        # Request 1: Goal following
        req1 = {
            "context": "サーバーAは256GBで30ms、サーバーBは512GBで50msです。",
            "question": "応答遅延を考慮せず、最も大容量のサーバーを一つ選んでください。",
            "choices": [
                {"id": "a", "text": "サーバーA"},
                {"id": "b", "text": "サーバーB"},
            ],
        }
        status1, resp1 = http_post("/predict", req1)
        assert status1 == 200, f"Expected 200, got {status1}: {resp1}"
        assert resp1["best_candidate_id"] == "b"
        assert resp1["decision"]["status"] == "review"
        assert resp1["calibration"]["status"] == "applied"
        assert resp1["calibration"]["artifact_id"].startswith("calib-m3_6")
        probs1 = [c["probability"] for c in resp1["choices"]]
        assert abs(sum(probs1) - 1.0) < 1e-4, "Probabilities do not sum to 1"
        print(f"Request 1 Passed: best={resp1['best_candidate_id']}, calib={resp1['calibration']}, probs={probs1}")

        # Request 2: Explicit rule boundary
        req2 = {
            "context": "測定数値はちょうど50点です。",
            "question": "ルールに従って選んでください。48点以下なら合格、48点を超えるなら不合格とします。",
            "choices": [
                {"id": "pass", "text": "合格"},
                {"id": "fail", "text": "不合格"},
            ],
        }
        status2, resp2 = http_post("/predict", req2)
        assert status2 == 200, f"Expected 200, got {status2}: {resp2}"
        assert resp2["best_candidate_id"] == "fail"
        assert resp2["decision"]["status"] == "review"
        assert resp2["calibration"]["status"] == "applied"
        probs2 = [c["probability"] for c in resp2["choices"]]
        assert abs(sum(probs2) - 1.0) < 1e-4, "Probabilities do not sum to 1"
        print(f"Request 2 Passed: best={resp2['best_candidate_id']}, calib={resp2['calibration']}, probs={probs2}")

        result_data = {
            "startup_latency_sec": startup_latency,
            "health": health_data,
            "sample_1": {
                "best": resp1["best_candidate_id"],
                "decision": resp1["decision"],
                "calibration": resp1["calibration"],
                "probabilities": resp1["choices"],
            },
            "sample_2": {
                "best": resp2["best_candidate_id"],
                "decision": resp2["decision"],
                "calibration": resp2["calibration"],
                "probabilities": resp2["choices"],
            },
        }

        out_path = ROOT / "runs/m3_6_calibration/api_verification.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        print(f"API verification saved to {out_path}")

    finally:
        print("Terminating server process...")
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server process terminated cleanly.")


if __name__ == "__main__":
    main()
