# Practical V1 synthetic choice data

This directory contains original, fictional choice questions generated with
DeepSeek V4.1 Flash. It is a **candidate corpus**,
not human-reviewed gold and not a measure of real-world accuracy. No private
chat logs, actual entrance exams, or copyrighted passages were supplied as
prompts. The apparent exam questions are newly generated, self-contained
examples rather than past papers.

DeepSeek's [Terms of Use](https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html)
(section 4.2, checked 2026-09-22) explicitly include training other models among
permitted uses of outputs, subject to applicable law and the Terms.

Families: everyday arithmetic word problems, tool selection, next dialogue
action, JSON conversation-log tool selection, reading inference, and original
exam-style questions. Each family has Japanese, English, and Simplified Chinese
examples. `train.jsonl`, `dev.jsonl`, and `eval_candidate.jsonl` are separated
by generation topic and ID. `eval_teacher_agreed.jsonl` is the stricter
evaluation candidate subset that survived two answer-blind same-model checks.

`all.jsonl` is the unfiltered generation output. `all_judgments.jsonl` and
`eval_judgments.jsonl` retain checks and disagreements. The packaged splits
exclude answer disagreements and known arithmetic-spec overlap between train
and holdout. Choice order is deterministically shuffled while candidate IDs
and the target ID are preserved. `audit.json` has counts, token checks, and
SHA-256 hashes. `usage_ledger.json` records API token usage and a conservative
peak-price spending estimate; it does not contain the API key.

Generation and re-audit:

```powershell
.venv\Scripts\python.exe scripts\build_practical_v1.py --batch-size 6 --train-batches 24 --holdout-batches 4 --budget-usd 5
.venv\Scripts\python.exe scripts\audit_practical_v1.py --judge-eval --budget-usd 5
.venv\Scripts\python.exe scripts\audit_practical_v1.py --judge-all --budget-usd 5
```

API credentials stay outside Git. The API usage ledger is resumed across runs.
Re-running a judge pass does not regenerate records, but a malformed response
may require another paid attempt. Do not treat teacher agreement as correctness,
calibrated probability, or final sealed acceptance; independent human review
and a truly held-out evaluation set remain necessary before release claims.

The process is resumable but model sampling is not deterministic. The final
counts and hashes in `audit.json`, not the command-line batch target, define
this corpus version.
