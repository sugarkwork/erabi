"""GLiClass model adapter and inference engine for ERABI."""

from __future__ import annotations

import logging
import math
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

DEFAULT_MODEL_ID = "knowledgator/gliclass-multilang-mini"


class GLiClassEngine:
    """Wrapper around GLiClass model ensuring strict contracts, full logits, and proper softmax."""

    def __init__(
        self,
        model_id: str = DEFAULT_MODEL_ID,
        device: Optional[str] = None,
        revision: Optional[str] = None,
        max_tokens: int = MAX_TOKENS,
    ):
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.revision = revision

        if device is None:
            self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

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
        # Choice texts are passed as classification labels (choice IDs are strictly excluded)
        labels = [c.text for c in request.choices]

        # Use official GLiClass prompt structure:
        # question is passed as the task description prompt, context as the text
        context_text = request.context if request.context is not None else ""
        inner_pipe = self.pipe.pipe
        tokenized_inputs = inner_pipe.prepare_inputs(
            [context_text],
            [labels],
            same_labels=False,
            prompt=[request.question],
        )

        input_tokens = int(tokenized_inputs["input_ids"].shape[1])
        if input_tokens > self.max_tokens:
            raise ValidationError(
                "input_too_long",
                f"Total input length ({input_tokens} tokens) exceeds maximum limit of {self.max_tokens} tokens.",
                {"input_tokens": input_tokens, "max_tokens": self.max_tokens},
            )

        max_num_classes = inner_pipe._resolve_max_num_classes([labels], same_labels=False)

        with torch.inference_mode():
            outputs = inner_pipe.model(**tokenized_inputs, max_num_classes=max_num_classes)
            # Cast logits to float32 before numpy/tolist conversion to support BFloat16 weights safely
            logits_tensor = outputs.logits[0, : len(labels)].to(torch.float32)
            row_logits = logits_tensor.cpu().tolist()

        # Check for non-finite logits
        for val in row_logits:
            if not math.isfinite(val):
                raise RuntimeError(f"Model returned non-finite logit: {val}")

        # Determine best candidate directly from raw logits (argmax with input order tie-breaking)
        best_idx = 0
        best_logit = row_logits[0]
        for idx, logit_val in enumerate(row_logits):
            if logit_val > best_logit:
                best_logit = logit_val
                best_idx = idx

        # Compute single Softmax over raw candidate logits
        probs = compute_softmax(row_logits, temperature=temperature)

        # Assemble choice outputs in exact original order with unrounded float precision
        choice_outputs = [
            ChoiceOutput(id=c.id, probability=float(p))
            for c, p in zip(request.choices, probs)
        ]
        best_candidate_id = choice_outputs[best_idx].id

        return ChoiceResponse(
            schema_version="1",
            model_id=self.model_id,
            choices=choice_outputs,
            best_candidate_id=best_candidate_id,
            decision=DecisionOutput(status="review", reason="policy_not_configured"),
            calibration=calibration or CalibrationOutput(status="none", artifact_id=None),
            usage=UsageOutput(input_tokens=input_tokens, truncated=False),
            raw_logits=row_logits if return_logits else None,
        )
