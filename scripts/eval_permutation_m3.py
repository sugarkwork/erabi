"""Permutation sensitivity evaluation on 20 balanced cases from final_test.jsonl."""

from __future__ import annotations

import json
import random
from erabi.inference import GLiClassEngine
from erabi.schema import ChoiceRequest

def main():
    model_id = "runs/m2_1/trained_instruct_base/checkpoint"
    input_file = "data/m3_1/final_test.jsonl"

    records = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    # Pick 20 balanced cases: 10 goal_following (5 seen, 5 novel) + 10 explicit_rule (5 seen, 5 novel)
    selected = []
    counts = {"gf_seen": 0, "gf_novel": 0, "er_seen": 0, "er_novel": 0}
    for r in records:
        tf = r.get("task_family")
        tpl = r.get("template_family")
        key = f"{'gf' if tf == 'goal_following' else 'er'}_{tpl}"
        if key in counts and counts[key] < 5:
            selected.append(r)
            counts[key] += 1
        if len(selected) >= 20:
            break

    print(f"Selected {len(selected)} balanced test cases from {input_file}.")
    engine = GLiClassEngine(model_id=model_id)

    orig_correct = 0
    perm_correct = 0
    match_count = 0

    rng = random.Random(20260918)

    for r in selected:
        target = r["target"]["choice_id"]

        # 1. Original order
        req_orig = ChoiceRequest.from_dict(r)
        resp_orig = engine.predict(req_orig)
        pred_orig = resp_orig.best_candidate_id
        if pred_orig == target:
            orig_correct += 1

        # 2. Permuted order (reversed or shuffled)
        r_perm = dict(r)
        choices_perm = list(r["choices"])
        choices_perm.reverse()  # complete reversal
        r_perm["choices"] = choices_perm
        req_perm = ChoiceRequest.from_dict(r_perm)
        resp_perm = engine.predict(req_perm)
        pred_perm = resp_perm.best_candidate_id
        if pred_perm == target:
            perm_correct += 1

        if pred_orig == pred_perm:
            match_count += 1

    n = len(selected)
    print("\n--- Permutation Sensitivity Results (20 cases) ---")
    print(f"Original Order Accuracy:   {orig_correct}/{n} ({orig_correct/n*100:.1f}%)")
    print(f"Reversed Order Accuracy:   {perm_correct}/{n} ({perm_correct/n*100:.1f}%)")
    print(f"Prediction Match Rate:     {match_count}/{n} ({match_count/n*100:.1f}%)")

    summary = {
        "dataset": input_file,
        "sample_count": n,
        "original_accuracy": orig_correct / n,
        "permuted_accuracy": perm_correct / n,
        "prediction_match_rate": match_count / n,
    }
    with open("runs/m3_1/permutation_test.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print("Saved results to runs/m3_1/permutation_test.json")

if __name__ == "__main__":
    main()
