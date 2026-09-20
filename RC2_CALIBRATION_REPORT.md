# ERABI Milestone 22 — RC2 Temperature Calibration Report

**Date**: 2026-09-20  
**Status**: **ALL GATES PASSED**  
**Milestone Reference**: `ERABI_RC2_AUTONOMOUS_RESEARCH_ROADMAP.md` (Section 16)  
**Calibrated Target Model**: `release/rc2/model/`  
**Bound Weights Hash (SHA256)**: `dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0`  
**Optimal Temperature ($T^*$)**: **`0.263007`**  
**Calibration Artifact**: `release/rc2/calibration.json`

---

## 1. Executive Summary

In Milestone 22, the frozen RC2 candidate model (`release/rc2/model/`) underwent independent probability calibration using temperature scaling via negative log-likelihood (NLL) optimization with float64 precision. Rather than reusing the historical RC1 calibration temperature ($T^* = 0.2560$), a brand new, leak-free calibration suite (`data/rc2_m22_calibration/`) was generated specifically for RC2.

The optimization successfully converged to an interior minimum of **$T^* = 0.263007$** within the bounded interval $[0.1, 10.0]$ without boundary saturation. On the fresh 100-case calibration verification suite, temperature scaling preserved **100.0% Top-1 prediction parity**, achieved **0.0% high-confidence errors ($p \ge 0.90$)**, and maintained optimal Brier and NLL scores.

All five Milestone 22 calibration gates are **PASSED**.

---

## 2. Gate Verification Summary

| Gate Requirement | Verification Condition | Measured Outcome | Gate Verdict |
| :--- | :---: | :---: | :---: |
| **Top-1 Prediction Parity** | Parity between $T=1.0$ and $T=T^*$ must be 100.0% | **100.00% (100/100)** | **PASS** |
| **Fresh NLL Non-Worsening** | $\text{NLL}(T^*) \le \text{NLL}(T=1.0)$ | $1.76 \times 10^{-14} \le 1.15 \times 10^{-6}$ | **PASS** |
| **Fresh Brier Score Non-Worsening** | $\text{Brier}(T^*) \le \text{Brier}(T=1.0)$ | $5.39 \times 10^{-28} \le 4.65 \times 10^{-12}$ | **PASS** |
| **High-Confidence Error Rate ($p \ge 0.90$)** | Must be $\le 5.0\%$ | **0.00% (0 / 100)** | **PASS** |
| **Cryptographic Model Hash Binding** | Must match frozen `model.safetensors` | `dd3bae25efcce97df8b14cf...` | **PASS** |

---

## 3. Fresh Calibration Evaluation Metrics ($T=1.0$ vs. $T=T^*$)

Evaluated on `data/rc2_m22_calibration/fresh_calibration_eval.jsonl` (100 cases / 50 pairs across Core rules, operators, natural Japanese, general choices, and variable choices):

| Metric | Raw Baseline ($T = 1.0$) | Calibrated RC2 ($T^* = 0.263007$) | Delta / Effect |
| :--- | :---: | :---: | :---: |
| **Top-1 Accuracy** | **100.0% (100/100)** | **100.0% (100/100)** | **0.0% (Strict Rank Preservation)** |
| **Mean Negative Log-Likelihood (NLL)** | $1.15 \times 10^{-6}$ | **$1.76 \times 10^{-14}$** | **Improved by $10^8\times$** |
| **Mean Brier Score** | $4.65 \times 10^{-12}$ | **$5.39 \times 10^{-28}$** | **Improved by $10^{16}\times$** |
| **Total Predictions with $p \ge 0.90$** | 100 / 100 | 100 / 100 | 100% High Confidence |
| **High-Confidence Errors ($p \ge 0.90$)** | **0 / 100 (0.0%)** | **0 / 100 (0.0%)** | **Zero Overconfident Errors** |

---

## 4. Calibration Artifact & Reproducibility Binding

The resulting calibration artifact is saved to `release/rc2/calibration.json`:

```json
{
  "version": "1.0",
  "method": "temperature_scaling",
  "temperature": 0.263007,
  "calibration_dataset": "data/rc2_m22_calibration/calibration.jsonl",
  "model_dir": "release/rc2/model",
  "target_model_sha256": "dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0",
  "checkpoint_hashes": {
    "config.json": "30031aeabbfcbd04bd6211903d5779ec31de10af157f1bfb49ab36344b41111d",
    "model.safetensors": "dd3bae25efcce97df8b14cf29064c9910f62686436ff95bb16b1c184fb03c0c0",
    "tokenizer.json": "ac84fa7889747f37393545a7fc14ce4f1f158b33460318cad93531e0aa8db109",
    "tokenizer_config.json": "276e1525b9d4543bf789cfbd981155e82324d78a5dcf4fbc01803886899efc3e"
  }
}
```

### Remark on Cross-Milestone Calibration Stability:
The optimal temperature for RC2 ($T^* = 0.2630$) is in near-perfect agreement with the RC1 optimal temperature ($T^* = 0.2560$). This demonstrates that across diverse capability expansions (from simple rule imitation to 10 general choice tasks and 12 natural Japanese styles), ERABI's underlying confidence dynamics remain remarkably stable and well-calibrated on the GLiClass architecture.

---

## 5. Next Step: Milestone 23 — ONNX FP16 Engine Build

With RC2 candidate weights and temperature calibration fully frozen and verified, we proceed to **Milestone 23: ONNX FP16 Export and Latency Benchmarking**:
- Export PyTorch $\to$ ONNX FP32 $\to$ ONNX FP16 CUDA.
- Verify 100% Top-1 parity across all 8 representative evaluation suites.
- Verify that inference latency achieves p50 $\le 15$ ms and p95 $\le 20$ ms on RTX A4000.
