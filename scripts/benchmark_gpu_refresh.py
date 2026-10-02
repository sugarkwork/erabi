"""Matched local single-request evaluation; no API calls or input command execution."""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.metadata
import json
import math
import random
import statistics
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_CLEF_SOURCE = "0e304cf7c6500e8bb59bef7e2afd2c6373f82596dfb3b57d1aa93c175e2dc3a3"
sys.path.insert(0, str(ROOT / "src"))
from scripts.run_neutral_benchmark import gpu_snapshot, percentile


def read_cases(paths, limit, public_limit=None, sample_seed=None):
    rows, sources = [], []
    for path in paths:
        raw = path.read_bytes()
        sources.append({"file": path.name, "sha256": hashlib.sha256(raw).hexdigest()})
        for row in (json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()):
            if "gold_choice_id" in row:
                row = {**row, "target": {"kind": "hard", "choice_id": row["gold_choice_id"]},
                       "domain": "public/" + row["suite"], "canonical_group_id": row["id"]}
            else:
                row = {**row, "domain": "decision/" + row["domain"]}
            ids = [c["id"] for c in row["choices"]]
            if len(set(ids)) != len(ids) or row["target"].get("kind") != "hard" or row["target"].get("choice_id") not in ids:
                raise ValueError("Invalid benchmark choice IDs or hard target")
            rows.append(row)
    if limit or public_limit:
        groups = collections.defaultdict(list)
        for index, row in enumerate(rows):
            groups[row["domain"]].append(index)
        chosen = set()
        rng = random.Random(sample_seed)
        for domain, indices in groups.items():
            quota = public_limit if domain.startswith("public/") and public_limit else limit
            if quota is None or len(indices) <= quota:
                chosen.update(indices)
            else:
                chosen.update(indices[:quota] if sample_seed is None else rng.sample(indices, quota))
        rows = [row for index, row in enumerate(rows) if index in chosen]
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Empty input or duplicate IDs")
    return rows, sources


def load_predictor(args):
    import torch
    if args.system.startswith("erabi"):
        from erabi.model_loader import load_engine
        from erabi.schema import ChoiceRequest
        fmt = {"erabi_fp16": "onnx-fp16", "erabi_fp32": "onnx-fp32", "erabi_pytorch": "pytorch"}[args.system]
        engine = load_engine(model_id=str(args.model_dir), model_format=fmt, device=args.device)
        if args.device.startswith("cuda") and fmt.startswith("onnx") and "CUDAExecutionProvider" not in engine.active_providers:
            raise RuntimeError("CUDA provider unavailable; refusing CPU fallback")

        def predict(row):
            response = engine.predict(ChoiceRequest.from_dict(row))
            if response.usage.truncated:
                raise RuntimeError("Unexpected truncation")
            return response.best_candidate_id, {c.id: c.probability for c in response.choices}, response.usage.input_tokens
        return predict, {"format": fmt, "providers": getattr(engine, "active_providers", None),
                         "provider_options": engine.session.get_provider_options() if hasattr(engine, "session") else None}
    if args.system == "laya":
        sys.path.insert(0, args.laya_repo)
        from laya import Router
        from laya.common import render_options
        router = Router(device=args.device, default="multilingual", revision="reviewed", max_loaded=2, auto_task_detection=False)
        router.preload(["english", "multilingual"])
        checkpoint_revisions = {}
        for name in ("english", "multilingual"):
            agent = router.load(name)
            checkpoint_revisions[name] = {"repo": agent.model_id, "revision": agent.revision,
                                          "subfolder": router.models[name][1],
                                          "autocast_enabled": agent.amp_enabled,
                                          "compute_dtype": str(agent.dtype),
                                          "parameter_dtype": str(next(agent.model.parameters()).dtype)}
        audits = collections.Counter()

        def question_payload(row):
            criteria = {c["id"]: c["text"] for c in row["choices"]}
            if args.laya_text_keys:
                criteria = {c["text"]: None for c in row["choices"]}
                if len(criteria) != len(row["choices"]):
                    raise RuntimeError("Text-key encoding requires unique option descriptions")
            return {"answer": {"type": "choice", "instructions": row["question"], "criteria": criteria}}

        def predict(row):
            questions = question_payload(row)
            answer = router.predict(row["context"], questions, max_len=8192, head_max_len=2048)
            output = answer["answers"]["answer"]
            if args.laya_text_keys:
                ids = {c["text"]: c["id"] for c in row["choices"]}
                return ids[output["choice"]], {ids[k]: v for k, v in output["probabilities"].items()}, answer["usage"]["input_tokens"]
            return output["choice"], output["probabilities"], answer["usage"]["input_tokens"]

        # Audit outside the timed region using the same rendering settings.
        def audit(row):
            questions = question_payload(row)
            route = router.route(row["context"], questions)
            agent = router.load(route["model"])
            internal = {"answer": agent._to_internal(questions["answer"])}
            rendered = render_options(internal["answer"])
            mask_token = agent.tok.mask_token or "[MASK]"
            audits["options_over_48_tokens"] += sum(len(agent.tok(" " + option.replace(mask_token, " "), add_special_tokens=False)["input_ids"]) > 48 for option in rendered)
            encoded = agent._encode_state(row["context"], ["answer"], internal, max_len=8192, head_max_len=2048)[0]
            full = agent._encode_state(row["context"], ["answer"], internal, max_len=32768, head_max_len=8192)[0]
            if len(encoded["ids"]) != len(full["ids"]):
                raise RuntimeError("Laya input truncated")
            audits["rows"] += 1
        return predict, {"revision": "reviewed", "checkpoints": ["english", "multilingual"],
                         "checkpoint_revisions": checkpoint_revisions,
                         "criteria_encoding": "text keys" if args.laya_text_keys else "ID:description",
                         "option_audit": audits, "audit": audit, "max_len": 8192, "head_max_len": 2048}

    # Official, locally reviewed source is imported only from the pinned checkout.
    from transformers import AutoTokenizer, BitsAndBytesConfig, Qwen3_5ForConditionalGeneration
    from safetensors.torch import load_file
    if args.device != "cuda:0":
        raise ValueError("CLEF benchmark uses one GPU (cuda:0) with CPU offload")
    source_hash = hashlib.sha256((args.model_dir / "joint_schema_model.py").read_bytes()).hexdigest()
    if source_hash != REVIEWED_CLEF_SOURCE:
        raise RuntimeError("CLEF source differs from the locally reviewed pinned source")
    sys.path.insert(0, str(args.model_dir.resolve()))
    from joint_schema_model import JointSchemaHead, collate_records, encode_record
    kwargs = {"dtype": torch.bfloat16, "local_files_only": True, "trust_remote_code": False,
              "device_map": "auto", "max_memory": {0: "12GiB", "cpu": "52GiB"}, "attn_implementation": "sdpa"}
    if args.system == "clef_nf4":
        kwargs["quantization_config"] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16, llm_int8_enable_fp32_cpu_offload=True)
        # Explicit CPU modules are excluded from quantization by Transformers. With
        # an "auto" map, quantized CPU layers hit a nested quant-state/meta error
        # in the tested bitsandbytes/Accelerate combination.
        config = json.loads((args.model_dir / "config.json").read_text())
        layers = config["text_config"]["num_hidden_layers"]
        if not 1 <= args.clef_gpu_layers < layers:
            raise ValueError("--clef-gpu-layers must leave at least one layer on CPU")
        kwargs["device_map"] = {"model.visual": "cpu", "lm_head": "cpu",
                                "model.language_model.embed_tokens": 0,
                                "model.language_model.norm": 0,
                                "model.language_model.rotary_emb": 0,
                                **{f"model.language_model.layers.{i}": 0 if i < args.clef_gpu_layers else "cpu" for i in range(layers)}}
    backbone = Qwen3_5ForConditionalGeneration.from_pretrained(args.model_dir, **kwargs).eval()
    backbone.config.use_cache = False
    head = JointSchemaHead(**json.loads((args.model_dir / "joint_head_config.json").read_text()))
    head.load_state_dict(load_file(args.model_dir / "joint_head.safetensors"), strict=True)
    head = head.to(device=args.device, dtype=torch.bfloat16).eval()
    # This benchmark contains text only; the official encoder accepts processor=None.
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, local_files_only=True, trust_remote_code=False)
    text_model = backbone.model.language_model
    # RoPE has non-persistent buffers, which Accelerate's CPU-offload hooks can
    # miss because they are absent from state_dict. Text inputs execute on CUDA.
    text_model.rotary_emb.to(args.device)
    storage = collections.Counter()
    for parameter in backbone.parameters():
        storage[f"{parameter.device}:{parameter.dtype}"] += parameter.numel() * parameter.element_size()

    def predict(row):
        request = {"state": row["context"], "questions": {"answer": {"type": "choice", "instructions": row["question"],
                    "criteria": {c["id"]: c["text"] for c in row["choices"]}}}}
        # Encode once at a large bound; reject instead of truncating at the benchmark limit.
        encoded = encode_record(tokenizer, request, max_length=65536)
        if len(encoded.input_ids) > 16384:
            raise RuntimeError("CLEF benchmark input exceeds 16384 tokens")
        pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
        batch = collate_records([encoded], pad_id, torch.device(args.device))
        outputs = text_model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"], use_cache=False, return_dict=True)
        hidden = outputs.last_hidden_state.to(device=args.device, dtype=torch.bfloat16)
        output_module = backbone.get_output_embeddings()
        embedding = output_module.weight
        if embedding.device.type == "meta":
            # Accelerate may keep CPU-offloaded weights in its hook rather than the module.
            embedding = output_module._hf_hook.weights_map["weight"]
        # Head uses only per-option embedding slices. Move slices, not the full vocabulary table.
        class EmbeddingView:
            def __getitem__(self, indices):
                return embedding[indices.to(embedding.device)].to(device=args.device, dtype=hidden.dtype)
        logits = head(hidden, batch["input_ids"], batch["attention_mask"], batch["records"], EmbeddingView())[0][0]
        probabilities = dict(zip(encoded.questions[0].option_ids, logits.float().softmax(-1).tolist()))
        return max(probabilities, key=probabilities.get), probabilities, len(encoded.input_ids)
    return predict, {"dtype": "BF16", "quantization": "NF4 double quant" if args.system == "clef_nf4" else "none",
                     "max_memory": {"cuda:0": "12GiB", "cpu": "52GiB"},
                     "placement": "explicit map; max_memory is not a placement cap" if args.system == "clef_nf4" else "auto map with max_memory",
                     "device_map": {k: str(v) for k, v in backbone.hf_device_map.items()},
                     "parameter_storage_bytes": dict(storage),
                     "head": "official BF16; CPU embedding slices moved to head device",
                     "candidate_order": "official encoder sorts option IDs; probabilities mapped back by ID",
                     "source_sha256": source_hash}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", required=True, choices=("erabi_fp16", "erabi_fp32", "erabi_pytorch", "laya", "clef_nf4", "clef_offload"))
    parser.add_argument("--input", required=True, type=Path, nargs="+")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--laya-repo", default=str(ROOT.parent / "laya-local"))
    parser.add_argument("--laya-text-keys", action="store_true", help="Diagnostic: choice text as Laya criteria keys; map results back to original IDs")
    parser.add_argument("--clef-gpu-layers", type=int, default=52, help="NF4: explicit GPU layer count; CPU layers remain unquantized")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--limit-per-domain", type=int)
    parser.add_argument("--public-limit-per-domain", type=int, help="Limit public suites only; retain the entire private test")
    parser.add_argument("--sample-seed", type=int, help="Seeded random per-domain subsampling instead of first rows")
    parser.add_argument("--warmup", type=int, default=8)
    args = parser.parse_args()
    if args.limit_per_domain is not None and args.limit_per_domain < 1:
        parser.error("--limit-per-domain must be positive")
    if args.public_limit_per_domain is not None and args.public_limit_per_domain < 1:
        parser.error("--public-limit-per-domain must be positive")
    if args.warmup < 0:
        parser.error("--warmup must be nonnegative")
    if args.output.exists() or args.output.with_suffix(".jsonl").exists():
        raise FileExistsError("Results preserved; use a new output")
    rows, sources = read_cases(args.input, args.limit_per_domain, args.public_limit_per_domain, args.sample_seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    import psutil
    import torch
    torch.set_num_threads(8)
    cuda = args.device.startswith("cuda")
    process, stop, samples = psutil.Process(), threading.Event(), []
    before = gpu_snapshot() if cuda else None
    def sample():
        while not stop.is_set():
            samples.append({"rss_mib": process.memory_info().rss / 2**20, "gpu": gpu_snapshot() if cuda else None})
            stop.wait(.5 if cuda else .05)
    sampler = threading.Thread(target=sample, daemon=True)
    sampler.start()
    records = []
    try:
        init = time.perf_counter()
        predict, metadata = load_predictor(args)
        if cuda:
            torch.cuda.synchronize()
        init_seconds = time.perf_counter() - init
        audit = metadata.pop("audit", None)
        if audit:
            for row in rows:
                audit(row)
        with torch.inference_mode():
            for row in rows[:args.warmup]:
                predict(row)
            if cuda:
                torch.cuda.synchronize()
                torch.cuda.reset_peak_memory_stats()
            started = time.perf_counter()
            with args.output.with_suffix(".jsonl").open("x", encoding="utf-8") as stream:
                for index, row in enumerate(rows, 1):
                    if cuda:
                        torch.cuda.synchronize()
                    start = time.perf_counter()
                    best, probabilities, tokens = predict(row)
                    if cuda:
                        torch.cuda.synchronize()
                    elapsed = (time.perf_counter() - start) * 1000
                    ids = [c["id"] for c in row["choices"]]
                    if best not in ids or set(probabilities) != set(ids) or any(not math.isfinite(p) or not 0 <= p <= 1 for p in probabilities.values()) or not math.isclose(sum(probabilities.values()), 1, abs_tol=.02):
                        raise RuntimeError("Invalid candidate distribution")
                    record = {"id": row["id"], "domain": row["domain"], "language": row["language"], "best": best,
                              "correct": best == row["target"]["choice_id"], "probabilities": probabilities,
                              "tokens": tokens, "elapsed_ms": elapsed}
                    records.append(record)
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                    stream.flush()
                    if index % 50 == 0 or index == len(rows):
                        print(f"{args.system}: {index}/{len(rows)}", flush=True)
            wall = time.perf_counter() - started
    finally:
        stop.set()
        sampler.join(timeout=6)
    def metrics(group):
        latencies = [r["elapsed_ms"] for r in group]
        return {"n": len(group), "correct": sum(r["correct"] for r in group), "accuracy": statistics.mean(r["correct"] for r in group),
                "mean_ms": statistics.mean(latencies), "p50_ms": percentile(latencies, .5), "p95_ms": percentile(latencies, .95)}
    gpu_samples = [s["gpu"] for s in samples if s["gpu"]]
    report = {"system": args.system, "sources": sources, "mode": "subset" if args.limit_per_domain or args.public_limit_per_domain else "full",
              "selection": {"limit_per_domain": args.limit_per_domain, "public_limit_per_domain": args.public_limit_per_domain, "sample_seed": args.sample_seed},
              "device": args.device, "warmup": args.warmup, "batch": 1, "metadata": metadata,
              "gpu_name": torch.cuda.get_device_name() if cuda else None,
              "cuda_runtime": torch.version.cuda,
              "torch_matmul_precision": torch.get_float32_matmul_precision(),
              "init_seconds": init_seconds, "wall_seconds": wall, "requests_per_second": len(records) / wall,
              "overall": metrics(records), "by_domain": {d: metrics([r for r in records if r["domain"] == d]) for d in sorted({r["domain"] for r in records})},
              "peak_rss_mib": max(s["rss_mib"] for s in samples), "gpu_before": before,
              "gpu_peak_mib": max((s["memory_used_mib"] for s in gpu_samples), default=None),
              "gpu_samples": gpu_samples, "torch_peak_allocated_mib": torch.cuda.max_memory_allocated() / 2**20 if cuda else None,
              "torch_peak_reserved_mib": torch.cuda.max_memory_reserved() / 2**20 if cuda else None,
              "versions": {},
              "notes": "Network-free inference; batch 1; per-call GPU sync; tokenizer included; nvidia-smi is whole-device; PyTorch allocator excludes ONNX allocations."}
    for package in ("torch", "transformers", "onnxruntime-gpu", "bitsandbytes", "accelerate"):
        try:
            report["versions"][package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            report["versions"][package] = None
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("system", "overall", "init_seconds", "peak_rss_mib", "gpu_peak_mib")}), flush=True)


if __name__ == "__main__":
    main()
