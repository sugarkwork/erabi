import json

with open("scripts/scratch/diag_op_rules.txt", "w", encoding="utf-8") as out_f:
    with open("data/rc2_1_research_fresh/research_fresh_eval.jsonl", encoding="utf-8") as f:

        for line in f:
            obj = json.loads(line)
            if obj["family"] == "logical_operators" and obj["id"].endswith("_s2") and int(obj["id"].split("_")[-2]) <= 10:
                out_f.write(f"=== {obj['id']} ===\n")
                out_f.write(f"Context: {obj['context']}\n")
                out_f.write(f"Question: {obj['question']}\n")
                out_f.write(f"Choices: {obj['choices']}\n")
                out_f.write(f"Target: {obj['target']}\n\n")

