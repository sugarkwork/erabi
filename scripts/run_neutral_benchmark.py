"""Run one implementation against the exact same neutral benchmark JSONL.

Use separate virtual environments for `--system erabi` and `--system laya`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import statistics
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def percentile(values, q):
    ordered = sorted(values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * q
    low = int(position)
    frac = position - low
    return ordered[low] if low + 1 == len(ordered) else ordered[low] * (1 - frac) + ordered[low + 1] * frac


def process_rss_mib():
    try:
        import psutil
        return psutil.Process().memory_info().rss / 1024**2
    except ImportError:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes
            class Counters(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
                            ("PrivateUsage", ctypes.c_size_t)]
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if psapi.GetProcessMemoryInfo(kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
                return counters.WorkingSetSize / 1024**2
        else:
            try:
                import resource
                value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                return value / 1024 if sys.platform != "darwin" else value / 1024**2
            except (ImportError, AttributeError):
                pass
        return None


def gpu_snapshot():
    try:
        output = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,temperature.gpu,clocks.sm,power.draw,utilization.gpu",
             "--format=csv,noheader,nounits"], check=True, capture_output=True, text=True, timeout=5
        ).stdout.splitlines()[0]
        values = [float(value.strip()) for value in output.split(",")]
        return dict(zip(("memory_used_mib", "memory_total_mib", "temperature_c", "sm_clock_mhz",
                         "power_w", "utilization_percent"), values))
    except (FileNotFoundError, IndexError, ValueError, subprocess.SubprocessError):
        return None


def summarise_samples(samples):
    if not samples:
        return {}
    keys = [key for key in samples[0] if key != "suite"]
    summary = {}
    for key in keys:
        values = [row[key] for row in samples if isinstance(row.get(key), (int, float))]
        if values:
            summary[key] = {"min": min(values), "median": statistics.median(values), "max": max(values)}
    return summary


class Sampler:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.current_suite = "loading"
        self.samples = []
        self.thread = None

    def start(self):
        if not self.enabled:
            return
        def collect():
            while not self.stop_event.wait(0.5):
                row = gpu_snapshot()
                rss = process_rss_mib()
                if row:
                    with self.lock:
                        self.samples.append({"suite": self.current_suite, "rss_mib": rss, **row})
        self.thread = threading.Thread(target=collect, daemon=True)
        self.thread.start()

    def set_suite(self, name: str):
        with self.lock:
            self.current_suite = name

    def snapshot(self, suite: str):
        row = gpu_snapshot() if self.enabled else None
        if row:
            with self.lock:
                self.samples.append({"suite": suite, "rss_mib": process_rss_mib(), **row})

    def stop(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=6)

    def suite_samples(self, suite: str):
        with self.lock:
            return [row for row in self.samples if row["suite"] == suite]


def macro_f1(gold, pred):
    labels = sorted(set(gold) | set(pred))
    scores = []
    for label in labels:
        tp = sum(a == label and b == label for a, b in zip(gold, pred))
        fp = sum(a != label and b == label for a, b in zip(gold, pred))
        fn = sum(a == label and b != label for a, b in zip(gold, pred))
        scores.append(2 * tp / max(1, 2 * tp + fp + fn))
    return sum(scores) / len(scores) if scores else None


def _load_cases(path: Path):
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows:
        raise ValueError(f"No cases in {path}")
    if any(not 2 <= len(row["choices"]) <= 16 for row in rows):
        raise ValueError("Benchmark case violates the shared 2-16 choice contract")
    return rows


def run_erabi(rows, args, manifest):
    if str(ROOT / "src") not in sys.path:
        sys.path.insert(0, str(ROOT / "src"))
    import torch
    from erabi.onnx_engine import ERABIONNXEngine
    from erabi.schema import ChoiceRequest, ChoiceInput

    device = args.device
    use_cuda = device.startswith("cuda")
    if use_cuda and not torch.cuda.is_available():
        raise RuntimeError("ERABI requested CUDA but torch reports no CUDA device")
    baseline_gpu = gpu_snapshot() if use_cuda else None
    rss_before = process_rss_mib()
    init_start = time.perf_counter()
    engine = ERABIONNXEngine(args.model_dir, device=device, max_tokens=512)
    engine.preparer.max_length = 512
    if use_cuda and "CUDAExecutionProvider" not in engine.active_providers:
        raise RuntimeError(f"ONNX CUDA provider did not activate: {engine.active_providers}")
    if use_cuda:
        torch.cuda.synchronize()
    init_seconds = time.perf_counter() - init_start
    after_load = gpu_snapshot() if use_cuda else None
    rss_after_load = process_rss_mib()

    requests = []
    token_counts = []
    for row in rows:
        labels = [choice["text"] for choice in row["choices"]]
        formatted = engine.preparer.prepare_input(row["context"], labels, prompt=row["question"])
        input_ids = engine.tokenizer(formatted, truncation=False, padding=False)["input_ids"]
        token_count = len(input_ids)
        token_counts.append(token_count)
        if token_count > 512:
            raise ValueError(f"ERABI's 512-token fail-closed limit exceeded by {row['id']} ({token_count} tokens); rebuild with shorter contexts")
        requests.append(ChoiceRequest(context=row["context"], question=row["question"],
                                      choices=[ChoiceInput(id=c["id"], text=c["text"]) for c in row["choices"]]))

    for request in requests[:args.warmup]:
        engine.predict(request, temperature=1.0)
    if use_cuda:
        torch.cuda.synchronize()
    grouped = defaultdict(list)
    suite_wall = {}
    sampler = Sampler(use_cuda)
    sampler.start()
    inference_start = time.perf_counter()
    for suite in sorted({row["suite"] for row in rows}):
        sampler.set_suite(suite)
        suite_start = time.perf_counter()
        suite_rows = [(index, row) for index, row in enumerate(rows) if row["suite"] == suite]
        for index, row in suite_rows:
            if use_cuda:
                torch.cuda.synchronize()
            started = time.perf_counter()
            response = engine.predict(requests[index], temperature=1.0)
            if use_cuda:
                torch.cuda.synchronize()
            elapsed = (time.perf_counter() - started) * 1000
            choice_index = next(i for i, choice in enumerate(requests[index].choices)
                                if choice.id == response.best_candidate_id)
            grouped[suite].append({"id": row["id"], "gold_label": row["gold_label"],
                                   "predicted_label": row["choices"][choice_index]["text"],
                                   "correct": response.best_candidate_id == row["gold_choice_id"],
                                   "latency_ms": elapsed, "input_tokens": token_counts[index],
                                   "choice_count": len(row["choices"]), "model": "ERABI ONNX FP16"})
        suite_wall[suite] = time.perf_counter() - suite_start
        sampler.snapshot(suite)
    wall_seconds = time.perf_counter() - inference_start
    sampler.stop()
    return _result("erabi", rows, grouped, suite_wall, manifest, args, init_seconds,
                   baseline_gpu, after_load, rss_before, rss_after_load, sampler, wall_seconds,
                   {"active_providers": engine.active_providers, "model_dir": str(Path(args.model_dir).resolve()),
                    "onnxruntime_version": __import__("onnxruntime").__version__,
                    "torch_version": torch.__version__, "torch_cuda_runtime": torch.version.cuda,
                    "input_token_limit": 512, "truncated_count": 0,
                    "input_token_min": min(token_counts), "input_token_max": max(token_counts)})


def run_laya(rows, args, manifest):
    if args.laya_repo not in sys.path:
        sys.path.insert(0, args.laya_repo)
    import torch
    from laya import Router, __version__

    if not torch.cuda.is_available():
        raise RuntimeError("Laya GPU run requested but torch reports no CUDA device")
    baseline_gpu = gpu_snapshot()
    rss_before = process_rss_mib()
    init_start = time.perf_counter()
    router = Router(device=args.device, default="multilingual", revision=args.laya_revision,
                    max_loaded=2, auto_task_detection=False)
    router.preload(["english", "multilingual"])
    torch.cuda.synchronize()
    init_seconds = time.perf_counter() - init_start
    after_load = gpu_snapshot()
    rss_after_load = process_rss_mib()

    requests = []
    audits = []
    routes = []
    for row in rows:
        questions = {"answer": {"type": "choice", "instructions": row["question"],
                                "criteria": {c["text"]: None for c in row["choices"]}}}
        route = router.route(row["context"], questions)
        model_name = route["model"]
        agent = router.load(model_name)
        internal = {"answer": agent._to_internal(questions["answer"])}
        capped = agent._encode_state(row["context"], ["answer"], internal)[0]
        full = agent._encode_state(row["context"], ["answer"], internal,
                                   max_len=8192, head_max_len=2048)[0]
        options = capped.get("options", {})
        raw_option_tokens = [len(agent.tok(" " + c["text"], add_special_tokens=False)["input_ids"])
                             for c in row["choices"]]
        audits.append({"id": row["id"], "input_tokens_capped": len(capped["ids"]),
                       "input_tokens_full": len(full["ids"]),
                       "truncated": len(capped["ids"]) < len(full["ids"]),
                       "options": len(row["choices"]),
                       "options_distinct_after_budget": options.get("options_distinct"),
                       "tokens_per_option_after_shared_budget": options.get("tokens_per_option"),
                       "options_over_laya_48_token_cap": sum(n > 48 for n in raw_option_tokens)})
        requests.append((questions, model_name))
        routes.append(model_name)

    for row, (questions, model_name) in zip(rows[:args.warmup], requests[:args.warmup]):
        router.predict(row["context"], questions, max_len=None, head_max_len=None)
    torch.cuda.synchronize()
    sampler = Sampler(True)
    sampler.start()
    grouped = defaultdict(list)
    suite_wall = {}
    inference_start = time.perf_counter()
    for suite in sorted({row["suite"] for row in rows}):
        sampler.set_suite(suite)
        suite_start = time.perf_counter()
        for index, row in enumerate(rows):
            if row["suite"] != suite:
                continue
            questions, model_name = requests[index]
            torch.cuda.synchronize()
            started = time.perf_counter()
            response = router.predict(row["context"], questions)
            torch.cuda.synchronize()
            elapsed = (time.perf_counter() - started) * 1000
            answer = response["answers"]["answer"]
            predicted_label = answer["choice"]
            predicted_index = next(i for i, choice in enumerate(row["choices"])
                                   if choice["text"] == predicted_label)
            grouped[suite].append({"id": row["id"], "gold_label": row["gold_label"],
                                   "predicted_label": row["choices"][predicted_index]["text"],
                                   "correct": row["choices"][predicted_index]["id"] == row["gold_choice_id"],
                                   "latency_ms": elapsed,
                                   "input_tokens": response.get("usage", {}).get("input_tokens"),
                                   "choice_count": len(row["choices"]),
                                   "model": response.get("routing", {}).get("model", model_name)})
        suite_wall[suite] = time.perf_counter() - suite_start
        sampler.snapshot(suite)
    wall_seconds = time.perf_counter() - inference_start
    sampler.stop()
    cap_counts = Counter(audit["options_over_laya_48_token_cap"] > 0 for audit in audits)
    agents = {name: router.load(name) for name in router.loaded}
    runtime = {name: {
        "device": str(agent.device),
        "dtype": str(agent.dtype),
        "parameter_dtype": str(next(agent.model.parameters()).dtype),
        "amp_enabled": bool(agent.amp_enabled),
        "fast_path_enabled": agent._fast is not None,
        "compiled": bool(getattr(agent, "_compiled", False)),
    } for name, agent in agents.items()}
    return _result("laya", rows, grouped, suite_wall, manifest, args, init_seconds,
                   baseline_gpu, after_load, rss_before, rss_after_load, sampler, wall_seconds,
                   {"version": __version__, "revision": args.laya_revision,
                    "torch_version": torch.__version__, "torch_cuda_runtime": torch.version.cuda,
                    "transformers_version": __import__("transformers").__version__,
                    "runtime_settings": runtime,
                    "loaded_revisions": router.loaded_revisions,
                    "checkpoints": ["english", "multilingual"], "routing_counts": dict(Counter(routes)),
                    "max_len": {name: router.load(name).cfg.get("max_len") for name in router.loaded},
                    "head_max_len": {name: router.load(name).cfg.get("head_max_len") for name in router.loaded},
                    "truncated_count": sum(audit["truncated"] for audit in audits),
                    "laya_48_token_cap_hit_rows": cap_counts[True],
                    "laya_48_token_cap_hit_options": sum(audit["options_over_laya_48_token_cap"] for audit in audits),
                    "collapsed_option_rows": sum(
                        audit["options_distinct_after_budget"] is not None
                        and audit["options_distinct_after_budget"] < audit["options"]
                        for audit in audits
                    ),
                    "audit_token_range": {"min": min(audit["input_tokens_capped"] for audit in audits),
                                          "max": max(audit["input_tokens_capped"] for audit in audits)}}, audits)


def _result(system, rows, grouped, suite_wall, manifest, args, init_seconds,
            gpu_before, gpu_after_load, rss_before, rss_after_load, sampler, wall_seconds,
            engine, audits=None):
    suites = {}
    record_list = []
    for suite in sorted(grouped):
        records = grouped[suite]
        record_list.extend(records)
        gold = [row["gold_label"] for row in records]
        pred = [row["predicted_label"] for row in records]
        latencies = [row["latency_ms"] for row in records]
        samples = sampler.suite_samples(suite)
        gpu = summarise_samples(samples)
        suites[suite] = {
            "n": len(records), "correct": sum(row["correct"] for row in records),
            "accuracy": sum(row["correct"] for row in records) / len(records),
            "macro_f1": macro_f1(gold, pred),
            "chance_accuracy_mean": statistics.mean(1 / row["choice_count"] for row in records),
            "latency_ms": {"mean": statistics.mean(latencies), "p50": percentile(latencies, .50),
                           "p95": percentile(latencies, .95), "min": min(latencies), "max": max(latencies)},
            "wall_seconds": suite_wall[suite], "throughput_requests_per_second": len(records) / suite_wall[suite],
            "gpu_samples": len(samples), "gpu_sample_summary": gpu,
            "process_rss_peak_mib": max((sample["rss_mib"] for sample in samples if sample.get("rss_mib") is not None), default=None),
            "model_counts": dict(Counter(row["model"] for row in records)),
        }
    result = {
        "format": "erabi-laya-neutral-run-v1", "system": system,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "cases_sha256": manifest["cases_sha256"], "cases": len(rows),
        "engine_initialization_seconds": init_seconds,
        "overall_wall_seconds": wall_seconds,
        "overall_throughput_requests_per_second": len(rows) / wall_seconds,
        "process_rss_mib": {"before_model_load": rss_before, "after_model_load": rss_after_load,
                            "peak_sampled": max((sample["rss_mib"] for sample in sampler.samples if sample.get("rss_mib") is not None), default=None)},
        "gpu_total_memory_mib": {"before_model_load": gpu_before, "after_model_load": gpu_after_load,
                                 "peak_sampled": max((sample["memory_used_mib"] for sample in sampler.samples
                                                      if sample.get("memory_used_mib") is not None), default=None),
                                 "samples": summarise_samples(sampler.samples)},
        "gpu_memory_caveat": "nvidia-smi reports whole-device memory, including unrelated processes; 0.5 s polling can miss brief peaks and does not attribute VRAM to this process.",
        "gpu_sampling_interval_seconds": 0.5,
        "engine": engine, "suites": suites,
        "records": sorted(record_list, key=lambda row: row["id"]),
    }
    if audits is not None:
        result["input_audits"] = audits
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system", choices=("erabi", "laya"), required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model-dir", help="ERABI ONNX FP16 model directory")
    parser.add_argument("--laya-repo", default=r"F:\ai\laya-local")
    parser.add_argument("--laya-revision", default="reviewed")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--limit-per-suite", type=int,
                        help="Smoke-only cap applied after verifying the full shared input file")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    cases_path = args.cases.resolve()
    manifest_path = args.manifest.resolve() if args.manifest else cases_path.with_name("manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _load_cases(cases_path)
    if len(rows) != manifest["total_cases"]:
        raise ValueError("Case count does not match manifest")
    if manifest["cases_sha256"] != __import__("hashlib").sha256(cases_path.read_bytes()).hexdigest():
        raise ValueError("cases.jsonl SHA256 does not match manifest")
    if args.limit_per_suite is not None:
        if args.limit_per_suite < 1:
            parser.error("--limit-per-suite must be positive")
        limited = []
        seen = defaultdict(int)
        for row in rows:
            if seen[row["suite"]] < args.limit_per_suite:
                limited.append(row)
                seen[row["suite"]] += 1
        rows = limited
    result = run_erabi(rows, args, manifest) if args.system == "erabi" else run_laya(rows, args, manifest)
    result["run_mode"] = "smoke_subset" if args.limit_per_suite is not None else "full"
    result["limit_per_suite"] = args.limit_per_suite
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"system": result["system"], "cases": result["cases"],
                      "initialization_seconds": result["engine_initialization_seconds"],
                      "throughput": result["overall_throughput_requests_per_second"],
                      "suites": {name: {"n": stat["n"], "accuracy": stat["accuracy"],
                                        "p50_ms": stat["latency_ms"]["p50"]}
                                 for name, stat in result["suites"].items()},
                      "output": str(args.output.resolve())}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
