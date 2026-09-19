"""ONNX Runtime inference engine for ERABI Release Candidate 1.

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

        # Device / provider setup
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = "cuda" if "cuda" in str(device).lower() else "cpu"

        available_providers = ort.get_available_providers()
        if self.device == "cuda" and "CUDAExecutionProvider" in available_providers:
            providers = [
                ("CUDAExecutionProvider", {
                    "device_id": 0,
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
        labels = [c.text for c in request.choices]
        context_text = request.context if request.context is not None else ""

        tokenized_inputs = self.preparer.prepare_inputs(
            [context_text],
            [labels],
            same_labels=False,
            prompt=[request.question],
        )

        input_ids = tokenized_inputs["input_ids"]
        attention_mask = tokenized_inputs["attention_mask"]

        input_tokens = int(input_ids.shape[1])
        if input_tokens > self.max_tokens:
            raise ValidationError(
                "input_too_long",
                f"Total input length ({input_tokens} tokens) exceeds maximum limit of {self.max_tokens} tokens.",
                {"input_tokens": input_tokens, "max_tokens": self.max_tokens},
            )

        ort_inputs = {
            "input_ids": input_ids.cpu().numpy(),
            "attention_mask": attention_mask.cpu().numpy(),
        }

        # Run ONNX inference
        ort_outputs = self.session.run(["logits"], ort_inputs)
        raw_logits_all = ort_outputs[0]  # shape: (1, num_classes)
        # Select first len(labels)
        logits_arr = raw_logits_all[0, : len(labels)].astype(np.float32)
        row_logits = logits_arr.tolist()

        # Check for non-finite logits
        for val in row_logits:
            if not math.isfinite(val):
                raise RuntimeError(f"Model returned non-finite logit: {val}")

        # Argmax over raw logits
        best_idx = int(np.argmax(logits_arr))

        # Softmax with temperature scaling
        probs = compute_softmax(row_logits, temperature=temperature)

        choice_outputs = [
            ChoiceOutput(id=c.id, probability=float(p))
            for c, p in zip(request.choices, probs)
        ]
        best_candidate_id = choice_outputs[best_idx].id

        return ChoiceResponse(
            schema_version="1",
            model_id=f"onnx::{self.onnx_path.name}",
            choices=choice_outputs,
            best_candidate_id=best_candidate_id,
            decision=DecisionOutput(status="review", reason="policy_not_configured"),
            calibration=calibration or CalibrationOutput(status="none", artifact_id=None),
            usage=UsageOutput(input_tokens=input_tokens, truncated=False),
            raw_logits=row_logits if return_logits else None,
        )
