"""Model cache routing without loading weights or using the network."""

import sys
from unittest.mock import Mock

import pytest

from erabi import __main__ as cli
from erabi.inference import GLiClassEngine


@pytest.mark.parametrize(
    ("explicit", "environment", "expected"),
    [
        ("explicit-cache", "env-cache", "explicit-cache"),
        (None, "env-cache", "env-cache"),
        (None, None, None),
    ],
)
def test_model_cache_forwarded_to_tokenizer_and_weights(monkeypatch, explicit, environment, expected):
    if environment is None:
        monkeypatch.delenv("ERABI_MODEL_CACHE_DIR", raising=False)
    else:
        monkeypatch.setenv("ERABI_MODEL_CACHE_DIR", environment)

    import gliclass
    import transformers

    tokenizer_loader = Mock(return_value=object())
    model_loader = Mock(return_value=object())
    monkeypatch.setattr(transformers.AutoTokenizer, "from_pretrained", tokenizer_loader)
    monkeypatch.setattr(gliclass.GLiClassModel, "from_pretrained", model_loader)
    monkeypatch.setattr(gliclass, "ZeroShotClassificationPipeline", Mock())

    GLiClassEngine(model_id="owner/model", device="cpu", cache_dir=explicit)

    kwargs = {"cache_dir": expected} if expected else {}
    tokenizer_loader.assert_called_once_with("owner/model", **kwargs)
    model_loader.assert_called_once_with("owner/model", **kwargs)


@pytest.mark.parametrize("command", ["predict", "evaluate"])
def test_cli_accepts_model_cache_dir(monkeypatch, command):
    captured = []
    monkeypatch.setattr(cli, f"run_{command}", lambda args: captured.append(args))
    required = ["--request", "{}"] if command == "predict" else ["--input", "cases.jsonl"]
    monkeypatch.setattr(sys, "argv", ["erabi", command, *required, "--model-cache-dir", "custom-cache"])
    cli.main()
    assert captured[0].model_cache_dir == "custom-cache"
