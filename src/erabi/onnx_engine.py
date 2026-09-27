"""ONNX Runtime inference engine for ERABI.

Supports:
- Execution on CUDA (CUDAExecutionProvider) and CPU (CPUExecutionProvider).
- Native FP16 execution on GPU.
- Exact compliance with ERABI schema contracts (ChoiceRequest -> ChoiceResponse).
- Input length validation (max_tokens <= 512, fail-closed without silent truncation).
- Candidate ordering and probability distribution preservation.
- Calibrated temperature scaling applied post-graph to raw float32 logits.
"""

from __future__ import annotations

import logging
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import torch
from erabi.evaluate import compute_softmax
from erabi.schema import (
    ChoiceOutput,
    ChoiceRequest,
    ChoiceResponse,
    DecisionOutput,
    CalibrationOutput,
    UsageOutput,
    ValidationError,
    MAX_TOKENS,
)

logger = logging.getLogger(__name__)

# Ensure CUDA runtime DLLs (from torch/lib if available) are accessible on Windows
if sys.platform == "win32":
    try:
        import torch
        torch_lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        if os.path.exists(torch_lib):
            os.add_dll_directory(torch_lib)
            os.environ["PATH"] = torch_lib + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass


class ERABIONNXEngine:
    """High-performance ONNX Runtime inference engine for ERABI."""

    def __init__(
        self,
        model_dir: str | Path,
        onnx_model_file: str = "model.onnx",
        device: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        model_id: Optional[str] = None,
    ):
        import onnxruntime as ort
        from transformers import AutoTokenizer

        self.model_dir = Path(model_dir)
        p_file = Path(onnx_model_file)
        if p_file.is_absolute() or p_file.exists():
            self.onnx_path = p_file
        else:
            self.onnx_path = self.model_dir / onnx_model_file

        if not self.onnx_path.exists():
            raise FileNotFoundError(f"ONNX model not found: {self.onnx_path}")

        self.max_tokens = max_tokens
        self.model_id = model_id or f"onnx::{self.onnx_path.name}"

        # Device / provider setup
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cuda" if "cuda" in str(device).lower() else "cpu"
        # Measured ONNX kernels are faster one request at a time on the current
        # CPU and CUDA runtimes. Callers can still request a larger explicit batch.
        self.recommended_batch_size = 1

        available_providers = ort.get_available_providers()
        if self.device == "cuda" and "CUDAExecutionProvider" in available_providers:
            device_id = int(str(device).split(":", 1)[1]) if device and ":" in str(device) else 0
            providers = [
                ("CUDAExecutionProvider", {
                    "device_id": device_id,
                    "arena_extend_strategy": "kNextPowerOfTwo",
                    "gpu_mem_limit": 4 * 1024 * 1024 * 1024,  # 4 GB max
                    "cudnn_conv_algo_search": "EXHAUSTIVE",
                    "do_copy_in_default_stream": True,
                }),
                "CPUExecutionProvider",
            ]
        else:
            providers = ["CPUExecutionProvider"]

        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        opts.log_severity_level = 3  # Warning/Error only

        logger.info(f"Loading ONNX model from {self.onnx_path} with providers: {providers}")
        self.session = ort.InferenceSession(str(self.onnx_path), sess_options=opts, providers=providers)
        self.active_providers = self.session.get_providers()
        logger.info(f"Active ONNX Runtime providers: {self.active_providers}")

        # Tokenizer & inner pipeline input preparation
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))
        self._init_input_preparer()

    def _init_input_preparer(self):
        """Initialize input preparer matching the exact GLiClass instruct pipe contract."""
        from gliclass.config import GLiClassModelConfig
        from gliclass.pipeline import UniEncoderZeroShotClassificationPipeline

        config = GLiClassModelConfig.from_pretrained(str(self.model_dir))
        class DummyModel(torch.nn.Module):
            def __init__(self, cfg):
                super().__init__()
                self.config = cfg
                self.device = torch.device("cpu")

        dummy = DummyModel(config)
        self.preparer = UniEncoderZeroShotClassificationPipeline(
            model=dummy,
            tokenizer=self.tokenizer,
            classification_type="single-label",
            device="cpu",
        )

    def predict(
        self,
        request: ChoiceRequest,
        temperature: float = 1.0,
        return_logits: bool = False,
        calibration: Optional[CalibrationOutput] = None,
    ) -> ChoiceResponse:
        """Execute ONNX inference on a single validated ChoiceRequest.

        Guarantees:
          1. Exact same candidate IDs and ordering as request.
          2. Full probability distribution over all candidates summing to 1.0.
          3. Rejection of inputs exceeding max_tokens without silent truncation.
          4. Single Softmax over raw logits without sigmoid renormalization.
          5. Alignment with official GLiClass Task Description Prompt API.
        """
        return self.predict_batch(
            [request],
            temperature=temperature,
            return_logits=return_logits,
            calibration=calibration,
            batch_size=1,
        )[0]

    def predict_batch(
        self,
        requests: List[ChoiceRequest],
        temperature: float = 1.0,
        return_logits: bool = False,
        calibration: Optional[CalibrationOutput] = None,
        batch_size: Optional[int] = None,
    ) -> List[ChoiceResponse]:
        """Infer multiple requests in one or more ONNX Runtime calls."""
        if not requests:
            raise ValidationError("empty_batch", "Batch must contain at least one request.")
        if batch_size is None:
            batch_size = self.recommended_batch_size
        if batch_size < 1:
            raise ValidationError("invalid_batch_size", "batch_size must be at least 1.")

        labels_by_request = [[choice.text for choice in req.choices] for req in requests]
        formatted_inputs = [
            self.preparer.prepare_input(
                req.context if req.context is not None else "",
                labels,
                prompt=req.question,
            )
            for req, labels in zip(requests, labels_by_request)
        ]
        encoded = self.tokenizer(formatted_inputs, truncation=False, padding=False)
        encoded_rows = [
            {key: values[index] for key, values in encoded.items()}
            for index in range(len(requests))
        ]
        input_lengths = [len(row["input_ids"]) for row in encoded_rows]
        for request_index, input_tokens in enumerate(input_lengths):
            if input_tokens > self.max_tokens:
                raise ValidationError(
                    "input_too_long",
                    f"Total input length ({input_tokens} tokens) exceeds maximum limit of {self.max_tokens} tokens.",
                    {
                        "request_index": request_index,
                        "input_tokens": input_tokens,
                        "max_tokens": self.max_tokens,
                    },
                )

        processing_order = sorted(range(len(requests)), key=input_lengths.__getitem__)
        responses: List[Optional[ChoiceResponse]] = [None] * len(requests)
        for start in range(0, len(requests), batch_size):
            request_indices = processing_order[start : start + batch_size]
            chunk = [requests[index] for index in request_indices]
            labels_list = [labels_by_request[index] for index in request_indices]
            tokenized_inputs = self.tokenizer.pad(
                [encoded_rows[index] for index in request_indices],
                padding="longest",
                return_tensors="pt",
            )
            ort_inputs = {
                "input_ids": tokenized_inputs["input_ids"].cpu().numpy(),
                "attention_mask": tokenized_inputs["attention_mask"].cpu().numpy(),
            }
            raw_logits_all = self.session.run(["logits"], ort_inputs)[0]

            for row_index, (request_index, req, labels) in enumerate(
                zip(request_indices, chunk, labels_list)
            ):
                row_logits = (
                    raw_logits_all[row_index, : len(labels)]
                    .astype(np.float32)
                    .tolist()
                )
                responses[request_index] = self._build_response(
                    req,
                    row_logits,
                    input_lengths[request_index],
                    temperature,
                    return_logits,
                    calibration,
                )

        if any(response is None for response in responses):
            raise RuntimeError("Batch inference did not produce every requested response.")
        return [response for response in responses if response is not None]

    def _build_response(
        self,
        request: ChoiceRequest,
        row_logits: List[float],
        input_tokens: int,
        temperature: float,
        return_logits: bool,
        calibration: Optional[CalibrationOutput],
    ) -> ChoiceResponse:
        for value in row_logits:
            if not math.isfinite(value):
                raise RuntimeError(f"Model returned non-finite logit: {value}")

        best_idx = int(np.argmax(np.asarray(row_logits, dtype=np.float32)))
        probabilities = compute_softmax(row_logits, temperature=temperature)
        choice_outputs = [
            ChoiceOutput(id=choice.id, probability=float(probability))
            for choice, probability in zip(request.choices, probabilities)
        ]
        return ChoiceResponse(
            schema_version="1",
            model_id=self.model_id,
            choices=choice_outputs,
            best_candidate_id=choice_outputs[best_idx].id,
            decision=DecisionOutput(status="review", reason="policy_not_configured"),
            calibration=calibration or CalibrationOutput(status="none", artifact_id=None),
            usage=UsageOutput(input_tokens=input_tokens, truncated=False),
            raw_logits=row_logits if return_logits else None,
        )
