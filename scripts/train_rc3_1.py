"""RC3.1 Run 1 continual-training driver.

The module keeps dataset preparation, gate logic, and checkpoint selection
pure enough to test without loading a model.  Actual training/evaluation is
lazy-imported and requires an explicitly available CUDA device.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import sys
from collections import Counter, OrderedDict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

BASE_MODEL_DIR = ROOT / "release" / "rc3" / "model"
BASE_MODEL_FILE = BASE_MODEL_DIR / "model.safetensors"
EXPECTED_BASE_MODEL_SHA256 = "2ad53a3317244003938d0417aa4572dde5a1e413f5e7272c318bda539108a0c1"
OLD_REPLAY_FILE = ROOT / "data" / "rc3_train" / "train.jsonl"
NEW_TRAIN_FILE = ROOT / "data" / "rc3_1_train" / "train.jsonl"
LOGIC_BRIDGE_FILE = ROOT / "data" / "rc3_1_logic_bridge" / "benchmark.jsonl"
RC3_BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"
RUN1_DIR = ROOT / "runs" / "rc3_1_run1"
BASELINE_DIR = ROOT / "runs" / "rc3_1_baseline"

RETENTION_SUITES: Mapping[str, Path] = {
    "eval_v2": ROOT / "data" / "m3_3_v2" / "eval_v2.jsonl",
    "eval_exception": ROOT / "data" / "m4_1_exception" / "eval_exception.jsonl",
    "fresh_operator": ROOT / "data" / "m6_operator" / "fresh_operator_eval.jsonl",
    "fresh_robustness": ROOT / "data" / "m7_robustness" / "fresh_robustness_eval.jsonl",
    "fresh_general": ROOT / "data" / "m8_general_choice" / "fresh_general_eval.jsonl",
}

DEFAULT_CONFIG: Mapping[str, Any] = {
    "epochs": 2,
    "lr": 1.0e-6,
    "micro_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "weight_decay": 0.01,
    "warmup_steps": 50,
    "cosine_floor": 2.0e-7,
    "seed": 3101,
    "amp": "fp16",
    "scheduler": "warmup+cosine",
}

LOGIC_GATE: Mapping[str, float] = {
    "overall": 0.90,
    "xor": 0.85,
    "nand": 0.85,
    "nor": 0.85,
    "negation": 0.90,
    "nested": 0.85,
    "paired_both": 0.85,
}
RC3_GATE: Mapping[str, float] = {
    "overall": 0.88,
    "logical_operators": 0.90,
    "general_choice": 0.85,
    "priority_exception": 0.85,
    "variable_choice": 0.85,
    "perturbation_invariance": 0.85,
    "natural_japanese": 0.90,
    "permutation": 0.95,
}
RETENTION_GATE = 0.96
NESTED_OPERATORS = {
    "nested_and_or",
    "nested_a_and_or",
    "nested_not_and",
    "nested_not_or",
    "nested_xor_and",
}
# The negation gate covers standalone negation plus the two explicit
# clause-level negation forms.  Keeping these names here makes the gate match
# the generated bridge operator contract rather than silently evaluating only
# the three short forms.
NEGATION_OPERATORS = {
    "not",
    "double_negation",
    "polarity_reversal",
    "and_not_b",
    "not_a_or_b",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_base_model(base_dir: Path = BASE_MODEL_DIR) -> Dict[str, Any]:
    model_file = base_dir / "model.safetensors"
    if not model_file.is_file():
        raise FileNotFoundError(f"Base model file is missing: {model_file}")
    actual = sha256_file(model_file)
    if actual.lower() != EXPECTED_BASE_MODEL_SHA256.lower():
        raise ValueError(
            f"Base model hash mismatch: expected {EXPECTED_BASE_MODEL_SHA256}, got {actual}"
        )
    return {"path": str(base_dir), "model_file": str(model_file), "sha256": actual}


def _group_signature(group: Sequence[Mapping[str, Any]]) -> Tuple[Any, ...]:
    """Signature of model-visible pair payload, excluding IDs/group IDs."""
    return tuple(
        (
            str(record.get("context", "")),
            str(record.get("question", "")),
            tuple(
                (str(choice.get("id", "")), str(choice.get("text", "")))
                for choice in record.get("choices", [])
            ),
            str(record.get("target", {}).get("choice_id", "")),
        )
        for record in group
    )


def group_records(records: Sequence[Mapping[str, Any]]) -> "OrderedDict[str, List[Dict[str, Any]]]":
    groups: "OrderedDict[str, List[Dict[str, Any]]]" = OrderedDict()
    for record in records:
        group_id = str(record.get("group_id", ""))
        if not group_id:
            raise ValueError("Every replay/training record must have a group_id")
        groups.setdefault(group_id, []).append(dict(record))
    return groups


def deduplicate_group_replay(records: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Keep one complete pair for each repeated group payload."""
    groups = group_records(records)
    seen: set[Tuple[Any, ...]] = set()
    result: List[Dict[str, Any]] = []
    for group_id, group in groups.items():
        if len(group) != 2:
            raise ValueError(f"Replay group {group_id} has {len(group)} records; expected 2")
        signature = _group_signature(group)
        if signature in seen:
            continue
        seen.add(signature)
        result.extend(copy.deepcopy(group))
    return result


def prepare_mixture(
    old_replay_file: Path = OLD_REPLAY_FILE,
    new_train_file: Path = NEW_TRAIN_FILE,
) -> Dict[str, Any]:
    old_records = load_jsonl(old_replay_file)
    replay_records = deduplicate_group_replay(old_records)
    new_records = load_jsonl(new_train_file)
    if len(replay_records) != 2766 or len({r["group_id"] for r in replay_records}) != 1383:
        raise ValueError(
            "Old replay deduplication contract failed: "
            f"got {len({r['group_id'] for r in replay_records})} groups / {len(replay_records)} records"
        )
    if len(new_records) != 1920:
        raise ValueError(f"RC3.1 train contract failed: expected 1920 records, got {len(new_records)}")
    old_groups = {str(r["group_id"]) for r in replay_records}
    new_groups = {str(r["group_id"]) for r in new_records}
    if any(len(group) != 2 for group in group_records(new_records).values()):
        raise ValueError("RC3.1 train contract failed: every group must contain exactly two records")
    if old_groups & new_groups:
        raise ValueError("Old replay and RC3.1 train group IDs overlap")
    mixed = replay_records + new_records
    return {
        "old_source_records": old_records,
        "old_replay_records": replay_records,
        "new_train_records": new_records,
        "mixed_records": mixed,
        "old_source_count": len(old_records),
        "old_source_groups": len(group_records(old_records)),
        "old_replay_count": len(replay_records),
        "old_replay_groups": len(old_groups),
        "new_train_count": len(new_records),
        "new_train_groups": len(new_groups),
        "mixed_count": len(mixed),
        "mixed_groups": len(old_groups | new_groups),
    }


def shuffle_groups(records: Sequence[Mapping[str, Any]], seed: int) -> List[Dict[str, Any]]:
    groups = [copy.deepcopy(group) for group in group_records(records).values()]
    random.Random(seed).shuffle(groups)
    return [record for group in groups for record in group]


def shuffle_choices(record: Mapping[str, Any], rng: random.Random) -> Dict[str, Any]:
    result = copy.deepcopy(dict(record))
    choices = list(result.get("choices", []))
    rng.shuffle(choices)
    result["choices"] = choices
    return result


def _stats(total: int, correct: int, nll: float) -> Dict[str, Any]:
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 6) if total else 0.0,
        "mean_nll": round(nll / total, 6) if total else 0.0,
    }


def _aggregate_stats(by_operator: Mapping[str, Mapping[str, Any]], names: Iterable[str]) -> Dict[str, Any]:
    selected = [by_operator[name] for name in names if name in by_operator]
    return _stats(
        sum(int(item["total"]) for item in selected),
        sum(int(item["correct"]) for item in selected),
        sum(float(item.get("mean_nll", 0.0)) * int(item["total"]) for item in selected),
    )


def evaluate_records(
    engine: Any,
    records: Sequence[Mapping[str, Any]],
    test_permutation: bool = False,
    seed: int = 42,
) -> Dict[str, Any]:
    """Evaluate records with the same request/prediction contract as inference."""
    from erabi.schema import ChoiceRequest

    rng = random.Random(seed)
    correct = 0
    total_nll = 0.0
    permuted_matches = 0
    by_family: Dict[str, Dict[str, Any]] = {}
    by_operator: Dict[str, Dict[str, Any]] = {}
    groups: Dict[str, List[bool]] = {}

    for record in records:
        request = ChoiceRequest.from_dict(dict(record))
        target_id = str(record["target"]["choice_id"])
        target_index = next(index for index, choice in enumerate(request.choices) if choice.id == target_id)
        response = engine.predict(request, temperature=1.0, return_logits=True)
        predicted_id = str(response.best_candidate_id)
        is_correct = predicted_id == target_id
        correct += int(is_correct)
        probabilities = [float(choice.probability) for choice in response.choices]
        target_probability = max(probabilities[target_index], 1.0e-15)
        nll = -math.log(target_probability)
        total_nll += nll

        family = str(record.get("family", "unknown"))
        operator = str(record.get("operator_family", record.get("subcategory", "unknown")))
        for bucket, key in ((by_family, family), (by_operator, operator)):
            if key not in bucket:
                bucket[key] = {"total": 0, "correct": 0, "nll": 0.0}
            bucket[key]["total"] += 1
            bucket[key]["correct"] += int(is_correct)
            bucket[key]["nll"] += nll

        group_id = str(record.get("group_id", record.get("id", "")))
        groups.setdefault(group_id, []).append(is_correct)

        if test_permutation:
            permuted = copy.deepcopy(dict(record))
            permuted_choices = list(permuted["choices"])
            rng.shuffle(permuted_choices)
            permuted["choices"] = permuted_choices
            permutation_response = engine.predict(
                ChoiceRequest.from_dict(permuted), temperature=1.0, return_logits=False
            )
            permuted_matches += int(str(permutation_response.best_candidate_id) == predicted_id)

    def finalize(bucket: Mapping[str, Mapping[str, Any]]) -> Dict[str, Dict[str, Any]]:
        return {
            key: _stats(int(value["total"]), int(value["correct"]), float(value["nll"]))
            for key, value in sorted(bucket.items())
        }

    paired_total = sum(len(values) == 2 for values in groups.values())
    paired_both = sum(len(values) == 2 and all(values) for values in groups.values())
    return {
        "total_cases": len(records),
        "correct": correct,
        "accuracy": round(correct / len(records), 6) if records else 0.0,
        "mean_nll": round(total_nll / len(records), 6) if records else 0.0,
        "paired_total": paired_total,
        "paired_both": paired_both,
        "paired_both_rate": round(paired_both / paired_total, 6) if paired_total else 0.0,
        "permutation_consistency": round(permuted_matches / len(records), 6) if test_permutation and records else None,
        "by_family": finalize(by_family),
        "by_operator": finalize(by_operator),
    }


def evaluate_logic_bridge(engine: Any, records: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    result = evaluate_records(engine, records)
    result["nested"] = _aggregate_stats(result["by_operator"], NESTED_OPERATORS)
    result["negation"] = _aggregate_stats(result["by_operator"], NEGATION_OPERATORS)
    return result


def evaluate_existing_bridge(
    engine: Any,
    records: Sequence[Mapping[str, Any]],
    test_permutation: bool = False,
) -> Dict[str, Any]:
    return evaluate_records(engine, records, test_permutation=test_permutation)


def evaluate_retention(engine: Any, suites: Mapping[str, Sequence[Mapping[str, Any]]]) -> Dict[str, Any]:
    per_suite = {name: evaluate_records(engine, records) for name, records in suites.items()}
    mean_accuracy = sum(float(result["accuracy"]) for result in per_suite.values()) / max(1, len(per_suite))
    return {
        "suites": per_suite,
        "mean_accuracy": round(mean_accuracy, 6),
        "gate": mean_accuracy >= RETENTION_GATE,
    }


def logic_gate_passed(metrics: Mapping[str, Any]) -> bool:
    operators = metrics.get("by_operator", {})
    return (
        float(metrics.get("accuracy", 0.0)) >= LOGIC_GATE["overall"]
        and all(float(operators.get(name, {}).get("accuracy", 0.0)) >= LOGIC_GATE[name] for name in ("xor", "nand", "nor"))
        and float(metrics.get("negation", {}).get("accuracy", 0.0)) >= LOGIC_GATE["negation"]
        and float(metrics.get("nested", {}).get("accuracy", 0.0)) >= LOGIC_GATE["nested"]
        and float(metrics.get("paired_both_rate", 0.0)) >= LOGIC_GATE["paired_both"]
    )


def rc3_gate_passed(metrics: Mapping[str, Any], require_permutation: bool = True) -> bool:
    families = metrics.get("by_family", {})
    required = ("logical_operators", "general_choice", "priority_exception", "variable_choice", "perturbation_invariance", "natural_japanese")
    family_gate = all(
        float(families.get(name, {}).get("accuracy", 0.0)) >= RC3_GATE[name]
        for name in required
    )
    permutation_gate = (
        float(metrics.get("permutation_consistency", 0.0)) >= RC3_GATE["permutation"]
        if require_permutation
        else True
    )
    return float(metrics.get("accuracy", 0.0)) >= RC3_GATE["overall"] and family_gate and permutation_gate


def retention_gate_passed(metrics: Mapping[str, Any]) -> bool:
    return float(metrics.get("mean_accuracy", 0.0)) >= RETENTION_GATE


def selection_key(epoch_result: Mapping[str, Any]) -> Tuple[float, float, float, float]:
    logic = epoch_result["logic_bridge"]
    rc3 = epoch_result["existing_rc3_bridge"]
    return (
        float(logic.get("accuracy", 0.0)),
        float(rc3.get("accuracy", 0.0)),
        float(rc3.get("paired_both_rate", 0.0)),
        -float(logic.get("mean_nll", math.inf)),
    )


def select_checkpoint_epoch(epoch_results: Mapping[int, Mapping[str, Any]]) -> Optional[int]:
    """Apply retention filter, then logic/RC3 gates, then the fixed ranking."""
    retention_candidates = [
        epoch
        for epoch, result in epoch_results.items()
        if retention_gate_passed(result.get("retention", {}))
    ]
    gated = [
        epoch
        for epoch in retention_candidates
        if logic_gate_passed(epoch_results[epoch].get("logic_bridge", {}))
        and rc3_gate_passed(epoch_results[epoch].get("existing_rc3_bridge", {}), require_permutation=True)
    ]
    if not gated:
        return None
    return max(gated, key=lambda epoch: selection_key(epoch_results[epoch]))


def validate_output_path(path: Path = RUN1_DIR) -> None:
    if path.exists():
        raise FileExistsError(f"Run output already exists; resume/overwrite is disabled: {path}")


def dry_run_report(config: Mapping[str, Any], base_dir: Path = BASE_MODEL_DIR) -> Dict[str, Any]:
    base = verify_base_model(base_dir)
    mixture = prepare_mixture()
    bridge_count = len(load_jsonl(LOGIC_BRIDGE_FILE))
    if bridge_count != 480:
        raise ValueError(f"Logic Bridge contract failed: expected 480 records, got {bridge_count}")
    existing_bridge_count = len(load_jsonl(RC3_BRIDGE_FILE))
    if existing_bridge_count != 480:
        raise ValueError(
            f"Existing RC3 Bridge contract failed: expected 480 records, got {existing_bridge_count}"
        )
    retention_counts = {
        name: len(load_jsonl(path)) for name, path in RETENTION_SUITES.items()
    }
    if any(count <= 0 for count in retention_counts.values()):
        raise ValueError(f"Retention suite contract failed: {retention_counts}")
    return {
        "mode": "dry-run",
        "base_model": base,
        "old_replay": {
            "source": str(OLD_REPLAY_FILE),
            "source_records": mixture["old_source_count"],
            "source_groups": mixture["old_source_groups"],
            "unique_groups": mixture["old_replay_groups"],
            "unique_records": mixture["old_replay_count"],
        },
        "new_logic_train": {
            "source": str(NEW_TRAIN_FILE),
            "records": mixture["new_train_count"],
            "groups": mixture["new_train_groups"],
        },
        "logic_bridge": {"source": str(LOGIC_BRIDGE_FILE), "records": bridge_count},
        "existing_rc3_bridge": {"source": str(RC3_BRIDGE_FILE), "records": existing_bridge_count},
        "retention_suites": retention_counts,
        "mixture_records": mixture["mixed_count"],
        "mixture_groups": mixture["mixed_groups"],
        "gate_config": {
            "logic": dict(LOGIC_GATE),
            "existing_rc3_bridge": dict(RC3_GATE),
            "retention_mean": RETENTION_GATE,
        },
        "training_config": dict(config),
        "output": str(RUN1_DIR),
    }


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_eval_suites() -> Dict[str, Any]:
    logic_bridge = load_jsonl(LOGIC_BRIDGE_FILE)
    existing_rc3_bridge = load_jsonl(RC3_BRIDGE_FILE)
    if len(logic_bridge) != 480:
        raise ValueError(f"Logic Bridge contract failed: expected 480 records, got {len(logic_bridge)}")
    if len(existing_rc3_bridge) != 480:
        raise ValueError(
            "Existing RC3 Bridge contract failed: "
            f"expected 480 records, got {len(existing_rc3_bridge)}"
        )
    retention = {name: load_jsonl(path) for name, path in RETENTION_SUITES.items()}
    if any(not records for records in retention.values()):
        raise ValueError("Retention suite contract failed: an evaluation suite is empty")
    return {
        "logic_bridge": logic_bridge,
        "existing_rc3_bridge": existing_rc3_bridge,
        "retention": retention,
    }


def _evaluate_checkpoint(
    checkpoint: Path,
    device: str,
    suites: Mapping[str, Any],
    permutation: bool = False,
) -> Dict[str, Any]:
    from erabi.inference import GLiClassEngine

    engine = GLiClassEngine(model_id=str(checkpoint), device=device)
    result = {
        "logic_bridge": evaluate_logic_bridge(engine, suites["logic_bridge"]),
        "existing_rc3_bridge": evaluate_existing_bridge(
            engine, suites["existing_rc3_bridge"], test_permutation=permutation
        ),
        "retention": evaluate_retention(engine, suites["retention"]),
    }
    del engine
    return result


def run_training(
    config: Mapping[str, Any],
    output_dir: Path = RUN1_DIR,
    device: Optional[str] = None,
) -> Dict[str, Any]:
    validate_output_path(output_dir)
    base = verify_base_model()
    mixture = prepare_mixture()
    suites = _load_eval_suites()

    import torch
    import torch.nn.functional as F
    from erabi.train import Trainer, set_seed

    selected_device = device or "cuda:0"
    if not selected_device.startswith("cuda") or not torch.cuda.is_available():
        raise RuntimeError("RC3.1 Run 1 requires an available CUDA device; GPU execution was not requested in this run")
    set_seed(int(config["seed"]))
    output_dir.mkdir(parents=True, exist_ok=False)
    checkpoints_dir = output_dir / "checkpoints"
    checkpoints_dir.mkdir()
    _write_json(output_dir / "run_config.json", {"base_model": base, "config": dict(config), "data_counts": {k: v for k, v in mixture.items() if k.endswith("count") or k.endswith("groups")}})

    trainer = Trainer(
        model_id=str(BASE_MODEL_DIR),
        device=selected_device,
        lr=float(config["lr"]),
        weight_decay=float(config["weight_decay"]),
        gradient_accumulation_steps=int(config["gradient_accumulation_steps"]),
        micro_batch_size=int(config["micro_batch_size"]),
        seed=int(config["seed"]),
    )
    records = mixture["mixed_records"]
    total_micro_batches = math.ceil(len(records) / int(config["micro_batch_size"]))
    steps_per_epoch = math.ceil(total_micro_batches / int(config["gradient_accumulation_steps"]))
    total_steps = steps_per_epoch * int(config["epochs"])
    scaler = torch.amp.GradScaler("cuda", enabled=True)
    epoch_results: Dict[int, Dict[str, Any]] = {}
    optimizer_steps = 0

    for epoch in range(1, int(config["epochs"]) + 1):
        trainer.model.train()
        shuffled = shuffle_groups(records, int(config["seed"]) + epoch)
        micro_batches = [
            shuffled[index : index + int(config["micro_batch_size"])]
            for index in range(0, len(shuffled), int(config["micro_batch_size"]))
        ]
        rng = random.Random(int(config["seed"]) + epoch * 1009)
        total_loss = 0.0
        windows = math.ceil(len(micro_batches) / int(config["gradient_accumulation_steps"]))
        for window in range(windows):
            batches = micro_batches[
                window * int(config["gradient_accumulation_steps"]) : (window + 1) * int(config["gradient_accumulation_steps"])
            ]
            sample_count = sum(len(batch) for batch in batches)
            progress = optimizer_steps / max(1, total_steps - 1)
            if optimizer_steps < int(config["warmup_steps"]):
                current_lr = float(config["lr"]) * (optimizer_steps + 1) / int(config["warmup_steps"])
            else:
                cosine_progress = min(1.0, max(0.0, progress))
                current_lr = float(config["cosine_floor"]) + 0.5 * (
                    float(config["lr"]) - float(config["cosine_floor"])
                ) * (1.0 + math.cos(math.pi * cosine_progress))
            for parameter_group in trainer.optimizer.param_groups:
                parameter_group["lr"] = current_lr
            trainer.optimizer.zero_grad(set_to_none=True)
            for batch in batches:
                tokenized, target_indices, choice_counts, max_classes = trainer.prepare_batch(
                    batch, shuffle_choices=True, rng=rng
                )
                with torch.amp.autocast("cuda", dtype=torch.float16, enabled=True):
                    outputs = trainer.model(**tokenized, max_num_classes=max_classes)
                    batch_loss = torch.tensor(0.0, device=selected_device)
                    for row_index, (target_index, choice_count) in enumerate(zip(target_indices, choice_counts)):
                        logits = outputs.logits[row_index, :choice_count].to(torch.float32)
                        batch_loss = batch_loss + F.cross_entropy(
                            logits.unsqueeze(0), torch.tensor([target_index], device=selected_device)
                        )
                    loss = batch_loss / sample_count
                scaler.scale(loss).backward()
                total_loss += float(batch_loss.detach().cpu().item())
            scaler.unscale_(trainer.optimizer)
            torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), 1.0)
            scaler.step(trainer.optimizer)
            scaler.update()
            optimizer_steps += 1

        checkpoint = checkpoints_dir / f"epoch_{epoch}"
        checkpoint.mkdir()
        trainer.model.save_pretrained(checkpoint)
        trainer.tokenizer.save_pretrained(checkpoint)
        torch.save(
            {"optimizer": trainer.optimizer.state_dict(), "scaler": scaler.state_dict(), "epoch": epoch},
            checkpoint / "training_state.pt",
        )
        metrics = _evaluate_checkpoint(checkpoint, selected_device, suites, permutation=False)
        metrics.update({"epoch": epoch, "checkpoint": str(checkpoint), "mean_training_loss": total_loss / len(records)})
        epoch_results[epoch] = metrics
        _write_json(checkpoint / "results.json", metrics)

    # Permutation is reserved for epochs that pass the other selection gates.
    permutation_candidates = [
        epoch
        for epoch, result in epoch_results.items()
        if retention_gate_passed(result["retention"])
        and logic_gate_passed(result["logic_bridge"])
        and rc3_gate_passed(result["existing_rc3_bridge"], require_permutation=False)
    ]
    for epoch in permutation_candidates:
        checkpoint = Path(epoch_results[epoch]["checkpoint"])
        permutation_metrics = _evaluate_checkpoint(checkpoint, selected_device, suites, permutation=True)
        epoch_results[epoch]["existing_rc3_bridge"]["permutation_consistency"] = permutation_metrics[
            "existing_rc3_bridge"
        ]["permutation_consistency"]
        _write_json(checkpoint / "results.json", epoch_results[epoch])

    selected_epoch = select_checkpoint_epoch(epoch_results)
    summary = {
        "base_model": base,
        "config": dict(config),
        "data_counts": {k: v for k, v in mixture.items() if k.endswith("count") or k.endswith("groups")},
        "epoch_results": epoch_results,
        "permutation_candidates": permutation_candidates,
        "selected_epoch": selected_epoch,
        "selection_order": ["retention", "logic_bridge", "existing_rc3_bridge", "paired_both", "logic_mean_nll"],
    }
    _write_json(output_dir / "selection.json", summary)
    return summary


def run_baseline(device: str = "cuda:0") -> Path:
    base = verify_base_model()
    mixture = prepare_mixture()
    suites = _load_eval_suites()
    if not device.startswith("cuda"):
        raise RuntimeError("Baseline evaluation requires CUDA for this Run 1 driver")
    result = _evaluate_checkpoint(BASE_MODEL_DIR, device, suites, permutation=True)
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        output = BASELINE_DIR / f"baseline_results_{index:03d}.json"
        if not output.exists():
            break
        index += 1
    _write_json(
        output,
        {
            "base_model": base,
            "data_counts": {k: v for k, v in mixture.items() if k.endswith("count") or k.endswith("groups")},
            "metrics": result,
            "gates": {"logic": logic_gate_passed(result["logic_bridge"]), "rc3": rc3_gate_passed(result["existing_rc3_bridge"]), "retention": retention_gate_passed(result["retention"])},
        },
    )
    return output


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RC3.1 Run 1 continual training")
    parser.add_argument("--dry-run", action="store_true", help="Validate base/data/config without loading a model")
    parser.add_argument("--baseline-only", action="store_true", help="Evaluate the frozen base and write result JSON only")
    parser.add_argument("--device", default=None)
    parser.add_argument("--runs-dir", default=str(RUN1_DIR))
    parser.add_argument("--epochs", type=int, default=int(DEFAULT_CONFIG["epochs"]))
    parser.add_argument("--lr", type=float, default=float(DEFAULT_CONFIG["lr"]))
    parser.add_argument("--micro-batch-size", type=int, default=int(DEFAULT_CONFIG["micro_batch_size"]))
    parser.add_argument("--grad-accumulation-steps", type=int, default=int(DEFAULT_CONFIG["gradient_accumulation_steps"]))
    parser.add_argument("--weight-decay", type=float, default=float(DEFAULT_CONFIG["weight_decay"]))
    parser.add_argument("--warmup-steps", type=int, default=int(DEFAULT_CONFIG["warmup_steps"]))
    parser.add_argument("--cosine-floor", type=float, default=float(DEFAULT_CONFIG["cosine_floor"]))
    parser.add_argument("--seed", type=int, default=int(DEFAULT_CONFIG["seed"]))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.dry_run and args.baseline_only:
        raise ValueError("--dry-run and --baseline-only are mutually exclusive")
    config = {
        "epochs": args.epochs,
        "lr": args.lr,
        "micro_batch_size": args.micro_batch_size,
        "gradient_accumulation_steps": args.grad_accumulation_steps,
        "weight_decay": args.weight_decay,
        "warmup_steps": args.warmup_steps,
        "cosine_floor": args.cosine_floor,
        "seed": args.seed,
        "amp": "fp16",
        "scheduler": "warmup+cosine",
    }
    if args.dry_run:
        validate_output_path(Path(args.runs_dir))
        print(json.dumps(dry_run_report(config), ensure_ascii=False, indent=2, sort_keys=True))
        return
    if args.baseline_only:
        print(str(run_baseline(args.device or "cuda:0")))
        return
    summary = run_training(config, output_dir=Path(args.runs_dir), device=args.device)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
