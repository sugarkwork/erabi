# ERABI RC1 ONNX FP16 Runtime Limitations & Operational Bounds

1. **Localhost & Single-Worker Execution**:
   - The ERABI choice engine is strictly designed for local edge inference. Multi-worker asynchronous concurrency is disallowed to prevent VRAM allocation spikes and state corruption.

2. **Sequence Length Limit (512 tokens)**:
   - Inputs where `context + question + choices` exceed 512 tokens are rejected with HTTP 422 (`input_too_long`) to prevent truncation errors.

3. **Choice Count Bound (2 to 16)**:
   - The engine is verified and calibrated for between 2 and 16 candidates per request. Queries with fewer than 2 or more than 16 choices are rejected.

4. **Review Default Policy**:
   - Automated actions default to `decision.status = "review"`. The output probability distribution is a calibrated local decision ranking, not an infallible guarantee of external truth.

5. **CUDA Version Compatibility**:
   - Optimized for CUDA 12.x on Windows x64.
