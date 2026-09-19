# ERABI Release Candidate 1 (RC1) Release Report

- **Version**: `RC-1.0.0`
- **Release Date**: 2026-09-19 23:18:49
- **Model Checkpoint**: `release/rc1/model/` (`W_general_v1`)
- **Calibration Artifact**: `release/rc1/calibration.json` ($T^* = 0.256$)

## Performance & Invariance Metrics (100 Warm Requests)
- **Latency p50**: **27.69 ms** [Target: <= 50 ms] -> **PASS**
- **Latency p95**: **45.44 ms** [Target: <= 100 ms] -> **PASS**
- **Latency Mean**: **32.08 ms**
- **Probability Sum**: $\sum p_i \approx 1.0$ (Max deviation: 0.00e+00) -> **PASS**
- **Raw Choice Order Preservation**: **True** -> **PASS**
- **Deterministic Inference**: **True** -> **PASS**
- **Memory RSS Delta**: **+0.19 MB** (No memory leak) -> **PASS**

## Model Accuracy & Generalization Summary
- **General Choice Tasks (`fresh_general_eval`)**: **100.0%** (120/120)
  - `support_routing`: 100.0%
  - `short_nli`: 100.0%
  - `semantic_relation`: 100.0%
  - `intent_selection`: 100.0%
  - `instruction_separation`: 100.0%
  - `negative_goal`: 100.0%
- **Domain & Perturbation Robustness (`fresh_robustness_eval`)**: **100.0%** (108/108)
  - All 9 domains: 100.0%
  - All 6 perturbation modes: 100.0%
  - Top-1 candidate permutation consistency: 100.0%
- **Logical Operators (`fresh_operator_eval`)**: **92.0%** (92/100)
- **Core Reasoning Retention (`eval_v2`)**: **97.5%** (195/200)
- **Exception Rules (`eval_exception`)**: **100.0%** (120/120)
- **Phrasing Generalization (`fresh_phrasing_eval`)**: **86.7%** (104/120)
- **Smoke Cases (`smoke_cases`)**: **10/12 (83.3%)**
