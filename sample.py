"""Experimental Jev-like choice decisions with GLiClass."""

import argparse
from time import perf_counter

from erabi.model_loader import load_engine
from erabi.schema import ChoiceRequest

parser = argparse.ArgumentParser()
parser.add_argument("--device", default="cpu")
parser.add_argument("--model-format", default="auto")
args = parser.parse_args()

print("ERABI: recreating Jev-like choice decisions with GLiClass (experimental, not official Jev).", flush=True)
print("Runtime: ONNX Runtime or PyTorch; model downloaded from Hugging Face.", flush=True)
print(f"[1/2] Loading model (device={args.device}, format={args.model_format})...", flush=True)
started = perf_counter()
engine = load_engine(device=args.device, model_format=args.model_format)
print(f"[1/2] Model ready in {perf_counter() - started:.2f}s (format={engine.model_format})", flush=True)

request = ChoiceRequest.from_dict({
    "context": "ノートを7冊、消しゴムを2個買った。",
    "question": "全部で何個？",
    "choices": [
        {"id": "nine", "text": "9個"},
        {"id": "ten", "text": "10個"},
    ],
})
print("[2/2] Running inference...", flush=True)
started = perf_counter()
result = engine.predict(request)
print(f"[2/2] Inference done in {perf_counter() - started:.2f}s", flush=True)
print("best:", result.best_candidate_id)
print("probabilities:", {choice.id: choice.probability for choice in result.choices})
