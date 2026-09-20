# ERABI RC2 Blind Sealed Acceptance Suite v2 Invalidation Notice

**Date**: 2026-09-20 06:00:00 UTC  
**Status**: **`INVALID_DATASET` (Retired and Superseded by Blind Suite v3)**  
**Directive Authority**: [`ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md`](file:///f:/ai/erabi-local/ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md) Section 10  

---

## 1. Incident Summary

During the initial one-shot execution of `scripts/run_rc2_blind_reacceptance.py` on `data/sealed_acceptance_rc2_blind_v2/sealed_test_rc2_blind_v2.jsonl`, execution aborted at case index 341 with:
```text
erabi.schema.ValidationError: Total input length (513 tokens) exceeds maximum limit of 512 tokens.
```

An immediate token length audit across the entire 480-case suite revealed that **62 cases** (primarily in $K=12$ and $K=16$ where choice descriptions were verbose) had total token counts between 513 and 734 tokens, in direct violation of the ERABI input contract:
> *`AGENTS.md`: "選択肢は初期2～16、全入力512 tokens。無言のtruncationは禁止。"*  
> *`src/erabi/inference.py`: `if total_tokens > 512: raise ValidationError(...)`*

---

## 2. Invalidation Mandate (Directive Section 10)

Section 10 of `ERABI_RC2_BLIND_SEALED_REACCEPTANCE_DIRECTIVE.md` explicitly dictates:
```text
実行後:
- datasetを書き換えない
- generatorを書き換えない
- targetを書き換えない
- wordingを書き換えない
- 「曖昧だったので除外」をしない

semantic errorが本当に見つかった場合はsuite全体を INVALID_DATASET とし、
問題だけ直して同じsuiteとして再利用しない。
blind_v3 を新規作成する。
```

Accordingly:
1. `data/sealed_acceptance_rc2_blind_v2/` is permanently designated as `INVALID_DATASET` and preserved for audit transparency.
2. No post-hoc patch or in-place edit was applied to `sealed_test_rc2_blind_v2.jsonl`.
3. A fresh suite, `data/sealed_acceptance_rc2_blind_v3/`, is authored with concise choice strings ensuring that every case satisfies $\text{tokens} \le 450 < 512$, with zero model inference during authoring, and re-precommitted to Git before evaluation.
