# Third-Party Licenses

ERABI original source code is licensed under the [MIT License](LICENSE).

The following third-party components are used in ERABI.
Each component retains its original license.

## Dependencies

| Component | Upstream URL | License | Role |
| :--- | :--- | :--- | :--- |
| gliclass | https://github.com/Knowledgator/GLiClass | Apache-2.0 | Core classification architecture |
| transformers | https://github.com/huggingface/transformers | Apache-2.0 | Model loading & tokenization |
| torch | https://github.com/pytorch/pytorch | BSD-3-Clause | Deep learning framework |
| onnxruntime | https://github.com/microsoft/onnxruntime | MIT | High-performance inference runtime |
| pydantic | https://github.com/pydantic/pydantic | MIT | Schema validation |
| fastapi | https://github.com/tiangolo/fastapi | MIT | Optional HTTP API server |
| uvicorn | https://github.com/encode/uvicorn | BSD-3-Clause | Optional ASGI web server |
| scipy | https://github.com/scipy/scipy | BSD-3-Clause | Optional probability calibration |
| numpy | https://github.com/numpy/numpy | BSD-3-Clause | Array manipulation |
| pytest | https://github.com/pytest-dev/pytest | MIT | Test suite runner |
| httpx | https://github.com/encode/httpx | BSD-3-Clause | Test HTTP client |

## Pretrained Model Bases

| Component | Upstream URL | License | Role |
| :--- | :--- | :--- | :--- |
| gliclass-instruct-base-v1.0 | https://huggingface.co/knowledgator/gliclass-instruct-base-v1.0 | Apache-2.0 | Base model (RC1, RC2, RC2.1) |
| gliclass-instruct-large-v1.0 | https://huggingface.co/knowledgator/gliclass-instruct-large-v1.0 | Apache-2.0 | Base model (RC3, RC3.1) |
| microsoft/deberta-v3-base | https://huggingface.co/microsoft/deberta-v3-base | MIT | Text encoder backbone (base) |
| microsoft/deberta-v3-large | https://huggingface.co/microsoft/deberta-v3-large | MIT | Text encoder backbone (large) |
| BAAI/bge-small-en-v1.5 | https://huggingface.co/BAAI/bge-small-en-v1.5 | MIT | Label encoder backbone |

## Notes

- ERABI's fine-tuned model weights (under `release/`) are derivative works of the
  Apache-2.0 licensed GLiClass models. Redistribution is permitted under Apache-2.0
  terms with appropriate attribution.
- Applying the MIT License to ERABI source code does not override or relicense any
  upstream component. Each component's original license terms apply.
