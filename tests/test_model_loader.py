"""Offline checks for format selection and selective Hub downloads."""

import sys
from types import SimpleNamespace

import huggingface_hub
import pytest

from erabi import model_loader
from erabi import __main__ as cli
from erabi.inference import DEFAULT_MODEL_ID


def set_providers(monkeypatch, providers):
    monkeypatch.setitem(sys.modules, "onnxruntime", SimpleNamespace(get_available_providers=lambda: providers))


def test_auto_selects_format_for_available_device_provider(monkeypatch):
    monkeypatch.setattr(model_loader.torch.cuda, "is_available", lambda: False)
    set_providers(monkeypatch, ["CPUExecutionProvider"])
    assert model_loader.select_model_format("auto", None) == ("onnx-fp32", "cpu")

    monkeypatch.setattr(model_loader.torch.cuda, "is_available", lambda: True)
    set_providers(monkeypatch, ["CUDAExecutionProvider", "CPUExecutionProvider"])
    assert model_loader.select_model_format("auto", None) == ("onnx-fp16", "cuda:0")


def test_auto_falls_back_to_pytorch_without_cuda_provider(monkeypatch):
    set_providers(monkeypatch, ["CPUExecutionProvider"])
    assert model_loader.select_model_format("auto", "cuda:0") == ("pytorch", "cuda:0")
    with pytest.raises(RuntimeError, match="CUDAExecutionProvider"):
        model_loader.select_model_format("onnx-fp16", "cuda:0")
    with pytest.raises(ValueError, match="requires CUDA"):
        model_loader.select_model_format("onnx-fp16", "cpu")


def test_selected_onnx_downloads_only_its_variant(monkeypatch, tmp_path):
    set_providers(monkeypatch, ["CPUExecutionProvider"])
    selected_file = tmp_path / "onnx" / "fp32" / "model.onnx"
    selected_file.parent.mkdir(parents=True)
    selected_file.touch()
    captured = {}

    def fake_download(**kwargs):
        captured.update(kwargs)
        return str(tmp_path)

    def fake_engine(**kwargs):
        captured["engine"] = kwargs
        return SimpleNamespace(active_providers=["CPUExecutionProvider"])

    monkeypatch.setattr(huggingface_hub, "snapshot_download", fake_download)
    monkeypatch.setattr("erabi.onnx_engine.ERABIONNXEngine", fake_engine)
    engine = model_loader.load_engine(
        model_id=DEFAULT_MODEL_ID, model_format="onnx-fp32", device="cpu", cache_dir="custom-cache"
    )
    assert captured["allow_patterns"] == ["onnx/fp32/model.onnx", *model_loader.ONNX_SUPPORT_FILES]
    assert captured["cache_dir"] == "custom-cache"
    assert captured["revision"] == model_loader.DEFAULT_MODEL_REVISION
    assert captured["engine"]["onnx_model_file"] == "onnx/fp32/model.onnx"
    assert engine.model_format == "onnx-fp32"


def test_custom_local_checkpoint_keeps_pytorch_default(monkeypatch, tmp_path):
    captured = {}

    def fake_torch_engine(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace()

    set_providers(monkeypatch, ["CPUExecutionProvider"])
    monkeypatch.setattr(model_loader, "GLiClassEngine", fake_torch_engine)
    engine = model_loader.load_engine(model_id=str(tmp_path), device="cpu")
    assert captured["model_id"] == str(tmp_path)
    assert engine.model_format == "pytorch"


def test_local_variant_directory_uses_its_own_tokenizer(monkeypatch, tmp_path):
    set_providers(monkeypatch, ["CPUExecutionProvider"])
    variant = tmp_path / "onnx" / "fp32"
    variant.mkdir(parents=True)
    (variant / "model.onnx").touch()
    captured = {}

    def fake_engine(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(active_providers=["CPUExecutionProvider"])

    monkeypatch.setattr("erabi.onnx_engine.ERABIONNXEngine", fake_engine)
    engine = model_loader.load_engine(model_id=str(tmp_path), device="cpu")
    assert captured["model_dir"] == variant
    assert captured["onnx_model_file"] == "model.onnx"
    assert engine.model_format == "onnx-fp32"


def test_cli_model_format_flag_overrides_environment(monkeypatch):
    captured = []
    monkeypatch.setenv("ERABI_MODEL_FORMAT", "pytorch")
    monkeypatch.setattr(cli, "run_predict", lambda args: captured.append(args))
    monkeypatch.setattr(sys, "argv", ["erabi", "predict", "--request", "{}", "--model-format", "onnx-fp32"])
    cli.main()
    assert captured[0].model_format == "onnx-fp32"
