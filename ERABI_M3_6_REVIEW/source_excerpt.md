# ERABI M3.6 ソース証拠（ユーザー提供ZIPの原文抜粋）

入力ZIP SHA256: `154973f51914402b9309c0803f1e88d72c371d8c9e4d4b4d2946bd0b2a287162`

各行の先頭は原ファイルの行番号。ここに含まれるコードは修正案ではなく、レビュー対象の原文。

## 採否状態と出力artifactのstatus
`scripts/run_m3_6_calibration.py` L509–L559
```python
 509     # 6. Determine Adoption Decision based on §6.1 Criteria:
 510     # Criteria:
 511     # - Numerically sound and not at search boundary
 512     # - On fresh_eval: NLL decreases (nll_diff > 0) AND Brier score does not worsen (brier_diff >= -1e-5)
 513     fresh_nll_imp = fresh_eval_summary["improvement"]["nll_diff"]
 514     fresh_brier_imp = fresh_eval_summary["improvement"]["brier_diff"]
 515 
 516     if not opt_summary["success"] or opt_summary["is_at_boundary"]:
 517         adoption_status = "unstable_boundary"
 518         adoption_decision = "HOLD (採用保留)"
 519         decision_reason = "Optimization failed or reached search boundary."
 520     elif fresh_nll_imp > 0 and fresh_brier_imp >= -1e-5:
 521         adoption_status = "applied_scoped"
 522         adoption_decision = "ACCEPT_SCOPED (合成ルール限定用途の校正候補として採用)"
 523         decision_reason = f"Fresh eval NLL improved by {fresh_nll_imp:.6f} and Brier score improved/maintained by {fresh_brier_imp:.6f}."
 524     else:
 525         adoption_status = "rejected_no_improvement"
 526         adoption_decision = "HOLD (採用保留)"
 527         decision_reason = f"Did not meet adoption criteria: NLL diff={fresh_nll_imp:.6f}, Brier diff={fresh_brier_imp:.6f}."
 528 
 529     logger.info(f"Adoption Decision: {adoption_decision} - {decision_reason}")
 530 
 531     # 7. Save calibration.json
 532     cal_file = ROOT / "data/m3_6_cal/calibration.jsonl"
 533     artifact_id = f"calib-m3_6-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}"
 534 
 535     calibration_artifact = {
 536         "artifact_id": artifact_id,
 537         "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
 538         "status": adoption_status,
 539         "temperature": round(optimal_T, 4),
 540         "method": "temperature_scaling_nll_minimize_scalar",
 541         "optimization": opt_summary,
 542         "target_model": {
 543             "checkpoint_path": str(MODEL_PATH),
 544             "model_safetensors_sha256": checkpoint_hashes.get("model.safetensors"),
 545             "files": checkpoint_hashes,
 546         },
 547         "dataset": {
 548             "path": str(cal_file),
 549             "cases": len(raw_results["calibration"]),
 550             "groups": len(raw_results["calibration"]) // 2,
 551             "sha256": compute_file_sha256(cal_file),
 552             "description": "ERABI M3.6 synthetic rule calibration set (goal_following and explicit_rule pairs)",
 553         },
 554         "contract": {
 555             "schema_version": "1",
 556             "max_tokens": MAX_TOKENS,
 557             "precision": "float32_forward_float64_nll",
 558             "decision_policy": "review_default",
 559             "scope": "bounded_synthetic_rules_only",
```

## APIが受け入れるstatusとフォールバック
`src/erabi/api.py` L46–L81
```python
  46     @asynccontextmanager
  47     async def lifespan(app: FastAPI):
  48         app.state.lock = asyncio.Lock()
  49         app.state.temperature = 1.0
  50         app.state.calibration_output = CalibrationOutput(status="none", artifact_id=None)
  51 
  52         if require_calibration and not calibration_path:
  53             raise RuntimeError(
  54                 "Calibration is required (--require-calibration), but no calibration_path was provided."
  55             )
  56 
  57         if calibration_path:
  58             from erabi.__main__ import load_and_verify_calibration
  59 
  60             logger.info(f"Verifying and loading calibration from {calibration_path}...")
  61             temp, calib_out, calib_data = load_and_verify_calibration(calibration_path, model_id)
  62             if calib_out.status == "applied":
  63                 app.state.temperature = temp
  64                 app.state.calibration_output = calib_out
  65                 logger.info(f"Calibration applied: T={temp:.4f}, artifact_id={calib_out.artifact_id}")
  66             else:
  67                 if require_calibration:
  68                     raise RuntimeError(
  69                         f"Calibration artifact status is '{calib_out.status}', but calibration was required."
  70                     )
  71                 logger.warning(
  72                     f"Calibration status is '{calib_out.status}'. Starting in uncalibrated mode (T=1.0)."
  73                 )
  74                 app.state.temperature = 1.0
  75                 app.state.calibration_output = CalibrationOutput(status="none", artifact_id=None)
  76 
  77         logger.info(f"Initializing engine for model: {model_id}...")
  78         if engine_factory:
  79             app.state.engine = engine_factory()
  80         else:
  81             app.state.engine = GLiClassEngine(model_id=model_id, device=device)
```

## モデルhash照合と契約読込
`src/erabi/__main__.py` L128–L160
```python
 128 def load_and_verify_calibration(calib_path: str, model_id: str):
 129     """Load calibration artifact and verify file hashes against target model checkpoint."""
 130     from erabi.schema import CalibrationOutput
 131     with open(calib_path, "r", encoding="utf-8") as f:
 132         calib_data = json.load(f)
 133 
 134     if "temperature" not in calib_data:
 135         raise ValueError("Calibration artifact missing 'temperature' field.")
 136     temp = float(calib_data["temperature"])
 137     if not math.isfinite(temp) or temp <= 0.0:
 138         raise ValueError(f"Calibration temperature must be positive and finite, got {temp}")
 139 
 140     status = calib_data.get("status", "none")
 141     if status == "applied":
 142         target_model = calib_data.get("target_model")
 143         if not target_model or not isinstance(target_model, dict):
 144             raise ValueError("Calibration status is 'applied' but 'target_model' information is missing.")
 145         target_files = target_model.get("files")
 146         if not target_files:
 147             raise ValueError("Calibration status is 'applied' but 'target_model.files' is empty or missing.")
 148         if os.path.isdir(model_id):
 149             from erabi.calibrate import compute_file_sha256
 150             for fname, expected_hash in target_files.items():
 151                 fpath = os.path.join(model_id, fname)
 152                 if not os.path.isfile(fpath):
 153                     raise ValueError(f"Calibration target model file missing: {fname}")
 154                 actual_hash = compute_file_sha256(fpath)
 155                 if actual_hash != expected_hash:
 156                     raise ValueError(f"Calibration hash mismatch for {fname}: expected {expected_hash}, got {actual_hash}")
 157 
 158     artifact_id = calib_data.get("artifact_id")
 159     calib_out = CalibrationOutput(status=status, artifact_id=artifact_id)
 160     return temp, calib_out, calib_data
```

## 既存logitsの再利用判定
`scripts/run_m3_6_calibration.py` L382–L427
```python
 382 def main():
 383     OUT_DIR.mkdir(parents=True, exist_ok=True)
 384     device = "cuda:0" if torch.cuda.is_available() else "cpu"
 385     logger.info(f"Using device: {device}")
 386 
 387     # Compute checkpoint hashes
 388     checkpoint_hashes = get_checkpoint_hashes(MODEL_PATH)
 389     logger.info(f"Verified {len(checkpoint_hashes)} files in checkpoint.")
 390 
 391     # 2. Extract or load raw logits on calibration and fresh_eval
 392     datasets = {
 393         "calibration": ROOT / "data/m3_6_cal/calibration.jsonl",
 394         "fresh_eval": ROOT / "data/m3_6_cal/fresh_eval.jsonl",
 395     }
 396 
 397     raw_results = {}
 398     need_inference = False
 399     for sname, spath in datasets.items():
 400         out_pred = OUT_DIR / f"raw_logits_{sname}.jsonl"
 401         if out_pred.exists():
 402             logger.info(f"Loading existing raw logits for {sname} from {out_pred}...")
 403             raw_results[sname] = [json.loads(l) for l in open(out_pred, encoding="utf-8")]
 404         else:
 405             need_inference = True
 406 
 407     if need_inference:
 408         logger.info(f"Loading checkpoint from {MODEL_PATH} onto {device}...")
 409         tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH))
 410         model = GLiClassModel.from_pretrained(str(MODEL_PATH)).to(device)
 411         model.eval()
 412 
 413         for sname, spath in datasets.items():
 414             if sname in raw_results:
 415                 continue
 416             logger.info(f"Running inference on {sname} ({spath})...")
 417             records = [json.loads(l) for l in open(spath, encoding="utf-8")]
 418             res = run_inference_and_extract_records(model, tokenizer, records, device)
 419             raw_results[sname] = res
 420 
 421             out_pred = OUT_DIR / f"raw_logits_{sname}.jsonl"
 422             with open(out_pred, "w", encoding="utf-8") as f:
 423                 for item in res:
 424                     f.write(json.dumps(item, ensure_ascii=False) + "\n")
 425             logger.info(f"Saved {len(res)} raw predictions to {out_pred}")
 426     else:
 427         logger.info("All raw logits loaded from disk. Skipping model inference.")
```

## 新規GF状態のキー
`scripts/build_m3_6_data.py` L105–L126
```python
 105         v2_pool = sorted(rng.sample(range(1, 25), 3))
 106 
 107     p1 = [0, 1, 2]
 108     rng.shuffle(p1)
 109     p2 = [0, 1, 2]
 110     rng.shuffle(p2)
 111 
 112     items = []
 113     choices = []
 114     val_pairs = []
 115     for idx in range(3):
 116         cid = choice_ids[idx]
 117         cname = f"{prefix}{choice_letters[idx]}"
 118         val1 = v1_pool[p1[idx]]
 119         val2 = v2_pool[p2[idx]]
 120         items.append({"id": cid, "name": cname, "v1": val1, "v2": val2})
 121         choices.append({"id": cid, "text": cname})
 122         val_pairs.append((val1, val2))
 123 
 124     semantic_state = ("gf", dom_name, tuple(sorted(val_pairs)))
 125 
 126     ctx_items = list(items)
```

## 既存GF状態を読むキー
`scripts/build_m3_6_data.py` L361–L394
```python
 361 def extract_existing_semantic_states(filepath: Path) -> Set[Any]:
 362     states = set()
 363     with open(filepath, "r", encoding="utf-8") as f:
 364         for line in f:
 365             d = json.loads(line)
 366             ctx = d["context"]
 367             q = d["question"]
 368             rk = d.get("rule_kind")
 369             tf = d["task_family"]
 370             if tf == "explicit_rule":
 371                 if rk == "composite_logic" or "HP" in ctx:
 372                     m_hp = re.search(r"HPは(\d+)", ctx)
 373                     m_item = "アイテムあり" in ctx
 374                     m_th = re.search(r"HPが(\d+)未満", q)
 375                     if m_hp and m_th:
 376                         states.add(("composite_logic", int(m_th.group(1)), int(m_hp.group(1)), m_item))
 377                 elif rk == "boundary" or "測定数値は" in ctx:
 378                     m_act = re.search(r"ちょうど(\d+)点", ctx)
 379                     m_th = re.search(r"(\d+)点", q)
 380                     if m_act and m_th:
 381                         states.add(("boundary", int(m_th.group(1)), int(m_act.group(1))))
 382                 elif rk == "comparison" or "在庫数" in ctx:
 383                     m_inv = re.search(r"在庫数は(\d+)個", ctx)
 384                     m_dem = re.search(r"受注数は(\d+)個", ctx)
 385                     if m_inv and m_dem:
 386                         states.add(("comparison", int(m_inv.group(1)), int(m_dem.group(1))))
 387             elif tf == "goal_following":
 388                 # Extract numeric tuples
 389                 m_nums = tuple(map(int, re.findall(r"(\d+)", ctx)))
 390                 if m_nums:
 391                     states.add(("gf", m_nums))
 392     return states
 393 
 394 
```

## 候補数別集計のelse分岐
`scripts/run_m3_6_calibration.py` L239–L269
```python
 239             "diff_target_both": diff_target_both,
 240             "diff_target_rate": diff_target_both / max(1, diff_target_total),
 241             "same_target_pairs": same_target_total,
 242             "same_target_both": same_target_both,
 243             "same_target_rate": same_target_both / max(1, same_target_total),
 244             "task_breakdown": task_breakdown,
 245         }
 246     else:
 247         pair_stats = {
 248             "is_paired": False,
 249             "note": "Dataset contains single or non-binary group records (e.g. smoke cases). Pair stats omitted.",
 250         }
 251 
 252     # NLL / Brier breakdown by choice count (2 vs 3 choices)
 253     nll_2ch_t1, nll_2ch_cal = [], []
 254     nll_3ch_t1, nll_3ch_cal = [], []
 255     brier_2ch_t1, brier_2ch_cal = [], []
 256     brier_3ch_t1, brier_3ch_cal = [], []
 257 
 258     for i, r in enumerate(dataset_records):
 259         n_ch = len(r["choices"])
 260         if n_ch == 2:
 261             nll_2ch_t1.append(metrics_t1[i]["nll"])
 262             nll_2ch_cal.append(metrics_cal[i]["nll"])
 263             brier_2ch_t1.append(metrics_t1[i]["brier"])
 264             brier_2ch_cal.append(metrics_cal[i]["brier"])
 265         else:
 266             nll_3ch_t1.append(metrics_t1[i]["nll"])
 267             nll_3ch_cal.append(metrics_cal[i]["nll"])
 268             brier_3ch_t1.append(metrics_t1[i]["brier"])
 269             brier_3ch_cal.append(metrics_cal[i]["brier"])
```

## 戻り値pair_stats
`scripts/run_m3_6_calibration.py` L337–L352
```python
 337     return {
 338         "total_cases": total_cases,
 339         "correct_count": correct_count,
 340         "accuracy": accuracy,
 341         "pair_stats": {
 342             "total_pairs": total_pairs,
 343             "both_correct": both_correct,
 344             "both_rate": both_correct / total_pairs,
 345             "diff_target_pairs": diff_target_total,
 346             "diff_target_both": diff_target_both,
 347             "diff_target_rate": diff_target_both / max(1, diff_target_total),
 348             "same_target_pairs": same_target_total,
 349             "same_target_both": same_target_both,
 350             "same_target_rate": same_target_both / max(1, same_target_total),
 351             "task_breakdown": task_breakdown,
 352         },
```
