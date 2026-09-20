import json
from pathlib import Path

with open("runs/rc2_1_run3b/dev_gate_results.json", encoding="utf-8") as f:
    d = json.load(f)

cases = d["fresh_suite_summary"]["cases"]
failed = [c for c in cases if not c["correct"]]
print(f"Total failed: {len(failed)} / {len(cases)}")

by_fam = {}
for c in failed:
    by_fam.setdefault(c["family"], []).append(c)

for f, fcases in sorted(by_fam.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {f:25s}: {len(fcases):2d} failed ({len(fcases)/(200 if 'natural' in f or 'logical' in f else (160 if 'general' in f or 'perturb' in f else 80))*100:.1f}% error)")

print("\n--- Logical Operators Failures ---")
op_failed = by_fam.get("logical_operators", [])
s1_fail = sum(1 for c in op_failed if c["id"].endswith("_s1"))
s2_fail = sum(1 for c in op_failed if c["id"].endswith("_s2"))
print(f"s1 failed: {s1_fail}, s2 failed: {s2_fail}")

# Group by group_id
groups = {}
for c in [c for c in cases if c["family"] == "logical_operators"]:
    groups.setdefault(c["group_id"], []).append(c)

both_wrong = 0
one_wrong = 0
both_right = 0
for gid, gcases in groups.items():
    if len(gcases) == 2:
        c1, c2 = gcases[0], gcases[1]
        if not c1["correct"] and not c2["correct"]:
            both_wrong += 1
        elif not c1["correct"] or not c2["correct"]:
            one_wrong += 1
        else:
            both_right += 1

print(f"Groups total: {len(groups)}, Both right: {both_right}, One wrong: {one_wrong}, Both wrong: {both_wrong}")

with open("scripts/scratch/diag_other_failures.txt", "w", encoding="utf-8") as out_f:
    out_f.write("=== General Choice Failures ===\n")
    gen_failed = [c for c in failed if c["family"] == "general_choice"]
    for c in gen_failed[:15]:
        out_f.write(f"ID: {c['id']}, Target: {c['target']}, Pred: {c['pred']}, p_pred: {c['p_pred']:.3f}\n")

    out_f.write("\n=== Perturbation Invariance Failures ===\n")
    pert_failed = [c for c in failed if c["family"] == "perturbation_invariance"]
    for c in pert_failed[:15]:
        out_f.write(f"ID: {c['id']}, Target: {c['target']}, Pred: {c['pred']}, p_pred: {c['p_pred']:.3f}\n")




