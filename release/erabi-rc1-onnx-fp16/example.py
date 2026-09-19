"""ERABI RC1 ONNX FP16 Usage Example."""

from pathlib import Path
from erabi.onnx_engine import ERABIONNXEngine
from erabi.schema import ChoiceRequest

MODEL_DIR = Path(__file__).parent

def main():
    engine = ERABIONNXEngine(str(MODEL_DIR), device="cuda")
    print("Engine initialized with providers:", engine.active_providers)

    request_dict = {
        "context": "物流拠点：製品『ITEM-001』の保管在庫数はちょうど110個です。出荷検査証を受領済みです。",
        "question": "数量が110を下回らない（110を含む）場合は出荷する、欠落していれば保留するを適用してください。",
        "choices": [
            {"id": "ship", "text": "出荷する"},
            {"id": "hold", "text": "保留する"}
        ]
    }

    req = ChoiceRequest.from_dict(request_dict)
    resp = engine.predict(req, temperature=0.256, return_logits=True)

    print(f"Decision: {resp.best_candidate_id}")
    print("Full probability distribution:")
    for c in resp.choices:
        print(f"  - {c.id}: {c.probability:.6f}")
    print(f"Raw Logits: {resp.raw_logits}")

if __name__ == "__main__":
    main()
