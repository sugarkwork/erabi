"""Select and load the requested ERABI inference format."""

from __future__ import annotations

import os
from pathlib import Path

import torch

from erabi.inference import DEFAULT_MODEL_ID, DEFAULT_MODEL_REVISION, GLiClassEngine

MODEL_FORMATS = ("auto", "pytorch", "onnx-fp32", "onnx-fp16")
ONNX_FILES = {
    "onnx-fp32": "onnx/fp32/model.onnx",
    "onnx-fp16": "onnx/fp16/model.onnx",
}
ONNX_SUPPORT_FILES = ("config.json", "tokenizer.json", "tokenizer_config.json")


def select_model_format(model_format: str, device: str | None) -> tuple[str, str]:
    """Choose a usable format without downloading an unusable ONNX variant."""
    if model_format not in MODEL_FORMATS:
        raise ValueError(f"Unknown model format: {model_format}")
    resolved_device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
    if resolved_device != "cpu" and not resolved_device.startswith("cuda"):
        raise ValueError(f"Unsupported device: {resolved_device}")
    is_cuda = resolved_device.startswith("cuda")
    if model_format == "onnx-fp16" and not is_cuda:
        raise ValueError("ONNX FP16 requires CUDA; use onnx-fp32 or pytorch on CPU")
    if model_format == "pytorch":
        return model_format, resolved_device

    try:
        import onnxruntime as ort
    except ImportError:
        if model_format == "auto":
            return "pytorch", resolved_device
        raise RuntimeError("ONNX Runtime is required for ONNX formats; install onnxruntime or onnxruntime-gpu") from None

    providers = ort.get_available_providers()
    if model_format == "auto":
        if is_cuda:
            return ("onnx-fp16" if "CUDAExecutionProvider" in providers else "pytorch"), resolved_device
        return ("onnx-fp32" if "CPUExecutionProvider" in providers else "pytorch"), resolved_device
    if is_cuda and "CUDAExecutionProvider" not in providers:
        raise RuntimeError("CUDAExecutionProvider is unavailable; install a compatible onnxruntime-gpu or use pytorch")
    if not is_cuda and "CPUExecutionProvider" not in providers:
        raise RuntimeError("CPUExecutionProvider is unavailable")
    return model_format, resolved_device


def load_engine(
    model_id: str = DEFAULT_MODEL_ID,
    model_format: str = "auto",
    device: str | None = None,
    revision: str | None = None,
    cache_dir: str | None = None,
):
    """Load only the selected Hub format, or use a local model directory."""
    selected, resolved_device = select_model_format(model_format, device)
    effective_cache = cache_dir if cache_dir is not None else os.environ.get("ERABI_MODEL_CACHE_DIR")
    effective_revision = revision or (DEFAULT_MODEL_REVISION if model_id == DEFAULT_MODEL_ID else None)
    local_dir = Path(model_id)
    if model_format == "auto" and model_id != DEFAULT_MODEL_ID:
        # Custom Hub IDs retain their previous PyTorch behavior. Local ONNX
        # directories can still be discovered without contacting the Hub.
        if not local_dir.is_dir() or not (
            (local_dir / ONNX_FILES.get(selected, "")).is_file()
            or (local_dir / "model.onnx").is_file()
        ):
            selected = "pytorch"
    if selected == "pytorch":
        engine = GLiClassEngine(
            model_id=model_id, device=resolved_device, revision=effective_revision, cache_dir=effective_cache
        )
        engine.model_format = selected
        return engine

    relative_file = ONNX_FILES[selected]
    if local_dir.is_dir():
        model_root = local_dir
        if (model_root / relative_file).is_file():
            if all((model_root / name).is_file() for name in ONNX_SUPPORT_FILES):
                onnx_file = relative_file
            else:
                model_root = model_root / Path(relative_file).parent
                onnx_file = "model.onnx"
        else:
            onnx_file = "model.onnx"
    else:
        from huggingface_hub import snapshot_download

        model_root = Path(snapshot_download(
            repo_id=model_id,
            revision=effective_revision,
            cache_dir=effective_cache,
            allow_patterns=[relative_file, *ONNX_SUPPORT_FILES],
        ))
        onnx_file = relative_file
    if not (model_root / onnx_file).is_file():
        raise FileNotFoundError(f"{selected} is not available for {model_id}: {onnx_file}")

    from erabi.onnx_engine import ERABIONNXEngine

    engine = ERABIONNXEngine(
        model_dir=model_root,
        onnx_model_file=onnx_file,
        device=resolved_device,
        model_id=model_id,
    )
    if resolved_device.startswith("cuda") and "CUDAExecutionProvider" not in engine.active_providers:
        raise RuntimeError("ONNX CUDA provider failed to initialize; no silent CPU fallback")
    engine.model_format = selected
    return engine
