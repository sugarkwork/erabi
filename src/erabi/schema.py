"""ERABI schema definitions and input validation."""

from __future__ import annotations

import hashlib
import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Constants
SCHEMA_VERSION = "1"
FORMATTER_VERSION = "m1_instruct_pipe_v1"
MAX_REQUEST_BYTES = 65536
MAX_TOKENS = 512
MIN_CHOICES = 2
MAX_CHOICES = 16
CHOICE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")
RESERVED_TOKENS = ["<<LABEL>>", "<<EXAMPLE>>", "<<SEP>>"]

ALLOWED_CALIBRATION_STATUSES = frozenset({"none", "applied"})
RUNTIME_PRECISION_CONTRACT = "float32_forward_float64_nll"


def compute_file_sha256(filepath: str | Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA256 hex digest of a file in chunks to avoid high memory usage."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


class ValidationError(ValueError):
    """Raised when request validation fails."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class ChoiceInput:
    id: str
    text: str

    def __post_init__(self):
        if not self.id or not isinstance(self.id, str):
            raise ValidationError("invalid_choice_id", "Choice id must be a non-empty string.")
        if not CHOICE_ID_PATTERN.match(self.id):
            raise ValidationError(
                "invalid_choice_id",
                f"Choice id '{self.id}' is invalid. Must be 1-64 characters of ASCII letters, digits, '_' or '-'.",
            )
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValidationError("empty_choice_text", f"Choice text for id '{self.id}' must not be empty or blank.")


@dataclass(frozen=True)
class ChoiceOutput:
    id: str
    probability: float


@dataclass(frozen=True)
class DecisionOutput:
    status: str = "review"
    reason: str = "policy_not_configured"


@dataclass(frozen=True)
class CalibrationOutput:
    status: str = "none"
    artifact_id: Optional[str] = None


@dataclass(frozen=True)
class UsageOutput:
    input_tokens: int
    truncated: bool = False


@dataclass
class ChoiceRequest:
    context: str
    question: str
    choices: List[ChoiceInput]
    schema_version: str = "1"

    @classmethod
    def from_dict(cls, data: Dict[str, Any], raw_bytes_len: Optional[int] = None) -> ChoiceRequest:
        if raw_bytes_len is not None and raw_bytes_len > MAX_REQUEST_BYTES:
            raise ValidationError(
                "request_too_large",
                f"Request byte size ({raw_bytes_len}) exceeds maximum limit ({MAX_REQUEST_BYTES} bytes).",
                {"bytes": raw_bytes_len, "max_bytes": MAX_REQUEST_BYTES},
            )

        if not isinstance(data, dict):
            raise ValidationError("invalid_request", "Request body must be a JSON object.")

        context = data.get("context", "")
        if not isinstance(context, str):
            raise ValidationError("invalid_context", "'context' must be a string.")

        question = data.get("question", "")
        if not isinstance(question, str) or not question.strip():
            raise ValidationError("empty_question", "'question' must be a non-empty string.")

        raw_choices = data.get("choices")
        if not isinstance(raw_choices, list):
            raise ValidationError("invalid_choices", "'choices' must be a list.")

        if len(raw_choices) < MIN_CHOICES or len(raw_choices) > MAX_CHOICES:
            raise ValidationError(
                "invalid_choice_count",
                f"Number of choices ({len(raw_choices)}) must be between {MIN_CHOICES} and {MAX_CHOICES}.",
                {"count": len(raw_choices), "min": MIN_CHOICES, "max": MAX_CHOICES},
            )

        choices: List[ChoiceInput] = []
        seen_ids = set()
        seen_normalized_texts = set()

        for idx, c in enumerate(raw_choices):
            if not isinstance(c, dict):
                raise ValidationError("invalid_choice", f"Choice at index {idx} must be an object.")
            cid = c.get("id")
            ctext = c.get("text")
            choice = ChoiceInput(id=str(cid) if cid is not None else "", text=str(ctext) if ctext is not None else "")

            if choice.id in seen_ids:
                raise ValidationError(
                    "duplicate_choice_id",
                    f"Duplicate choice id '{choice.id}' detected at index {idx}.",
                    {"duplicate_id": choice.id, "index": idx},
                )
            seen_ids.add(choice.id)

            normalized_text = unicodedata.normalize("NFC", choice.text).strip()
            if normalized_text in seen_normalized_texts:
                raise ValidationError(
                    "duplicate_choice_text",
                    f"Duplicate or near-duplicate choice text detected for id '{choice.id}'.",
                    {"id": choice.id, "text": choice.text},
                )
            seen_normalized_texts.add(normalized_text)

            choices.append(choice)

        # Check for reserved tokens in context, question, choices
        all_texts = [context, question] + [c.text for c in choices]
        for text in all_texts:
            for token in RESERVED_TOKENS:
                if token in text:
                    raise ValidationError(
                        "reserved_token_in_input",
                        f"Input text contains reserved internal marker '{token}'.",
                        {"reserved_token": token},
                    )

        schema_version = str(data.get("schema_version", "1"))
        return cls(context=context, question=question, choices=choices, schema_version=schema_version)


@dataclass
class ChoiceResponse:
    choices: List[ChoiceOutput]
    best_candidate_id: str
    usage: UsageOutput
    decision: DecisionOutput = field(default_factory=DecisionOutput)
    calibration: CalibrationOutput = field(default_factory=CalibrationOutput)
    model_id: str = "knowledgator/gliclass-multilang-mini"
    schema_version: str = "1"
    raw_logits: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "schema_version": self.schema_version,
            "model_id": self.model_id,
            "choices": [{"id": c.id, "probability": c.probability} for c in self.choices],
            "best_candidate_id": self.best_candidate_id,
            "decision": {
                "status": self.decision.status,
                "reason": self.decision.reason,
            },
            "calibration": {
                "status": self.calibration.status,
                "artifact_id": self.calibration.artifact_id,
            },
            "usage": {
                "input_tokens": self.usage.input_tokens,
                "truncated": self.usage.truncated,
            },
        }
        if self.raw_logits is not None:
            res["raw_logits"] = self.raw_logits
        return res
