"""FastAPI application factory for ERABI local inference API (M3.1).

Guarantees:
  - 127.0.0.1 loopback only.
  - Model loaded once at startup via lifespan events; unloaded at shutdown.
  - 1-concurrency inference protection: returns HTTP 503 if busy.
  - Decision is strictly locked to status='review' on all predictions.
  - Calibration hash verification against model checkpoint on startup.
  - Request byte limit (65,536 bytes) -> 413.
  - Validation error -> 422.
  - Swagger/ReDoc disabled.
"""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, Optional

from erabi.inference import GLiClassEngine
from erabi.schema import (
    ChoiceRequest,
    ChoiceResponse,
    CalibrationOutput,
    DecisionOutput,
    ValidationError,
    MAX_REQUEST_BYTES,
)
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("erabi.api")


def create_app(
    model_id: str,
    calibration_path: Optional[str] = None,
    device: Optional[str] = None,
    require_calibration: bool = False,
    engine_factory: Optional[Callable[[], Any]] = None,
    model_cache_dir: Optional[str] = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.lock = asyncio.Lock()
        app.state.temperature = 1.0
        app.state.calibration_output = CalibrationOutput(status="none", artifact_id=None)

        if require_calibration and not calibration_path:
            raise RuntimeError(
                "Calibration is required (--require-calibration), but no calibration_path was provided."
            )

        if calibration_path:
            from erabi.__main__ import load_and_verify_calibration

            logger.info(f"Verifying and loading calibration from {calibration_path}...")
            temp, calib_out, calib_data = load_and_verify_calibration(calibration_path, model_id)
            if calib_out.status == "applied":
                app.state.temperature = temp
                app.state.calibration_output = calib_out
                logger.info(f"Calibration applied: T={temp:.4f}, artifact_id={calib_out.artifact_id}")
            else:
                if require_calibration:
                    raise RuntimeError(
                        f"Calibration artifact status is '{calib_out.status}', but calibration was required."
                    )
                logger.warning(
                    f"Calibration status is '{calib_out.status}'. Starting in uncalibrated mode (T=1.0)."
                )
                app.state.temperature = 1.0
                app.state.calibration_output = CalibrationOutput(status="none", artifact_id=None)

        logger.info(f"Initializing engine for model: {model_id}...")
        if engine_factory:
            app.state.engine = engine_factory()
        else:
            app.state.engine = GLiClassEngine(model_id=model_id, device=device, cache_dir=model_cache_dir)

        yield

        logger.info("Shutting down engine...")
        app.state.engine = None

    app = FastAPI(
        title="ERABI Local Engine",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=exc.to_dict(),
        )

    @app.get("/health")
    async def health_check():
        if not getattr(app.state, "engine", None):
            raise HTTPException(status_code=503, detail="Engine not initialized")
        return {
            "status": "ok",
            "model_id": app.state.engine.model_id,
            "calibration": {
                "status": app.state.calibration_output.status,
                "artifact_id": app.state.calibration_output.artifact_id,
            },
            "temperature": app.state.temperature,
            "decision_policy": "review_default",
        }

    async def handle_choice_inference(request: Request):
        # 1. Byte limit check
        raw_body = await request.body()
        raw_len = len(raw_body)
        if raw_len > MAX_REQUEST_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request size ({raw_len} bytes) exceeds limit of {MAX_REQUEST_BYTES} bytes.",
            )

        # 2. JSON decoding check
        try:
            data = json.loads(raw_body.decode("utf-8"))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Malformed JSON: {str(e)}",
            )

        # 3. Contract validation
        choice_req = ChoiceRequest.from_dict(data, raw_bytes_len=raw_len)

        # 4. Concurrency lock (non-blocking acquire: return 503 if busy)
        lock: asyncio.Lock = app.state.lock
        if lock.locked():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Engine busy processing another request.",
            )

        async with lock:
            engine = app.state.engine
            if engine is None:
                raise HTTPException(status_code=500, detail="Engine unavailable")

            # Run inference in threadpool to avoid blocking event loop
            resp = await asyncio.to_thread(
                engine.predict,
                choice_req,
                temperature=app.state.temperature,
                calibration=app.state.calibration_output,
            )

            # Ensure decision is review locked
            resp_dict = resp.to_dict()
            resp_dict["decision"] = {
                "status": "review",
                "reason": "policy_not_configured",
            }
            return resp_dict

    @app.post("/predict")
    async def predict_endpoint(request: Request):
        return await handle_choice_inference(request)

    @app.post("/v1/choice")
    async def v1_choice_endpoint(request: Request):
        return await handle_choice_inference(request)

    return app
