"""Diagnose error cases of best 438M Large model on RC3 Bridge Benchmark."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from erabi.inference import GLiClassEngine
from scripts.train_rc3 import evaluate_records, load_jsonl

MODEL_PATH = ROOT / "runs" / "rc3_large_curriculum" / "best_model"
BRIDGE_FILE = ROOT / "data" / "rc3_bridge" / "rc3_bridge_benchmark.jsonl"


def main():
    print(f"Loading engine from {MODEL_PATH}...")
    engine = GLiClassEngine(model_id=str(MODEL_PATH), device="cuda:0")
    records = load_jsonl(BRIDGE_FILE)
    res = evaluate_records(engine, records, test_permutation=False)

    print(f"Total: {res['total_cases']}, Correct: {res['correct']}, Accuracy: {res['accuracy']*100:.2f}%")
    print(f"Paired Both: {res['paired_both']}/{res['paired_total']} ({res['paired_both_rate']*100:.2f}%)")

    wrongs = [c for c in res["cases"] if not c["correct"]]
    print(f"\nTotal Errors: {len(wrongs)}")

    fam_counts = Counter(c["family"] for c in wrongs)
    print("\nErrors by family:")
    for fam, cnt in fam_counts.most_common():
        total_fam = res["by_family"][fam]["total"]
        acc = res["by_family"][fam]["accuracy"]
        print(f"  - {fam:25s}: {cnt:2d}/{total_fam:2d} wrong ({acc*100:.1f}% acc)")

    # Inspect groups where one or both failed
    group_map = {}
    for c in res["cases"]:
        group_map.setdefault(c["group_id"], []).append(c)

    failed_pairs = {gid: pair for gid, pair in group_map.items() if not (pair[0]["correct"] and pair[1]["correct"])}
    print(f"\nTotal Groups with >=1 failure: {len(failed_pairs)}/240")

    # Sample error analysis
    print("\nSample Errors:")
    record_map = {r["id"]: r for r in records}
    for c in wrongs[:15]:
        r = record_map[c["id"]]
        print(f"\nID: {c['id']} | Family: {c['family']} | K: {len(r['choices'])}")
        print(f"Context: {r['context'][:120]}...")
        print(f"Question: {r['question']}")
        print(f"Target: {c['target']} | Pred: {c['pred']} (p_pred: {c['p_pred']:.4f}, p_tgt: {c['p_target']:.4f})")
        c_texts = {choice['id']: choice['text'] for choice in r['choices']}
        print(f"Target Text: {c_texts.get(c['target'])}")
        print(f"Pred Text:   {c_texts.get(c['pred'])}")


if __name__ == "__main__":
    main()
