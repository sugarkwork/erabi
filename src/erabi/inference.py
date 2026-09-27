"""GLiClass model adapter and inference engine for ERABI."""

from __future__ import annotations

import logging
import math
import os
import time
from typing import Any, Dict, List, Optional

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

DEFAULT_MODEL_ID = "sugarknight/erabi-practical-v1-experimental"
DEFAULT_MODEL_REVISION = "72ef0212cddae20486009f9e4ce2498c75bb0b0c"


class GLiClassEngine:
    """Wrapper around GLiClass model ensuring strict contracts, full logits, and proper softmax."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: Optional[str] = None,
        revision: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
        cache_dir: Optional[str] = None,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.revision = revision
        self.cache_dir = cache_dir if cache_dir is not None else os.environ.get("ERABI_MODEL_CACHE_DIR")

        if device is None:
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.recommended_batch_size = 16 if str(self.device).startswith("cuda") else 1

        self.model = None
        self.tokenizer = None
        self.pipe = None
        self._load_model()

    def _load_model(self):
        from gliclass import GLiClassModel, ZeroShotClassificationPipeline
        from transformers import AutoTokenizer

        kwargs = {}
        if self.revision:
            kwargs["revision"] = self.revision
        if self.cache_dir:
            kwargs["cache_dir"] = self.cache_dir

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, **kwargs)
        self.model = GLiClassModel.from_pretrained(self.model_id, **kwargs)

        # ZeroShotClassificationPipeline creates the architecture-specific inner pipe (UniEncoder, etc.)
        self.pipe = ZeroShotClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            classification_type="single-label",
            device=self.device,
        )

    def predict(
        self,
        request: ChoiceRequest,
        temperature: float = 1.0,
        return_logits: bool = False,
        calibration: Optional[CalibrationOutput] = None,
    ) -> ChoiceResponse:
        """Execute inference on a single validated ChoiceRequest.

        Guarantees:
          1. Exact same candidate IDs and ordering as request.
          2. Full probability distribution over all candidates summing to 1.0.
          3. Rejection of inputs exceeding max_tokens without silent truncation.
          4. Single Softmax over raw logits without sigmoid renormalization.
          5. Alignment with official GLiClass Task Description Prompt API (question -> prompt, context -> text).
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
        """Infer multiple requests while preserving request and candidate order."""
        if not requests:
            raise ValidationError("empty_batch", "Batch must contain at least one request.")
        if batch_size is None:
            batch_size = self.recommended_batch_size
        if batch_size < 1:
            raise ValidationError("invalid_batch_size", "batch_size must be at least 1.")

        inner_pipe = self.pipe.pipe
        labels_by_request = [[choice.text for choice in req.choices] for req in requests]
        formatted_inputs = [
            inner_pipe.prepare_input(
                req.context if req.context is not None else "",
                labels,
                prompt=req.question,
            )
            for req, labels in zip(requests, labels_by_request)
        ]
        encoded = inner_pipe.tokenizer(
            formatted_inputs,
            truncation=False,
            padding=False,
        )
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

        # Similar lengths share a batch to minimize padding. Responses are restored
        # to caller order below.
        processing_order = sorted(range(len(requests)), key=input_lengths.__getitem__)
        responses: List[Optional[ChoiceResponse]] = [None] * len(requests)
        for start in range(0, len(requests), batch_size):
            request_indices = processing_order[start : start + batch_size]
            chunk = [requests[index] for index in request_indices]
            labels_list = [labels_by_request[index] for index in request_indices]
            tokenized_inputs = inner_pipe.tokenizer.pad(
                [encoded_rows[index] for index in request_indices],
                padding="longest",
                return_tensors="pt",
            ).to(inner_pipe.device)
            max_num_classes = inner_pipe._resolve_max_num_classes(labels_list, same_labels=False)
            with torch.inference_mode():
                outputs = inner_pipe.model(
                    **tokenized_inputs,
                    max_num_classes=max_num_classes,
                )

            for row_index, (request_index, req, labels) in enumerate(
                zip(request_indices, chunk, labels_list)
            ):
                row_logits = (
                    outputs.logits[row_index, : len(labels)]
                    .to(torch.float32)
                    .cpu()
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

        best_idx = max(range(len(row_logits)), key=row_logits.__getitem__)
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
