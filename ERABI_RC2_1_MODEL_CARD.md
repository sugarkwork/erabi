# ERABI Release Candidate 2.1 Model Card

**Model Identifier**: `ERABI-RC2.1`  
**Architecture**: GLiClass Cross-Encoder Sequence Classifier  
**Base Model Backbone**: GLiClass Japanese (adapted for variable-choice behavioral inference)  
**Release Date**: 2026-09-21  
**Status**: Frozen Release Candidate (RC2.1)

---

## 1. Model Overview

ERABI (Evaluation and Ranking Analysis for Behavioral Inference) is a lightweight, high-performance local decision engine designed to evaluate structured contexts, questions, and variable candidate choices ($K \in [2, 16]$) and return mathematically rigorous, calibrated probability distributions across all options.

ERABI RC2.1 incorporates expanded training data (3,766 unique records across 8 families), post-hoc scalar temperature calibration ($T^* = 2.772176$), and an optimized ONNX Runtime FP16 CUDA deployment artifact.

---

## 2. Model Assets & Cryptographic Hashes

All release artifacts are packaged, frozen, and cryptographically verified:

| Asset Name | Filesystem Path | Format | SHA256 Checksum |
|:---|:---|:---:|:---|
| **PyTorch Checkpoint** | `release/rc2_1/model/model.safetensors` | SafeTensors (FP32) | `0951b356db1c72527826adeffe5fc24e8fb8a4360ac1e780df3e06cefb78d02b` |
| **Model Configuration** | `release/rc2_1/model/config.json` | JSON | `30031aeabbfcbd04bd6211903d5779ec31de10af157f1bfb49ab36344b41111d` |
| **Tokenizer Model** | `release/rc2_1/model/tokenizer.json` | JSON | `ac84fa7889747f37393545a7fc14ce4f1f158b33460318cad93531e0aa8db109` |
| **Temperature Calibration** | `release/rc2_1/calibration.json` | JSON ($T^*=2.772176$) | `0951b356...` (bound to weights) |
| **ONNX FP16 Runtime** | `release/erabi-rc2_1-onnx-fp16/model.onnx` | ONNX (FP16 CUDA) | `09b68c58a529367c3b24f54e1fb56891eb3ae52f9e4228946f041ff919eb793a` |

---

## 3. Input / Output Contract

### 3.1 Input Schema (`ChoiceRequest`)
- `context` (str): Grounding situation description or system telemetry.
- `question` (str): Explicit inquiry, decision prompt, or policy application request.
- `choices` (List[ChoiceInput]): 2 to 16 structured candidates, each with an ASCII identifier (`id`) and textual label (`text`).
- **Token Contract**: Total sequence length must be $\le 450$ tokens ($\le 512$ hard token ceiling). No silent truncation is permitted.

### 3.2 Output Schema (`ChoiceResponse`)
- `best_candidate_id` (str): Argmax prediction ID.
- `probabilities` (Dict[str, float]): Normalized softmax probabilities across all active choices, scaled by calibrated temperature $T^* = 2.772176$:
  $$\sum_{i=1}^K p_i = 1.0, \quad p_i > 0$$
- `raw_logits` (List[float]): Unscaled logits directly from the model forward pass.

---

## 4. Empirical Benchmark Performance

### 4.1 Development Gate Evaluation (Fresh In-Distribution Suite, $N=800$)
- **Overall Accuracy**: **92.37%** (739 / 800) [Gate: $\ge 88.0\%$ — **PASS**]
- **Logical Operators**: **86.00%** (172 / 200) [Gate: $\ge 85.0\%$ — **PASS**]
- **Natural Japanese**: **99.00%** (198 / 200) [Gate: $\ge 85.0\%$ — **PASS**]
- **Perturbation Invariance**: **95.63%** (153 / 160) [Gate: $\ge 90.0\%$ — **PASS**]
- **General Choice**: **90.62%** (145 / 160) [Gate: $\ge 85.0\%$ — **PASS**]
- **Variable Choice**: **88.75%** (71 / 80) [Gate: $\ge 85.0\%$ — **PASS**]
- **Critical Paired Reasoning**: **85.25%** (341 / 400 pairs) [Gate: $\ge 85.0\%$ — **PASS**]
- **Candidate Permutation Consistency**: **99.25%** [Gate: $\ge 95.0\%$ — **PASS**]
- **Regression Retention**: `eval_v2` = **96.50%**, `eval_exception` = **100.00%** [**PASS**]

### 4.2 Blind Sealed Acceptance Audit v4 (Completely Held-Out, $N=480$)
- **Overall Accuracy**: **74.17%** (PyTorch & ONNX FP16, **100.0% Parity**)
- **Strong Domains**:
  - `domain_transfer`: **95.00%** (57 / 60)
  - `priority_exception`: **91.67%** (55 / 60)
  - `natural_japanese`: **90.00%** (54 / 60)
  - `core_rules`: **81.67%** (49 / 60)
- **Challenged Domains**:
  - `variable_choice`: **63.33%** (38 / 60)
  - `general_choice`: **60.00%** (36 / 60)
  - `perturbation_invariance`: **56.67%** (34 / 60)
  - `logical_operators`: **55.00%** (33 / 60)
- **Critical Paired Reasoning**: **57.08%** (137 / 240 pairs)

---

## 5. Runtime & Hardware Efficiency

Tested on NVIDIA GeForce RTX 3060 (12GB VRAM, CUDA 12.8, Driver 572.70):

| Engine Configuration | Cold Start (ms) | Warm $p50$ (ms) | Warm $p95$ (ms) | Throughput (req/s) |
|:---|:---:|:---:|:---:|:---:|
| **PyTorch FP32 (CUDA)** | 37.31 | 19.39 | 33.50 | 46.6 |
| **ONNX Runtime FP32 (CUDA)** | 10.99 | 9.26 | 19.89 | 87.9 |
| **ONNX Runtime FP16 (CUDA)** | 21.57 | **11.13** | **16.44** | **77.6** |

- **Memory Leak Audit**: 1,000 continuous forward inference requests resulted in $+1.53$ MB memory drift (threshold: $< 50$ MB) — **PASSED**.
- **PyTorch $\leftrightarrow$ ONNX Parity**: **100.0% (800 / 800 on fresh, 480 / 480 on blind)**.

---

## 6. Intended Use & Deployment Guidelines

### Recommended Use Cases
- Rule-based operational dispatch and routing (e.g. facility alarms, telemetry alerts, SOP branching).
- Natural Japanese polite intent classification, customer inquiry routing, and document genre determination.
- Structured multi-choice decisions where choice cardinality $K \le 8$.

### Limitations & Out-of-Scope Usage
- **High-Cardinality Choices ($K \ge 12$)**: Cross-attention dilution can degrade performance on fine-grained distractor sets.
- **Complex Propositional Calculus**: Multi-clause Boolean equations with negation and exclusive-or should be pre-parsed or supplemented by symbolic logic engines.
- **Open-Ended Text Generation**: ERABI is strictly a discriminative choice-ranking model, not an autoregressive text generator.
- **Human-in-the-Loop Safeguard**: Automated downstream execution should mandate human review whenever calibrated target probability $p < 0.90$.
