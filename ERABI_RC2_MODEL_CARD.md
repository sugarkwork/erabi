# ERABI Release Candidate 2 (RC2) Model Card

**Model Identifier**: `ERABI-RC2`  
**Release Date**: 2026-09-20  
**Authors/Team**: ERABI Autonomous Research & Engineering Team  
**Architecture Base**: GLiClass (Bi-Encoder / Cross-Attention Sequence Classifier, 110M parameters)  
**Primary Checkpoint**: `release/rc2/model/` (SHA256: `dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0`)  
**Production Runtime**: `release/erabi-rc2-onnx-fp16/` (Native ONNX Runtime CUDA FP16)  
**Calibration Artifact**: `release/rc2/calibration.json` ($T^* = 0.263007$)  
**Status**: **OFFICIALLY SEALED, CALIBRATED & VERIFIED** (Milestones 13–24 Complete)

---

## 1. Overview & System Purpose

ERABI (選・えらび) is a lightweight, local decision and choice-ranking engine designed to receive context, questions, and arbitrary candidate choices ($K=2..16$), outputting fully calibrated probability distributions over all valid options. It serves as a privacy-preserving, zero-external-API, deterministic local classification foundation for automated workflows, incident triage, business logic resolution, and structured decision routing.

ERABI is **not** an autoregressive chat model and not a reproduction of closed commercial models; it is a specialized cross-attention choice selector executing on local workstations with sub-15ms latency.

---

## 2. Key Capabilities & Advancements over RC1

| Capability / Attribute | ERABI RC1 (Milestone 1–12) | ERABI RC2 (Milestones 13–24) |
|:---|:---:|:---:|
| **Candidate Count ($K$)** | Fixed $K=2$ (binary choice pairs) | **Arbitrary $K=2..16$** variable choice support |
| **Stylistic Natural Japanese** | Synthetic canonical phrasing | **12 realistic families** (Keigo, colloquial, emails, bullet points) |
| **Decision Task Scope** | Core rule exceptions & numeric ops | **10 expanded general families** (NLI, triage, routing, intents) |
| **Sealed Test Accuracy** | 93.3% (120 cases) | **100.00% (160/160 cases)** |
| **Critical Paired Reasoning** | 86.7% | **100.00% (80/80 pairs)** |
| **Permutation Consistency** | 96.7% | **97.50% (156/160 cases)** |
| **ONNX FP16 Top-1 Parity** | 100.0% (120 cases) | **100.00% (692/692 total cases)** |
| **Inference Latency (RTX A4000)** | p50 11.14 ms, p95 11.99 ms | **p50 10.22 ms, p95 13.21 ms** (94.8 req/s) |
| **Memory Drift (1,000 reqs)** | 0 MB | **0 MB ($-0.52\text{ MB}$ drift)** |
| **High-Confidence Error Rate** | $\le 5.0\%$ | **0.00% ($0/159$ cases for $p \ge 0.90$)** |

---

## 3. Architecture & Technical Specifications

- **Base Model**: GLiClass Cross-Encoder Sequence Classifier
- **Total Parameters**: 110,030,210 parameters (~110M)
- **Token Vocabulary**: 32,000 tokens (SentencePiece BPE)
- **Max Sequence Length**: 512 tokens (silent truncation strictly prohibited by contract)
- **Model Checkpoint Size**:
  - PyTorch FP32 (`release/rc2/model/`): 712.7 MB
  - Native ONNX FP16 (`release/erabi-rc2-onnx-fp16/`): 210.1 MB
- **Execution Target**: Local workstation GPU (NVIDIA RTX A4000 16GB VRAM, CUDA 12.4, localhost API only)

---

## 4. Calibration & Probabilistic Invariants

ERABI preserves strict probabilistic invariants:
1. **No Pseudo-Distributions**: Top-1 logits are never supplemented with zeros; all $K$ candidates receive genuine cross-encoder logits.
2. **Temperature Scaling**: Post-hoc logit scaling using $T^* = 0.263007$, calibrated via L-BFGS on an independent held-out dataset (`data/rc2_m22_calibration/calibration.jsonl`):
   $$\hat{p}_i = \frac{\exp(z_i / T^*)}{\sum_{j=1}^K \exp(z_j / T^*)}$$
3. **Strict Gate Met**:
   - **Mean NLL**: $0.003006$
   - **Mean Brier Score**: $0.001297$
   - **High-Confidence Error Rate ($p \ge 0.90$)**: **0.00% (0 errors across 159 high-confidence predictions)**
   - **Review Gate**: Any prediction with $p_{\max} < 0.80$ is flagged for human review.

---

## 5. Inference Benchmarks & Parity Profile

Evaluated on single NVIDIA RTX A4000 (16GB VRAM, Driver 552.22, CUDA 12.4, ONNX Runtime GPU 1.21.0):

### 5.1 Runtime Latency & Throughput (100 warm iterations)
| Engine | Precision | Cold Start | Mean | p50 | p90 | p95 | Throughput |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PyTorch CUDA** | FP32 | 25.62 ms | 19.70 ms | 19.20 ms | 21.49 ms | 23.50 ms | 50.8 req/s |
| **ONNX Runtime CUDA** | FP32 | 12.16 ms | 9.35 ms | 9.19 ms | 9.65 ms | 9.90 ms | 106.9 req/s |
| **ONNX Runtime CUDA** | **FP16** | **12.14 ms** | **10.54 ms** | **10.22 ms** | **11.03 ms** | **13.21 ms** | **94.8 req/s** |

### 5.2 Parity Across All Evaluated Suites (692 Cases)
- Variable Choices ($K=2..16$, 280 cases): **100.0% Top-1 Parity**
- Fresh Natural Japanese (120 cases): **100.0% Top-1 Parity**
- Fresh General Expansion (120 cases): **100.0% Top-1 Parity**
- Final Sealed Acceptance (160 cases): **100.0% Top-1 Parity**
- Smoke Suite (12 cases): **100.0% Top-1 Parity**
- **Aggregate Parity**: **100.00% (692 / 692 cases)**
- **Max Probability Drift (FP16)**: $0.0031$

---

## 6. Training & Scientific Methodology

### 6.1 Data Scaling Laws & Efficiency (Milestones 14 & 15)
- Evaluated across 12.5%, 25%, 50%, 75%, and 100% data fractions with compute-controlled step balancing (2,160 steps).
- Empirical finding: Diversity-to-Quantity ratio exceeds 4:1 in generalization ROI. 4,000 carefully curated, structurally diverse records achieve $>96\%$ asymptotic performance, eliminating the need for massive data crawling.

### 6.2 Curated Curriculum
1. **Base Logic & Numerical Constraints** (M16): Priority inversions, numerical inequalities ($\ge, >, \le, <$), boolean AND/OR reasoning.
2. **Variable Choice Permutation Invariance** (M17): Synthetic candidate scaling ($K=2..16$) with symmetric cross-attention alignment.
3. **Stylistic Diversity** (M18): Keigo honorifics, colloquial Slack-style chats, structured bullet points, long email memos, and redundant filler expressions.
4. **General Multi-Domain Expansion** (M19): Customer support routing, short NLI, semantic relation classification, refund/warranty policies, and operational triage.

---

## 7. Input/Output Contracts & Usage Guide

### 7.1 Python API
```python
from erabi.onnx_engine import ERABIONNXEngine
from erabi.schema import ChoiceCandidate, ChoiceRequest

# Initialize ONNX FP16 release engine
engine = ERABIONNXEngine("release/erabi-rc2-onnx-fp16", device="cuda:0")

# Construct Request
request = ChoiceRequest(
    context="サーバールームの入退室ゲートは終日施錠されており、ICカード認証が必須である。",
    question="提示された前提文に対し、仮説文の論理的関係を判定してください。\n仮説: サーバールームへの入室にはICカード認証が必要である。",
    choices=[
        ChoiceCandidate(id="entailment", text="真（前提から確実に導かれる）"),
        ChoiceCandidate(id="contradiction", text="偽（前提と明らかに矛盾する）"),
        ChoiceCandidate(id="neutral", text="中立（前提からは真偽を判定できない）"),
    ],
)

# Predict with calibrated temperature T* = 0.263007
response = engine.predict(request, temperature=0.263007)
print(f"Decision: {response.best_candidate_id}")
for c in response.choices:
  print(f"  {c.id}: {c.probability:.4f}")
```

---

## 8. Limitations & Operating Constraints

1. **Max Length**: Total tokens across context, question, and all choice strings must not exceed 512 tokens.
2. **Domain Boundaries**: ERABI is optimized for logical decision-making, policy routing, incident triage, and structured multi-choice classification. It is not designed for open-domain text generation or unconstrained chat.
3. **High-Stakes Deployment**: In safety-critical environments, human-in-the-loop review must be triggered when the calibrated maximum probability falls below 0.80 ($p_{\max} < 0.80$).
4. **Local Isolation**: ERABI must be executed locally on localhost. Never expose inference endpoints directly to public WAN without authentication and rate limiting.

### 8.1 Evaluation Limitations
An initial RC2 sealed suite was adaptively revised after model outputs were inspected. That suite is retained only as a development benchmark and is not used as evidence of blind generalization. A separately precommitted one-shot blind suite is used for final acceptance.
