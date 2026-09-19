"""Unit tests for M3.7 calibration handoff responsibilities (CPU only, offline).

Tests:
1. Artifact roundtrip: build_calibration_artifact -> load_and_verify_calibration -> create_app(API).
2. Rejection of misapplications: non-existent checkpoint, unknown status, hash mismatch, contract mismatch.
3. Cache manifest binding: load_logits_with_manifest rejects modified data, modified model, or modified contract.
4. Semantic state roundtrip: generate_goal_following_scenario context -> parse_gf_semantic_state invariance.
"""

import json
import os
import random
import re
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from erabi.__main__ import load_and_verify_calibration
from erabi.api import create_app
from erabi.cache import (
    get_checkpoint_hashes,
    load_logits_with_manifest,
    save_logits_with_manifest,
)
from erabi.calibrate import build_calibration_artifact
from erabi.schema import (
    ChoiceOutput,
    ChoiceRequest,
    ChoiceResponse,
    CalibrationOutput,
    DecisionOutput,
    FORMATTER_VERSION,
    MAX_TOKENS,
    SCHEMA_VERSION,
    UsageOutput,
    compute_file_sha256,
)
from scripts.audit_semantic_states import parse_gf_semantic_state
from scripts.build_m3_6_data import generate_goal_following_scenario


class FakeEngine:
    def __init__(self, model_id: str = "fake-model"):
        self.model_id = model_id

    def predict(
        self,
        req: ChoiceRequest,
        temperature: float = 1.0,
        return_logits: bool = False,
        calibration=None,
    ) -> ChoiceResponse:
        n = len(req.choices)
        prob = round(1.0 / n, 6)
        choice_outputs = [ChoiceOutput(id=c.id, probability=prob) for c in req.choices]
        return ChoiceResponse(
            schema_version="1",
            model_id=self.model_id,
            choices=choice_outputs,
            best_candidate_id=req.choices[0].id,
            decision=DecisionOutput(status="review", reason="policy_not_configured"),
            calibration=calibration or CalibrationOutput(status="none", artifact_id=None),
            usage=UsageOutput(input_tokens=42, truncated=False),
        )


@pytest.fixture
def dummy_checkpoint(tmp_path):
    """Create a temporary dummy checkpoint directory with required files."""
    cp_dir = tmp_path / "dummy_checkpoint"
    cp_dir.mkdir()
    (cp_dir / "model.safetensors").write_bytes(b"dummy safetensors weight bytes 12345")
    (cp_dir / "config.json").write_text('{"architectures": ["GLiClassModel"]}', encoding="utf-8")
    (cp_dir / "tokenizer.json").write_text('{"vocab": {}}', encoding="utf-8")
    (cp_dir / "tokenizer_config.json").write_text('{}', encoding="utf-8")
    return cp_dir


@pytest.fixture
def dummy_dataset(tmp_path):
    """Create a temporary dummy dataset."""
    d_path = tmp_path / "dummy_data.jsonl"
    d_path.write_text('{"id": "c1", "context": "ctx", "question": "q", "choices": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}], "target": {"choice_id": "a"}}\n', encoding="utf-8")
    return d_path


def test_artifact_roundtrip_and_api(dummy_checkpoint, dummy_dataset, tmp_path):
    """Verify programmatic creation of calibration artifact, loader verification, and API integration."""
    artifact = build_calibration_artifact(
        temperature=2.7182,
        status="applied",
        checkpoint_dir=str(dummy_checkpoint),
        dataset_path=str(dummy_dataset),
        dataset_cases=1,
        dataset_description="Test calibration dataset",
        adoption_decision="ACCEPT_SCOPED",
        adoption_reason="Test improvement",
        scope="test_scope",
        artifact_id="test-calib-001",
    )
    art_path = tmp_path / "calibration.json"
    with open(art_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f)

    # 1. Loader verification
    temp, cal_out, cal_data = load_and_verify_calibration(str(art_path), str(dummy_checkpoint))
    assert temp == 2.7182
    assert cal_out.status == "applied"
    assert cal_out.artifact_id == "test-calib-001"
    assert cal_data["adoption"]["decision"] == "ACCEPT_SCOPED"

    # 2. API integration with require_calibration=True
    app = create_app(
        model_id=str(dummy_checkpoint),
        calibration_path=str(art_path),
        require_calibration=True,
        engine_factory=lambda: FakeEngine(str(dummy_checkpoint)),
    )
    with TestClient(app) as client:
        # Check /health
        resp = client.get("/health")
        assert resp.status_code == 200
        health_data = resp.json()
        assert health_data["temperature"] == 2.7182
        assert health_data["calibration"]["status"] == "applied"
        assert health_data["calibration"]["artifact_id"] == "test-calib-001"
        assert health_data["decision_policy"] == "review_default"

        # Check inference response retains review decision
        pred_resp = client.post(
            "/predict",
            json={
                "context": "Context text",
                "question": "Question text",
                "choices": [{"id": "c1", "text": "A"}, {"id": "c2", "text": "B"}],
            },
        )
        assert pred_resp.status_code == 200
        pred_data = pred_resp.json()
        assert pred_data["decision"]["status"] == "review"
        assert pred_data["calibration"]["status"] == "applied"
        assert pred_data["calibration"]["artifact_id"] == "test-calib-001"


def test_rejection_of_misapplications(dummy_checkpoint, dummy_dataset, tmp_path):
    """Verify loader and API strictly reject non-existent checkpoints, invalid status, or contract mismatches."""
    # 1. Non-existent checkpoint path
    art_path = tmp_path / "valid_art.json"
    art = build_calibration_artifact(
        temperature=2.5,
        status="applied",
        checkpoint_dir=str(dummy_checkpoint),
        dataset_path=str(dummy_dataset),
        dataset_cases=1,
    )
    art_path.write_text(json.dumps(art), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="does not exist or is not a directory"):
        load_and_verify_calibration(str(art_path), "non/existent/checkpoint/path")

    # 2. Unknown status (applied_scoped should be rejected by runtime loader)
    bad_status_art = dict(art)
    bad_status_art["status"] = "applied_scoped"
    bad_status_path = tmp_path / "bad_status.json"
    bad_status_path.write_text(json.dumps(bad_status_art), encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid calibration status 'applied_scoped'"):
        load_and_verify_calibration(str(bad_status_path), str(dummy_checkpoint))

    # 3. Model file hash mismatch
    bad_hash_art = dict(art)
    bad_hash_art["target_model"] = {
        "files": {
            "model.safetensors": "0000000000000000000000000000000000000000000000000000000000000000",
            "config.json": compute_file_sha256(str(dummy_checkpoint / "config.json")),
            "tokenizer.json": compute_file_sha256(str(dummy_checkpoint / "tokenizer.json")),
            "tokenizer_config.json": compute_file_sha256(str(dummy_checkpoint / "tokenizer_config.json")),
        }
    }
    bad_hash_path = tmp_path / "bad_hash.json"
    bad_hash_path.write_text(json.dumps(bad_hash_art), encoding="utf-8")

    with pytest.raises(ValueError, match="Calibration hash mismatch for 'model.safetensors'"):
        load_and_verify_calibration(str(bad_hash_path), str(dummy_checkpoint))

    # 4. Missing required model file (e.g. tokenizer.json omitted)
    missing_file_art = dict(art)
    missing_file_art["target_model"] = {
        "files": {
            "model.safetensors": compute_file_sha256(str(dummy_checkpoint / "model.safetensors")),
            "config.json": compute_file_sha256(str(dummy_checkpoint / "config.json")),
            "tokenizer_config.json": compute_file_sha256(str(dummy_checkpoint / "tokenizer_config.json")),
        }
    }
    missing_file_path = tmp_path / "missing_file.json"
    missing_file_path.write_text(json.dumps(missing_file_art), encoding="utf-8")

    with pytest.raises(ValueError, match="Required model file 'tokenizer.json' missing"):
        load_and_verify_calibration(str(missing_file_path), str(dummy_checkpoint))

    # 5. Contract mismatches (schema, max_tokens, formatter, precision)
    for key, val, err in [
        ("schema_version", "999", "schema mismatch"),
        ("max_tokens", 1024, "max_tokens mismatch"),
        ("formatter_version", "unknown_formatter", "formatter_version mismatch"),
        ("precision", "different_precision_mode", "precision mismatch"),
    ]:
        bad_contract_art = dict(art)
        bad_contract_art["contract"] = dict(art["contract"])
        bad_contract_art["contract"][key] = val
        bad_contract_path = tmp_path / f"bad_{key}.json"
        bad_contract_path.write_text(json.dumps(bad_contract_art), encoding="utf-8")

        with pytest.raises(ValueError, match=err):
            load_and_verify_calibration(str(bad_contract_path), str(dummy_checkpoint))


def test_cache_manifest_binding(dummy_checkpoint, dummy_dataset, tmp_path):
    """Verify sidecar manifest binds logits to model, dataset, alignment, and contracts."""
    raw_logits_data = [
        {"id": "c1", "choices": [{"id": "a"}, {"id": "b"}], "target": "a", "target_index": 0, "raw_logits": [1.5, -0.5]}
    ]
    logits_path = tmp_path / "raw_logits.jsonl"
    manifest_path = save_logits_with_manifest(
        logits_path=logits_path,
        raw_records=raw_logits_data,
        model_dir=dummy_checkpoint,
        data_path=dummy_dataset,
        formatter_version=FORMATTER_VERSION,
    )
    assert manifest_path.exists()

    # 1. Normal load succeeds
    loaded = load_logits_with_manifest(
        logits_path=logits_path,
        model_dir=dummy_checkpoint,
        data_path=dummy_dataset,
        formatter_version=FORMATTER_VERSION,
    )
    assert len(loaded) == 1
    assert loaded[0]["id"] == "c1"

    # 2. Reject save if alignment mismatches (e.g. wrong choice order or target)
    mismatched_records = [
        {"id": "c1", "choices": [{"id": "b"}, {"id": "a"}], "target": "b", "target_index": 0, "raw_logits": [1.5, -0.5]}
    ]
    with pytest.raises(ValueError, match="Dataset alignment mismatch"):
        save_logits_with_manifest(
            logits_path=tmp_path / "bad_logits.jsonl",
            raw_records=mismatched_records,
            model_dir=dummy_checkpoint,
            data_path=dummy_dataset,
        )

    # 3. Reject if dataset modified
    other_dataset = tmp_path / "other_data.jsonl"
    other_dataset.write_text('{"id": "modified", "choices": [{"id": "a"}], "target": {"choice_id": "a"}}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="Dataset SHA256 mismatch"):
        load_logits_with_manifest(
            logits_path=logits_path,
            model_dir=dummy_checkpoint,
            data_path=other_dataset,
        )

    # 4. Reject if checkpoint modified
    (dummy_checkpoint / "model.safetensors").write_bytes(b"tampered weight content")
    with pytest.raises(ValueError, match="Model file hash mismatch for 'model.safetensors'"):
        load_logits_with_manifest(
            logits_path=logits_path,
            model_dir=dummy_checkpoint,
            data_path=dummy_dataset,
        )


def test_semantic_state_roundtrip():
    """Verify GF canonical state parsing has roundtrip consistency and candidate order invariance."""
    rng = random.Random(42)
    for trial in range(10):
        pair, expected_state = generate_goal_following_scenario(f"trial-{trial}", trial % 6, rng)
        ctx = pair[0]["context"]

        # Parse from context
        extracted = parse_gf_semantic_state(ctx)
        assert extracted == expected_state, f"Failed roundtrip for trial {trial}: {extracted} != {expected_state}"

        # Test candidate order invariance in context
        # Swap lines in context text
        lines = ctx.splitlines()
        header = lines[0]
        c_lines = lines[1:]
        shuffled_c_lines = list(reversed(c_lines))
        permuted_ctx = "\n".join([header] + shuffled_c_lines)

        permuted_extracted = parse_gf_semantic_state(permuted_ctx)
        assert permuted_extracted == expected_state, "Order permutation in context altered canonical semantic state!"
