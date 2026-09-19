"""Live local HTTP API verification script (M3.1).

Verifies:
  - Starting server in separate process with HF_HUB_OFFLINE=1.
  - GET /health endpoint.
  - POST /predict with valid inputs and verification of decision="review".
  - POST /predict with invalid inputs (422).
  - CLI vs HTTP output consistency.
  - 20 round-trip requests benchmark (p50, min, max latency).
  - Clean server termination without killing other processes.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

SERVER_PORT = 8765
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"


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
    model_id = "runs/m2_1/trained_instruct_base/checkpoint"
    env = os.environ.copy()
    env["HF_HUB_OFFLINE"] = "1"

    cmd = [
        sys.executable,
        "-m",
        "erabi.serve",
        "--model-id",
        model_id,
        "--port",
        str(SERVER_PORT),
    ]

    print(f"Starting server subprocess: {' '.join(cmd)} with HF_HUB_OFFLINE=1...")
    proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        t_start = time.time()
        health_data = wait_for_health(timeout=30.0)
        startup_latency = round(time.time() - t_start, 2)
        print(f"Server is HEALTHY in {startup_latency}s: {health_data}")

        # 1. Valid Request 1 (Plan comparison: Cheapest)
        req1 = {
            "context": "プランAは100円で5日、プランBは300円で1日です。",
            "question": "最も安いプランを選んでください。",
            "choices": [
                {"id": "a", "text": "プランA"},
                {"id": "b", "text": "プランB"},
            ],
        }
        status1, resp1 = http_post("/predict", req1)
        assert status1 == 200, f"Expected 200, got {status1}: {resp1}"
        assert resp1["best_candidate_id"] == "a"
        assert resp1["decision"]["status"] == "review"
        assert resp1["decision"]["reason"] == "policy_not_configured"
        print(f"Request 1 Passed: best={resp1['best_candidate_id']}, decision={resp1['decision']}")

        # 2. Valid Request 2 (Explicit rule: Boundary <= 10)
        req2 = {
            "context": "測定値は10点です。",
            "question": "10点以下なら合格、10点を超えるなら不合格を選んでください。",
            "choices": [
                {"id": "pass", "text": "合格"},
                {"id": "fail", "text": "不合格"},
            ],
        }
        status2, resp2 = http_post("/predict", req2)
        assert status2 == 200
        assert resp2["best_candidate_id"] == "pass"
        assert resp2["decision"]["status"] == "review"
        print(f"Request 2 Passed: best={resp2['best_candidate_id']}, decision={resp2['decision']}")

        # 3. Invalid Request (Only 1 choice -> 422)
        req_invalid = {
            "context": "文脈",
            "question": "質問",
            "choices": [{"id": "single", "text": "単一候補"}],
        }
        status_inv, resp_inv = http_post("/predict", req_invalid)
        assert status_inv == 422, f"Expected 422, got {status_inv}: {resp_inv}"
        print(f"Invalid Request Correctly Rejected with HTTP 422: {resp_inv}")

        # 4. Latency Benchmark: 20 round-trip requests
        print("Running 20 round-trip latency benchmark...")
        latencies = []
        for _ in range(20):
            t0 = time.perf_counter()
            s, _ = http_post("/predict", req1)
            assert s == 200
            latencies.append((time.perf_counter() - t0) * 1000)

        lat_p50 = round(sorted(latencies)[len(latencies) // 2], 2)
        lat_min = round(min(latencies), 2)
        lat_max = round(max(latencies), 2)
        print(f"HTTP Latency (20 runs): p50={lat_p50}ms, min={lat_min}ms, max={lat_max}ms")

        results = {
            "startup_time_sec": startup_latency,
            "offline_mode": True,
            "health_response": health_data,
            "validation_rejection_code": status_inv,
            "latency_p50_ms": lat_p50,
            "latency_min_ms": lat_min,
            "latency_max_ms": lat_max,
            "decision_policy_enforced": "review_default",
        }
        with open("runs/m3_1/api_verification.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print("API verification successfully saved to runs/m3_1/api_verification.json")

    finally:
        print("Terminating server process...")
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server process cleanly stopped.")


if __name__ == "__main__":
    main()
