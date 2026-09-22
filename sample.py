"""Minimal ERABI inference example."""

import argparse

from erabi.model_loader import load_engine
from erabi.schema import ChoiceRequest

parser = argparse.ArgumentParser()
parser.add_argument("--device", default="cpu")
parser.add_argument("--model-format", default="auto")
args = parser.parse_args()

engine = load_engine(device=args.device, model_format=args.model_format)
result = engine.predict(ChoiceRequest.from_dict({
    "context": "ノートを7冊、消しゴムを2個買った。",
    "question": "全部で何個？",
    "choices": [
        {"id": "nine", "text": "9個"},
        {"id": "ten", "text": "10個"},
    ],
}))
print("best:", result.best_candidate_id)
print("probabilities:", {choice.id: choice.probability for choice in result.choices})
