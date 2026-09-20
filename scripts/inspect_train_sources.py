import json
from pathlib import Path

train_files = [
    "data/m3_3_v2/train.jsonl",
    "data/m4_1_exception/train_exception.jsonl",
    "data/m6_operator/train_operator.jsonl",
    "data/m7_robustness/train_robustness.jsonl",
    "data/m8_general_choice/train_general.jsonl",
    "data/rc2_m17_choices/train_variable_choices_stream_a.jsonl",
    "data/rc2_m18_natural/train_natural_stream_a.jsonl",
    "data/rc2_m19_general/train_general_stream_a.jsonl",
    "data/m4_4_1_retention/combined_train_retention.jsonl"
]

unique_records = {}
for tf in train_files:
    p = Path(tf)
    if not p.exists():
        continue
    cnt = 0
    with open(p, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            fp = (r.get("context", "").strip(), r.get("question", "").strip())
            if fp not in unique_records:
                unique_records[fp] = r
                cnt += 1
    print(f"{tf}: added {cnt} new unique records (total unique so far: {len(unique_records)})")

print(f"\nTotal unique clean core records collected: {len(unique_records)}")
