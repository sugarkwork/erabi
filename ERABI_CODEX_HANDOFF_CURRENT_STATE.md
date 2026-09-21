# ERABI — Codex Handoff / Current Development State

**Date:** 2026-09-21  
**Purpose:** Handoff from Antigravity to Codex after the Antigravity usage limit was reached.  
**Primary instruction:** Continue development from the current state. Do **not** restart the project, re-run old milestones without cause, or overwrite frozen release artifacts.

---

# 1. Executive Summary

ERABI is a lightweight local **decision / choice reasoning engine**.

The intended interface is roughly:

```text
Input:
- context
- question / instruction
- arbitrary candidate choices

Output:
- probability for each candidate
- top choice
- optional review / calibration metadata
```

The project is inspired by a **Jev-like / System One local choice engine**: fast, local, non-generative, and suitable for routing, policy/priority decisions, lightweight reasoning, and agent pre-routing.

The project has already progressed through:

- data correctness / semantic validation
- leakage audits
- goal switching
- exception / priority rules
- operator generalization
- domain / perturbation robustness
- variable candidate counts
- natural Japanese robustness
- calibration
- ONNX FP16 export
- blind acceptance testing
- architecture diagnostics
- scale-up from ~200M to ~438M parameters

The current best RC3 model is **not yet accepted as final**.

It performs well on most task families, but the latest truly blind test (`Blind v5`) failed primarily because of **logical operator generalization**.

The next planned phase is **RC3.1 Logic Recovery**, not a full redesign.

---

# 2. Repository / Working Directory

Local project root:

```text
f:/ai/erabi-local
```

Historical public repository:

```text
sugarkwork/erabi-local
```

The user has explicitly requested that the repository be renamed to:

```text
sugarkwork/erabi
```

Target URL:

```text
https://github.com/sugarkwork/erabi
```

This rename is **pending** unless already completed after this handoff was written.

After renaming:

```bash
git remote set-url origin https://github.com/sugarkwork/erabi.git
```

Search the repository for stale references to:

```text
erabi-local
github.com/sugarkwork/erabi-local
```

and update README, docs, manifests, badges, CI, clone examples, release metadata, etc.

Do not create a second replacement repository if rename permission is unavailable. Report the permission problem instead.

---

# 3. Licensing Decision

The user decided:

> **ERABI original source code should use the MIT License.**

Required repository maintenance:

- add root `LICENSE` with the standard MIT License
- use year `2026`
- update `pyproject.toml` to identify MIT licensing
- add a License section to README
- preserve upstream / third-party licenses

Important distinction:

```text
ERABI original source code
→ MIT

GLiClass / upstream models / DeBERTa / pretrained tokenizers / other dependencies
→ retain their original upstream licenses
```

Do **not** relicense third-party components as MIT.

Create `THIRD_PARTY_LICENSES.md` or `THIRD_PARTY_NOTICES.md` if useful.

This repository/licensing work should be done in a separate commit from ML changes.

---

# 4. Runtime / Hardware Context

Primary recent development machine:

```text
GPU: NVIDIA RTX A4000 16GB
CPU: Ryzen 7 5800X
RAM: 96GB
OS: Windows 11
```

The project has successfully trained and exported both ~200M and ~438M GLiClass-family models on this hardware.

---

# 5. Current Architecture

Current RC3 backbone:

```text
knowledgator/gliclass-instruct-large-v1.0
```

Approximate parameter count:

```text
438M
```

Architecture retained:

```text
All-in-One Sequence Cross-Encoder
```

A candidate-separated scoring architecture was tested and rejected because it was worse and slower, including worse high-K behavior.

Do not switch to candidate-separated scoring unless new evidence justifies revisiting it.

---

# 6. Frozen Model / Release Lineage

Important frozen lines:

```text
RC1
RC2
RC2.1
RC3
```

Do not overwrite previous release artifacts.

Relevant release directories include:

```text
release/rc2_1/
release/erabi-rc2_1-onnx-fp16/

release/rc3/
release/rc3/model/
release/erabi-rc3-onnx-fp16/
```

The current RC3 release is a **failed final acceptance candidate**, not the final accepted product.

---

# 7. Why RC3 Exists

RC2.1 performed very well on development-facing fresh benchmarks but failed a truly blind benchmark.

RC2.1 Blind v4 result:

```text
Overall: 74.17%
Paired Both: 57.08%
Permutation: 93.54%
```

Major failures included:

```text
logical_operators
perturbation_invariance
variable_choice
general_choice
```

This exposed a major gap between development benchmarks and true unseen-distribution performance.

That triggered the RC3 diagnostic-first roadmap.

---

# 8. Important RC3 Diagnostic Findings

## 8.1 Development benchmark != blind benchmark

The old Research Fresh suite was repeatedly used for:

- error analysis
- data additions
- checkpoint selection
- iterative development

Therefore it became a **development benchmark**, not an unbiased blind benchmark.

## 8.2 Blind v4 was retired

Blind v4 became a:

```text
Retired Diagnostic Benchmark
```

It may be used for aggregate failure analysis, but must not be used for training, checkpoint selection, or final acceptance re-testing.

## 8.3 Candidate-separated scoring was tested and rejected

Milestone 29 A/B comparison:

```text
Condition A: All-in-One Cross-Encoder
Condition B: Candidate-Separated Scoring
```

Condition B was materially worse and slower.

Conclusion:

```text
Keep All-in-One Cross-Encoder.
```

## 8.4 RC3 Bridge benchmark bug was found and fixed

A serious evaluation data bug was discovered in the RC3 Bridge `logical_operators` family.

In many K=2 cases, the question described actions that did not match the provided choices, making some examples unanswerable / mislabeled.

The benchmark generator was corrected and the Bridge benchmark regenerated.

Earlier Bridge numbers before this fix are not the clean final reference.

---

# 9. 200M-Class RC3 Attempts

Best clean ~200M RC3 development result after benchmark repair / curriculum work was approximately:

```text
Bridge Overall: 81.87%
Paired Both: 66.25%
logical_operators: 73.33%
variable_choice: 90.00%
core_rules: 86.67%
perturbation_invariance: 85.00%
permutation: 96.67%
mean core retention: 98.00%
```

This improved substantially but still missed the RC3 development target.

After the allowed training budget was exhausted, the project moved to a larger compatible backbone.

---

# 10. 438M Backbone Scale-Up

Selected model:

```text
knowledgator/gliclass-instruct-large-v1.0
```

Reported parameter count:

```text
438,672,897
```

The untreated large model was near chance on the project tasks, confirming that project performance came from ERABI training rather than pre-existing task memorization.

Large-model training included:

```text
AdamW
FP16 AMP
effective batch size = 16
cosine LR schedule
```

The larger backbone substantially improved difficult families while keeping the All-in-One architecture.

---

# 11. SWA / Gentle Fine-Tuning

A strong SWA checkpoint reached approximately:

```text
Bridge Overall: 87.92%
logical_operators: 86.67%
core_rules: 90.00%
natural_japanese: 90.00%
perturbation_invariance: 95.00%
variable_choice: 88.33%
domain_transfer: 95.00%
Permutation: 97.50%
Mean Core Retention: 98.70%
```

Further gentle fine-tuning produced the winning RC3 checkpoint around:

```text
Bridge Overall: 88.75%
Paired Both: 80.42%
logical_operators: 90.00%
Mean Core Retention: 98.70%
```

That checkpoint was frozen into:

```text
release/rc3/model
```

---

# 12. RC3 Size / Speed

Frozen RC3 PyTorch weights:

```text
~1.75 GB
```

RC3 ONNX FP16 package:

```text
~838.76 MB
```

Measured ONNX FP16 CUDA latency on RTX A4000:

```text
p50 ≈ 24.63 ms
```

PyTorch ↔ ONNX FP16 Top-1 parity:

```text
100%
```

The runtime target was met.

---

# 13. RC3 Calibration

RC3 calibration was performed after model freeze.

Reported temperature:

```text
T* ≈ 2.6440
```

If RC3.1 changes weights, produce a new calibration artifact. Do not reuse RC3's temperature.

---

# 14. Latest Final Acceptance: Blind v5

This is the most important current-state result.

Blind v5:

```text
480 cases
240 contrastive pairs
zero historical leakage
programmatic semantic/schema audit passed
```

Frozen RC3 results:

```text
Overall: 409 / 480 = 85.21%
ONNX FP16: 409 / 480 = 85.21%
PyTorch ↔ ONNX: 100% Top-1 parity
Paired Both: 179 / 240 = 74.58%
Permutation: 96.46%
High-confidence error (p >= 0.90): 6.57%
```

Family results:

```text
general_choice          95.00%
natural_japanese        93.33%
priority_exception      91.67%
perturbation_invariance 85.00%
variable_choice         85.00%
core_rules              83.33%
domain_transfer         81.67%
logical_operators       66.67%
```

The clearly dominant failing family is:

```text
logical_operators
```

Formal result:

```text
FAILED
```

Do not relabel RC3 as accepted.

---

# 15. Blind v5 Failure Interpretation

Seven of eight families are already in the 81.67–95.00% range.

The main weakness is formal logic:

- XOR
- NAND
- NOR
- negation
- compound negation
- nested propositions
- polarity reversal
- exact truth-state switching

The model sometimes appears to fall back to lexical similarity rather than strict propositional logic.

This is why the next phase should be narrow and targeted rather than a complete redesign.

---

# 16. Arithmetic for the Next Phase

Current overall:

```text
409 / 480 = 85.21%
```

To exceed an 88% gate, the minimum passing count is:

```text
423 / 480 = 88.125%
```

Needed improvement:

```text
+14 correct cases
```

If all improvement comes only from `logical_operators`:

```text
40 / 60 → 54 / 60 = 90.0%
```

Therefore the next internal development target for logical operators should be:

```text
>= 90%
```

not merely 80–85%.

---

# 17. What Codex Should Do Next

Next phase:

```text
ERABI RC3.1 — Logic Recovery
```

Do **not** immediately move to an 8B model.

Do **not** redesign the whole architecture yet.

Keep:

```text
438M backbone
All-in-One Cross-Encoder
existing API/input contract
ONNX FP16 release path
```

Focus narrowly on formal logic generalization.

---

# 18. Blind v5 Must Be Retired

Blind v5 has now been inspected.

Therefore:

```text
Blind v5 = Retired Diagnostic Benchmark
```

Allowed:

- aggregate failure category analysis
- operator-type statistics
- confidence analysis
- K / token-length / nesting / negation analysis

Not allowed:

- copying Blind v5 examples into training
- making number-swapped near-copies
- checkpoint selection on Blind v5
- re-running Blind v5 as the final acceptance test after tuning

The next final acceptance must use a completely new:

```text
Blind v6
```

---

# 19. RC3.1 Logic Recovery Dataset

Create independent training data with new domains, wording, numerical states, semantic states, and templates.

Do not copy Blind v5.

Required logical families:

```text
AND
OR
XOR
NAND
NOR
NOT
implication / conditional
double negation
polarity reversal
nested logic
```

Required truth-state coverage:

```text
XOR: FF / FT / TF / TT
NAND / NOR: all truth states
Negation: A / NOT A / NOT NOT A / A AND NOT B / NOT A OR B
Nested:
(A AND B) OR C
A AND (B OR C)
NOT(A AND B)
NOT(A OR B)
(A XOR B) AND C
```

Start with nesting depth <= 2.

Use at least ~12 domains and do not bind one operator to one domain.

---

# 20. New Logic Bridge Benchmark

Create:

```text
data/rc3_1_logic_bridge/
```

Target size:

```text
320–480 cases
160–240 contrastive pairs
```

Include:

- unseen domains
- unseen phrasing
- XOR/NAND/NOR
- double negation
- nested logic
- K=2,3,4,6
- lexical-overlap distractors
- implicit fallback
- reordered clauses

Integrity requirements:

```text
semantic mismatch = 0
exact train overlap = 0
Blind v5 exact overlap = 0
choice-position balance
target balance
token limit compliance
independent semantic validator
```

---

# 21. RC3.1 Training Budget

Base:

```text
release/rc3/model
```

Prefer continual fine-tuning.

Maximum:

```text
2 full training runs
```

One primary variable per run.

Suggested Run 1:

```text
RC3 historical curriculum
+
new logic recovery dataset
+
task-balanced sampling
+
low LR
+
1–2 epochs
```

Only run a second experiment if the first misses the development gate.

---

# 22. RC3.1 Development Gates

## Logic Bridge

```text
Overall >= 90%
XOR >= 85%
NAND >= 85%
NOR >= 85%
NOT/negation >= 90%
nested logic >= 85%
Paired Both >= 85%
```

## Existing RC3 Bridge

```text
Overall >= 88%
logical_operators >= 90%
general_choice >= 85%
priority_exception >= 85%
variable_choice >= 85%
perturbation >= 85%
natural_japanese >= 90%
permutation >= 95%
```

## Retention

```text
mean core retention >= 96%
```

Do not use Blind v5 for model selection.

---

# 23. RC3.1 Calibration / Export

After RC3.1 weights are frozen:

1. build new calibration data
2. fit a new temperature
3. do not reuse RC3 `T*=2.6440`
4. export:

```text
PyTorch
→ ONNX FP32
→ ONNX FP16 CUDA
```

Required:

```text
Top-1 parity = 100%
K=2..16 support
calibration parity
no significant probability drift
1000-request memory stability
```

Runtime target:

```text
p50 <= 27 ms
p95 <= 45 ms
```

---

# 24. Final Acceptance: Blind v6

Only after RC3.1 model / calibration / ONNX are frozen.

Create a fully new Blind v6.

Do not reuse Blind v5 templates directly.

Gate:

```text
Overall >= 88%
logical_operators >= 80%
no major family < 75%
Paired Both >= 75%
Permutation >= 95%
high-confidence error <= 7%
PyTorch ↔ ONNX parity = 100%
semantic errors = 0
leakage = 0
```

Blind v6 should be used once.

If it fails, retire it and use Blind v7 next. Do not tune against Blind v6 and re-run it as final acceptance.

---

# 25. When to Consider a Larger / Different Model

Do not jump to 8B yet.

Only consider larger / different backends if RC3.1 shows that:

- logic bridge remains <90%
- XOR/NAND/NOR/nested logic do not improve
- both allowed full-training runs fail
- retention tradeoff cannot be resolved

---

# 26. Known Data / Evaluation Pitfalls

These bugs have happened before. Codex must actively defend against them.

## Semantic label inversion

Never trust generator metadata alone. Independently derive expected targets from rendered text.

## Exact / semantic leakage

Audit:

- exact model input
- group IDs
- context
- normalized semantic state
- structural template overlap when relevant

## Shortcut text in choices

Bad:

```text
Because condition X is met, continue operation
```

Good:

```text
Continue operation
```

## Joke / obviously wrong distractors

Use plausible domain-specific alternatives.

## Position bias

Shuffle candidate order during training and measure permutation consistency separately.

## Evaluation-set bug

Audit:

```text
question actions ↔ choice texts ↔ target
```

before trusting benchmark results.

## Dev benchmark overuse

Any benchmark repeatedly used for diagnosis / data additions / checkpoint selection is a development benchmark, not a blind benchmark.

---

# 27. Important Data Areas

```text
data/m3_3_v2/
data/m4_1_exception/
data/m4_3_1_phrasing_fix/
data/m6_operator/
data/m7_robustness/
data/m8_general_choice/

data/rc2_1_train/
data/rc2_1_research_fresh/

data/rc3_train/
data/rc3_bridge/

data/sealed_acceptance_rc3_blind_v5/
```

Do not casually delete or regenerate old accepted / retired benchmark artifacts.

---

# 28. Important Recent Scripts

Representative scripts:

```text
scripts/train_rc3.py
scripts/train_rc3_continual.py
scripts/train_rc3_large.py
scripts/train_rc3_large_gentle.py

scripts/calibrate_rc3.py
scripts/export_rc3_onnx.py

scripts/build_rc3_bridge_benchmark.py
scripts/build_rc3_train_data.py
scripts/build_rc3_blind_v5.py
scripts/run_rc3_blind_v5_acceptance.py
```

RC3 training-data generators:

```text
scripts/rc3_train_data/
```

Bridge generators:

```text
scripts/rc3_bridge_data/
```

Blind v5 generators:

```text
scripts/rc3_blind_v5_data/
```

Treat Blind v5 generators as retired evaluation assets, not training sources.

---

# 29. Codex Autonomy Rules

Do not ask the user for approval after every small step.

Proceed autonomously through:

```text
inspect
→ diagnose
→ pre-register hypothesis
→ build minimal experiment
→ audit data
→ train
→ recompute metrics from saved logits/predictions
→ self-review
→ decide next action
```

Stop and ask the user only if:

1. repository rename permission is unavailable
2. a serious third-party license issue is found
3. 2 RC3.1 full-training runs fail the development gate
4. architecture change is required
5. 8B-class backend should be considered
6. Blind v6 is completed
7. a major data/evaluation bug is discovered
8. destructive overwrite of frozen release artifacts would be required

---

# 30. Immediate Codex To-Do List

## A. Repository maintenance

1. rename GitHub repo: `erabi-local` → `erabi`
2. update local remote
3. add MIT `LICENSE`
4. update `pyproject.toml`
5. update README
6. preserve upstream licenses
7. create third-party license notice if needed
8. search/replace stale repo URLs

Keep this commit separate from ML work.

## B. RC3.1 preparation

1. verify RC3 and Blind v5 hashes / frozen state
2. mark Blind v5 as retired diagnostic
3. implement independent logic recovery generator
4. implement independent semantic validator
5. build logic bridge benchmark
6. run leakage / structural audits

## C. Training

1. run RC3.1 continual fine-tuning Run 1
2. evaluate development gates
3. if needed, run one more full-training experiment only

## D. Release candidate

If development gates pass:

1. freeze weights
2. new calibration
3. ONNX FP32 export
4. ONNX FP16 CUDA export
5. parity / latency / memory audit

## E. Final acceptance

1. create fully new Blind v6
2. pre-freeze / hash it
3. run one-shot acceptance
4. report result
5. stop and hand back to user

---

# 31. Do Not Do These

Do not:

- restart the project from RC1
- overwrite RC3 artifacts
- train on Blind v5
- re-use Blind v5 as final acceptance
- jump directly to 8B
- switch to candidate-separated scoring without new evidence
- treat RC3 as accepted
- lower the final gate to make the current model pass
- silently modify benchmark labels after seeing predictions
- use evaluation data as training data
- mix repository/license changes with model-training commits

---

# 32. Current One-Sentence Status

> **ERABI RC3 is a fast ~438M local choice engine with strong blind generalization on 7/8 task families and ONNX FP16 inference around 24.6 ms on RTX A4000, but it failed final Blind v5 acceptance at 85.21% overall because formal logical operator generalization remains the dominant bottleneck. The next phase is a narrowly scoped RC3.1 logic-recovery run followed by a completely new Blind v6 acceptance test.**

---

# 33. Suggested First Codex Internal Plan

```text
I will not restart ERABI.
I will treat RC1/RC2/RC2.1/RC3 and Blind v5 as frozen historical artifacts.
I will first perform repository maintenance (rename + MIT licensing) in a separate commit,
then implement RC3.1 logic recovery using independent new data and a new Logic Bridge,
without training on Blind v5.
I will use at most two full training runs.
If the development gate passes, I will recalibrate, export ONNX FP16,
and run exactly one new Blind v6 final acceptance.
```
