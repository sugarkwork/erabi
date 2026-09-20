# ERABI Release Candidate 2.1 Calibration Report

**Milestone**: ERABI RC2.1 Temperature Calibration Audit  
**Date**: 2026-09-21  
**Target Model**: `release/rc2_1/model`  
**Model Weight SHA256**: `0951b356db1c72527826adeffe5fc24e8fb8a4360ac1e780df3e06cefb78d02b`  
**Calibration Artifact**: `release/rc2_1/calibration.json`  
**Status**: **ALL CALIBRATION GATES PASSED**

---

## 1. Executive Summary

In accordance with Section 17 of `ERABI_RC2_1_AUTONOMOUS_RECOVERY_ROADMAP.md` and `AGENTS.md`, post-hoc temperature calibration was conducted on the frozen ERABI RC2.1 model checkpoint (`release/rc2_1/model`).

The objective of calibration is to correct overconfidence in the raw uncalibrated logits without altering the top-1 discrete classification decisions or violating numerical invariants. A bounded scalar temperature scaling parameter $T^*$ was optimized over the independent, held-out calibration partition (`data/rc2_1_train/calibration.jsonl`).

### Key Results
- **Optimal Temperature**: $T^* = \mathbf{2.772176}$
- **Top-1 Prediction Invariance**: **100.00% (800 / 800)** (Identical argmax at $T=1.0$ and $T=T^*$)
- **Calibration NLL**: $0.016629 \to \mathbf{0.008222}$ (**-50.56% reduction**)
- **Fresh Suite NLL ($N=800$)**: $0.779094 \to \mathbf{0.309020}$ (**-60.34% reduction**)
- **Fresh Suite Brier Score**: $0.137610 \to \mathbf{0.122400}$ (**Non-worsening, -11.05% improvement**)
- **High-Confidence ($p \ge 0.90$) Error Rate**: Reduced from $5.82\%$ to $\mathbf{4.32\%}$ (meets target $\le 5.0\%$)
- **Cryptographic Binding**: Calibration parameter is strictly bound to model weights SHA256.

---

## 2. Calibration Methodology & Numerical Invariants

### 2.1 Temperature Scaling Formulation
Given candidate logits $\mathbf{z} = (z_1, z_2, \dots, z_K)$ for $K$ candidates and ground-truth index $y$, the calibrated candidate probabilities are defined as:

$$p_i(T) = \frac{\exp(z_i / T)}{\sum_{j=1}^K \exp(z_j / T)}$$

The optimal temperature $T^*$ is determined by minimizing the cross-entropy negative log-likelihood (NLL) on the held-out calibration dataset $\mathcal{D}_{\text{cal}}$:

$$\min_{T \in [0.05, 20.0]} \mathcal{L}(T) = -\frac{1}{|\mathcal{D}_{\text{cal}}|} \sum_{(z, y) \in \mathcal{D}_{\text{cal}}} \log \left( \frac{\exp(z_y / T)}{\sum_{j=1}^K \exp(z_j / T)} \right)$$

### 2.2 Invariant Guarantees
1. **Top-1 Order Invariance**: Because temperature scaling is a strictly monotonic transformation of logits for any $T > 0$, $\arg\max_i z_i = \arg\max_i (z_i / T)$. The top-1 predicted candidate is mathematically invariant.
2. **Zero Truncation / No Masking Distortion**: Active candidate masks are applied prior to softmax; padding candidates are excluded ($-\infty$ masked) to avoid $0 \times -\infty \to \text{NaN}$.
3. **No Double-Softmax**: Raw logits from GLiClass are preserved; calibration divides raw logits by $T^*$ once before single softmax normalization.

---

## 3. Optimization Trajectory

The optimization was performed using bounded Brent optimization (`scipy.optimize.minimize_scalar`) over $T \in [0.05, 20.0]$:

| Iteration / Step | Temperature ($T$) | Calibration NLL | Note |
|:---|:---:|:---:|:---|
| Initial ($T=1.0$) | 1.000000 | 0.016629 | Raw model output |
| Bracket Step 1 | 7.671360 | 0.011681 | Decreasing gradient |
| Bracket Step 2 | 2.597304 | 0.008249 | Near optimum |
| Intermediate | 2.766159 | 0.008222 | Refinement |
| **Converged ($T^*$)** | **2.772176** | **0.008222** | **Optimal minimum found** |

The optimal temperature $T^* = 2.772176$ lies well within the interior of the search space ($0.05 < T^* < 20.0$), indicating a smooth, well-conditioned convex objective.

---

## 4. Empirical Validation on Fresh Suite ($N=800$)

To evaluate the generalization of the calibrated temperature on out-of-sample data, the temperature $T^*$ was evaluated on the independent 800-case Research Fresh Evaluation Suite across 5 challenging families:

| Metric | Raw ($T=1.0$) | Calibrated ($T^*=2.772176$) | Delta / Change | Status |
|:---|:---:|:---:|:---:|:---:|
| **Overall Accuracy** | 92.375% | 92.375% | 0.000% | **100% Identical** |
| **Mean Negative Log-Likelihood (NLL)** | 0.779094 | **0.309020** | **-60.34%** | **PASSED** |
| **Mean Brier Score** | 0.137610 | **0.122400** | **-11.05%** | **PASSED** |
| **High-Confidence Cases ($p \ge 0.90$)** | 739 cases | 185 cases | -74.97% (De-bloated) | Expected |
| **High-Confidence Error Rate ($p \ge 0.90$)** | 5.82% (43/739) | **4.32%** (8/185) | **-1.50%** | **PASSED ($\le 5.0\%$)** |

---

## 5. Calibration Gate Verification Scorecard

| Gate | Criterion | Threshold | Measured Value | Verdict |
|:---|:---|:---:|:---:|:---:|
| **Gate 1** | Top-1 Prediction Parity | == 100.0% | **100.00% (800/800)** | **PASSED** |
| **Gate 2** | Fresh NLL Non-Worsening | $\le 0.779094$ | **0.309020** | **PASSED** |
| **Gate 3** | Fresh Brier Non-Worsening | $\le 0.137610$ | **0.122400** | **PASSED** |
| **Gate 4** | High-Confidence Error Rate | $\le 5.0\%$ | **4.32%** | **PASSED** |
| **Gate 5** | Model Checkpoint Cryptographic Binding | Exact SHA256 Match | `0951b356db1c...` | **PASSED** |

**Final Calibration Gate Verdict**: **ALL GATES OFFICIALLY PASSED**.

---

## 6. Artifact Binding & Integration

The calibration parameters are packaged and frozen in `release/rc2_1/calibration.json`:
```json
{
  "version": "1.0",
  "method": "temperature_scaling",
  "temperature": 2.772175803296264,
  "calibration_dataset": "data\\rc2_1_train\\calibration.jsonl",
  "model_sha256": "0951b356db1c72527826adeffe5fc24e8fb8a4360ac1e780df3e06cefb78d02b",
  "checkpoint_hashes": {
    "config.json": "30031aeabbfcbd04bd6211903d5779ec31de10af157f1bfb49ab36344b41111d",
    "model.safetensors": "0951b356db1c72527826adeffe5fc24e8fb8a4360ac1e780df3e06cefb78d02b",
    "tokenizer.json": "ac84fa7889747f37393545a7fc14ce4f1f158b33460318cad93531e0aa8db109",
    "tokenizer_config.json": "276e1525b9d4543bf789cfbd981155e82324d78a5dcf4fbc01803886899efc3e"
  },
  "created_at": "2026-09-20T19:44:13.005090+00:00"
}
```

The runtime engines (`GLiClassEngine` and `ERABIONNXEngine`) read this file on initialization and automatically apply $T^* = 2.772176$ to scale output logits for all downstream clients.
