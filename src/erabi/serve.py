"""CLI server runner for ERABI local API (M3.1).

Enforces:
  - 127.0.0.1 loopback only.
  - 1 worker, no reload.
  - Rejection of external host binding.
"""

from __future__ import annotations

import argparse
import os
import sys
import uvicorn
from erabi.api import create_app
from erabi.model_loader import MODEL_FORMATS

ALLOWED_HOSTS = {"127.0.0.1", "localhost"}


def main():
    parser = argparse.ArgumentParser(prog="python -m erabi.serve", description="ERABI local HTTP API server")
    parser.add_argument("--model-id", type=str, required=True, help="Local model directory or Hugging Face model ID (explicitly required)")
    parser.add_argument("--model-format", choices=MODEL_FORMATS, default=os.environ.get("ERABI_MODEL_FORMAT", "auto"), help="auto, pytorch, onnx-fp32, or onnx-fp16")
    parser.add_argument("--model-cache-dir", type=str, default=None, help="Directory for downloaded model files (also settable via ERABI_MODEL_CACHE_DIR)")
    parser.add_argument("--calibration", type=str, default=None, help="Path to calibration.json")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Bind host (loopback only: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Bind port (default: 8765)")
    parser.add_argument("--device", type=str, default=None, help="Device to use")
    parser.add_argument("--require-calibration", action="store_true", help="Fail startup if calibration is missing/unstable")

    args = parser.parse_args()

    if args.host not in ALLOWED_HOSTS:
        print(f"Security error: Binding to '{args.host}' is prohibited. Only loopback (127.0.0.1) is permitted.", file=sys.stderr)
        sys.exit(1)

    app = create_app(
        model_id=args.model_id,
        model_format=args.model_format,
        calibration_path=args.calibration,
        device=args.device,
        model_cache_dir=args.model_cache_dir,
        require_calibration=args.require_calibration,
    )

    print(f"Starting ERABI Local Engine on http://{args.host}:{args.port}")
    print(f"Model: {args.model_id}")
    print(f"Calibration: {args.calibration or 'None (uncalibrated mode)'}")
    print(f"Decision policy: review_default")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=1,
        reload=False,
        access_log=False,
    )


if __name__ == "__main__":
    main()
