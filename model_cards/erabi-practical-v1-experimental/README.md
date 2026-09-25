---
language:
- ja
- en
- zh
license: apache-2.0
library_name: transformers
pipeline_tag: text-classification
base_model: knowledgator/gliclass-instruct-large-v1.0
tags:
- gliclass
- choice-classification
- experimental
---

# ERABI Practical V1 (experimental)

This is an **experimental**, uncalibrated choice-ranking model. It is not an official Jev model, a validated general-purpose reasoner, or an automatic decision-maker. The model ranks 2–16 user-supplied candidate texts for a natural-language context and question and returns all candidate probabilities through the [ERABI code](https://github.com/sugarkwork/erabi). Decisions should be reviewed by a person.

## Provenance

- Base: [knowledgator/gliclass-instruct-large-v1.0](https://huggingface.co/knowledgator/gliclass-instruct-large-v1.0), Apache-2.0, 438,672,897 parameters.
- First fine-tune: one epoch on 2,414 Practical V1 training records, peak learning rate 2.5e-6, 151 optimizer steps, microbatch 2, gradient accumulation 8, fp16 AMP.
- Second, exploratory fine-tune (2026-09-23): one selected epoch on 175 privately held Exam-QA transformations mixed with 175 deterministic Practical V1 replay records, learning rate 1.5e-6, 22 optimizer steps, maximum training length 1,024 tokens.
- Practical V1 data consists of original synthetic Japanese, English, and Simplified Chinese examples in six task families, generated and answer-blind rejudged with DeepSeek V4.1 Flash.
- The Exam-QA source was filtered and transformed with the same DeepSeek model. Symbolic answer labels were mapped to source choice text. Ambiguous, multi-answer, figure-dependent, partial-credit, incomplete, or over-1,024-token items were skipped. Generated distractors were train-only; validation used source-provided choices only.
- Exam-QA source records, transformed JSONL, and API responses are **not published** pending human review and source-by-source redistribution review. They are not claimed as human gold.
- Data and training code: [GitHub repository](https://github.com/sugarkwork/erabi/tree/main/data/practical_v1) and [training script](https://github.com/sugarkwork/erabi/blob/main/scripts/train_practical_v1.py). Labels remain **unreviewed synthetic teacher agreement**, not human gold.

## Exploratory evaluation

| Set | Frozen RC3 before this fine-tune | This checkpoint |
|---|---:|---:|
| Practical V1 dev, 399 cases | 59.90% | 77.19% |
| Practical V1 held-out synthetic eval, 386 cases | 61.66% | 76.17% |
| Existing RC3 Bridge, 480 cases | 88.75% | 88.54% |

The Practical V1 eval set was used once after selecting by dev and existing-bridge results. Reading inference **regressed** from 54/71 to 50/71 despite aggregate gains. Candidate-order consistency on the existing bridge was 97.50%. These figures are not a benchmark of real-world correctness or Jev parity, because Practical V1 questions and labels come from the same teacher family. There is no independent human-verified final test, temperature calibration, or formal release approval for this checkpoint.

The current weights add the private Exam-QA experiment to that checkpoint:

| Set | Before Exam-QA fine-tune | Current weights |
|---|---:|---:|
| Private Exam-QA validation, source choices only, 37 cases | 21.62% (8/37) | **24.32% (9/37)** |
| Practical V1 dev, 399 cases | 77.19% (308/399) | **78.20% (312/399)** |
| Existing RC3 Bridge, 480 cases | 88.54% (425/480) | **88.54% (425/480)** |
| Practical V1 teacher-agreed eval, 386 cases | 76.17% (294/386) | 75.65% (292/386) |

The Exam-QA gain is only **one additional correct item**, so it is weak exploratory evidence, not a claim of exam competence. The validation set has just nine source groups and has not been independently human-audited. The current safetensors SHA256 is `1ae38ef6c1103f8c021b0d3a974f3b1aedc42d89832d11761e74b95664216251`.

## Use

```bash
python -m pip install erabi
erabi predict --request request.json
```

The repository contains three inference formats from the same checkpoint: `model.safetensors` (PyTorch), `onnx/fp32/model.onnx` (CPU), and `onnx/fp16/model.onnx` (NVIDIA GPU). ERABI 0.1.3 pins this updated checkpoint by default; 0.1.2 pins the earlier Practical V1-only revision. Upgrade with `python -m pip install --upgrade erabi`. `--model-format auto` downloads only the selected variant: FP32 ONNX for CPU with ONNX Runtime, FP16 ONNX for CUDA with CUDA Execution Provider, and otherwise PyTorch safetensors. Install the compatible `onnxruntime` (CPU) or `onnxruntime-gpu` (GPU) separately; do not install both in one environment. You can also select `--model-format pytorch`, `onnx-fp32`, or `onnx-fp16` explicitly.

The newly exported ONNX FP32 and FP16 variants preserved the PyTorch top-ranked choice on 37/37 private Exam-QA validation cases, up to 853 input tokens. Experimental INT8 variants changed predictions substantially and are not distributed. The first invocation downloads the selected model; later invocations use the Hugging Face cache. Input and output JSON contracts and runtime recommendations are documented in the [ERABI README](https://github.com/sugarkwork/erabi#モデル形式の自動選択とおすすめ). The public ERABI runtime still defaults to a 512-token fail-closed contract. The weights were trained and experimentally checked at up to 1,024 tokens, but using that length requires changing both the runtime limit and preprocessing length while checking the untruncated input. Candidate probabilities are not calibrated confidence guarantees.

## License and limitations

These fine-tuned weights derive from the Apache-2.0-licensed GLiClass base model and are distributed under Apache-2.0; see the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) and the [base model card](https://huggingface.co/knowledgator/gliclass-instruct-large-v1.0). ERABI source code is separately MIT-licensed. Do not rely on this experimental model for high-stakes or unattended decisions.
