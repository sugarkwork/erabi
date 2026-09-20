import json
import sys
from pathlib import Path
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from erabi.schema import ChoiceRequest

tok = AutoTokenizer.from_pretrained("release/rc2/model")
cases = [json.loads(l) for l in open("data/sealed_acceptance_rc2_blind_v3/sealed_test_rc2_blind_v3.jsonl", encoding="utf-8") if l.strip()]

violations = []
high_tokens = []
for idx, c in enumerate(cases):
    req = ChoiceRequest.from_dict(c)
    text = f"Context: {req.context}\nQuestion: {req.question}"
    labels = [ch.text for ch in req.choices]
    text_enc = tok(text, add_special_tokens=False)["input_ids"]
    labels_enc = [tok(l, add_special_tokens=False)["input_ids"] for l in labels]
    total_tokens = len(text_enc) + sum(len(l) + 2 for l in labels_enc) + 2
    if total_tokens > 512:
        violations.append((idx, c["id"], c["family"], len(req.choices), total_tokens))
    elif total_tokens > 450:
        high_tokens.append((idx, c["id"], c["family"], len(req.choices), total_tokens))

print(f"Total violations (> 512 tokens): {len(violations)}")
for v in violations:
    print(v)
print(f"High token cases (450 - 512): {len(high_tokens)}")
for h in high_tokens:
    print(h)

