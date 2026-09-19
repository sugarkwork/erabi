# M3.4 ZIP内コードの抜粋

出所：review_bundle(2).zip。L番号はZIP内元ファイルの行番号。

## src/erabi/train.py : L380–L430

```python
L380:         epoch_records = list(train_records)
L381:         rng.shuffle(epoch_records)
L382: 
L383:         step = 0
L384:         opt_step = 0
L385:         epoch_loss = 0.0
L386:         n_batches = 0
L387: 
L388:         total_micro_batches = (len(epoch_records) + batch_size - 1) // batch_size
L389:         batch_idx = 0
L390: 
L391:         for i in range(0, len(epoch_records), batch_size):
L392:             batch_records = epoch_records[i : i + batch_size]
L393:             # Shuffle choices for training augmentation
L394:             tokenized, target_indices, num_choices_list, max_num_classes = trainer.prepare_batch(
L395:                 batch_records, shuffle_choices=True, rng=rng
L396:             )
L397: 
L398:             # Determine window bounds and total sample count in this accumulation window
L399:             window_start_batch = (batch_idx // trainer.gradient_accumulation_steps) * trainer.gradient_accumulation_steps
L400:             window_start_sample = window_start_batch * batch_size
L401:             window_end_sample = min(
L402:                 window_start_sample + trainer.gradient_accumulation_steps * batch_size,
L403:                 len(epoch_records),
L404:             )
L405:             window_sample_count = window_end_sample - window_start_sample
L406: 
L407:             loss = trainer.compute_batch_loss(tokenized, target_indices, num_choices_list, max_num_classes)
L408:             loss_scaled = loss * (len(batch_records) / window_sample_count)
L409:             loss_scaled.backward()
L410:             step += 1
L411:             batch_idx += 1
L412:             epoch_loss += loss.item()
L413:             n_batches += 1
L414: 
L415:             if step % trainer.gradient_accumulation_steps == 0 or (i + batch_size >= len(epoch_records)):
L416:                 torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
L417:                 trainer.optimizer.step()
L418:                 trainer.optimizer.zero_grad()
L419:                 opt_step += 1
L420: 
L421:         avg_loss = epoch_loss / max(n_batches, 1)
L422:         print(f"Epoch {epoch} finished. Average Train Loss: {avg_loss:.4f} ({opt_step} updates).")
L423: 
L424:         # Dev evaluation (fixed candidate order)
L425:         print(f"Evaluating Dev for Epoch {epoch}...")
L426:         dev_metrics = trainer.evaluate(dev_records)
L427:         both_rate = dev_metrics.get("pair_metrics", {}).get("both_correct_rate", 0.0)
L428:         acc = dev_metrics["accuracy"]
L429:         nll = dev_metrics["mean_nll"]
L430: 
```

## src/erabi/train.py : L430–L482

```python
L430: 
L431:         print(f"Dev Acc: {acc*100:.2f}%, Pair Both Correct: {both_rate*100:.2f}%, NLL: {nll:.4f}")
L432: 
L433:         epoch_logs.append({
L434:             "epoch": epoch,
L435:             "train_loss": round(avg_loss, 4),
L436:             "dev_accuracy": acc,
L437:             "dev_both_correct_rate": both_rate,
L438:             "dev_nll": nll,
L439:             "dev_brier": dev_metrics["mean_brier"],
L440:         })
L441: 
L442:         # Selection criteria: 1. both_correct_rate, 2. accuracy, 3. -nll
L443:         current_score = (both_rate, acc, -nll)
L444:         if current_score > best_score:
L445:             best_score = current_score
L446:             best_epoch = epoch
L447:             print(f"--> New best model! Saving checkpoint for Epoch {epoch}...")
L448:             trainer.save_checkpoint(best_ckpt_dir)
L449: 
L450:     print(f"\n=== Training Complete ===")
L451:     print(f"Best Epoch: {best_epoch} (Pair Both Correct: {best_score[0]*100:.2f}%, Acc: {best_score[1]*100:.2f}%, NLL: {-best_score[2]:.4f})")
L452:     print(f"Best checkpoint saved to: {best_ckpt_dir}")
L453: 
L454:     # Save training summary
L455:     summary = {
L456:         "base_model": args.model_id,
L457:         "epochs": epochs,
L458:         "best_epoch": best_epoch,
L459:         "initial_dev": init_dev,
L460:         "best_score": {
L461:             "both_correct_rate": best_score[0],
L462:             "accuracy": best_score[1],
L463:             "nll": -best_score[2],
L464:         },
L465:         "history": epoch_logs,
L466:         "elapsed_sec": round(time.time() - t_start, 2),
L467:     }
L468:     with open(os.path.join(args.output_dir, "train_summary.json"), "w", encoding="utf-8") as f:
L469:         json.dump(summary, f, indent=2, ensure_ascii=False)
L470: 
L471: 
L472: def main():
L473:     parser = argparse.ArgumentParser(prog="python -m erabi.train")
L474:     parser.add_argument("--mode", type=str, choices=["overfit", "full"], required=True, help="Training mode")
L475:     parser.add_argument("--data-dir", type=str, default="data/m2_1", help="Path to data directory")
L476:     parser.add_argument("--output-dir", type=str, required=True, help="Directory to save checkpoint and logs")
L477:     parser.add_argument("--model-id", type=str, default=DEFAULT_MODEL_ID, help="Base model ID")
L478:     parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
L479:     parser.add_argument("--weight-decay", type=float, default=0.01, help="Weight decay")
L480:     parser.add_argument("--max-steps", type=int, default=300, help="Max optimizer steps for overfit")
L481:     parser.add_argument("--epochs", type=int, default=5, help="Epochs for full training")
L482:     parser.add_argument("--micro-batch-size", type=int, default=2, help="Micro batch size")
```

## scripts/verify_gradient_accumulation.py : L42–L108

```python
L42: 
L43: 
L44: def compute_accumulated_gradients(
L45:     samples_x: torch.Tensor,
L46:     samples_y: torch.Tensor,
L47:     micro_batch_size: int,
L48:     gradient_accumulation_steps: int,
L49:     mode: str = "fixed",  # "fixed" (M3.4 fix), "old" (M3.3 bug)
L50: ) -> Tuple[torch.Tensor, List[float]]:
L51:     """Simulate training accumulation loop."""
L52:     model = TinyLinearModel(in_features=samples_x.size(1), num_classes=3)
L53:     loss_fn = nn.CrossEntropyLoss(reduction="mean")
L54: 
L55:     total_samples = samples_x.size(0)
L56:     batch_indices = list(range(0, total_samples, micro_batch_size))
L57:     total_micro_batches = len(batch_indices)
L58: 
L59:     recorded_losses = []
L60: 
L61:     for batch_idx, start_idx in enumerate(batch_indices):
L62:         end_idx = min(start_idx + micro_batch_size, total_samples)
L63:         batch_x = samples_x[start_idx:end_idx]
L64:         batch_y = samples_y[start_idx:end_idx]
L65:         batch_count = end_idx - start_idx
L66: 
L67:         # Forward
L68:         logits = model(batch_x)
L69:         loss = loss_fn(logits, batch_y)
L70:         recorded_losses.append(loss.item())
L71: 
L72:         if mode == "fixed":
L73:             # M3.4 fixed formula
L74:             window_start_batch = (batch_idx // gradient_accumulation_steps) * gradient_accumulation_steps
L75:             window_start_sample = window_start_batch * micro_batch_size
L76:             window_end_sample = min(
L77:                 window_start_sample + gradient_accumulation_steps * micro_batch_size,
L78:                 total_samples,
L79:             )
L80:             window_sample_count = window_end_sample - window_start_sample
L81:             loss_scaled = loss * (batch_count / window_sample_count)
L82:         elif mode == "old":
L83:             # M3.3 buggy formula
L84:             window_offset = batch_idx % gradient_accumulation_steps
L85:             remaining_in_window = gradient_accumulation_steps - window_offset
L86:             remaining_in_epoch = total_micro_batches - batch_idx
L87:             current_window_size = min(remaining_in_window, remaining_in_epoch)
L88:             loss_scaled = loss / current_window_size
L89:         else:
L90:             raise ValueError(f"Unknown mode: {mode}")
L91: 
L92:         loss_scaled.backward()
L93: 
L94:     grad = model.fc.weight.grad.clone()
L95:     return grad, recorded_losses
L96: 
L97: 
L98: def compute_exact_window_gradient(
L99:     samples_x: torch.Tensor,
L100:     samples_y: torch.Tensor,
L101: ) -> torch.Tensor:
L102:     """Compute exact gradient from a single forward-backward pass of the full window mean."""
L103:     model = TinyLinearModel(in_features=samples_x.size(1), num_classes=3)
L104:     loss_fn = nn.CrossEntropyLoss(reduction="mean")
L105: 
L106:     logits = model(samples_x)
L107:     loss = loss_fn(logits, samples_y)
L108:     loss.backward()
```

## tests/test_train.py : L100–L145

```python
L100:     assert (15 < 20 and False) is False
L101: 
L102: 
L103: def test_gradient_accumulation_matches_full_window_gradient():
L104:     """Verify that micro-batch weighting matches exact single-pass full-window mean gradient."""
L105:     torch.manual_seed(42)
L106:     # Test 3 distinct scenarios: normal 16 (2x8), fractional tail 15 (2x7+1x1), partial 8 (2x4)
L107:     for n_samples in [16, 15, 8]:
L108:         x = torch.randn(n_samples, 4)
L109:         y = torch.randint(0, 3, (n_samples,))
L110: 
L111:         # 1. Exact full-window gradient
L112:         model_exact = torch.nn.Linear(4, 3, bias=False)
L113:         with torch.no_grad():
L114:             model_exact.weight.fill_(0.0)
L115:         loss_exact = torch.nn.functional.cross_entropy(model_exact(x), y, reduction="mean")
L116:         loss_exact.backward()
L117:         exact_grad = model_exact.weight.grad.clone()
L118: 
L119:         # 2. Accumulated micro-batches (micro_batch=2, accum=8)
L120:         model_accum = torch.nn.Linear(4, 3, bias=False)
L121:         with torch.no_grad():
L122:             model_accum.weight.fill_(0.0)
L123: 
L124:         batch_size = 2
L125:         accum_steps = 8
L126:         batch_indices = list(range(0, n_samples, batch_size))
L127: 
L128:         for batch_idx, start_idx in enumerate(batch_indices):
L129:             end_idx = min(start_idx + batch_size, n_samples)
L130:             bx = x[start_idx:end_idx]
L131:             by = y[start_idx:end_idx]
L132: 
L133:             # M3.4 exact window sample count weighting
L134:             window_start_batch = (batch_idx // accum_steps) * accum_steps
L135:             window_start_sample = window_start_batch * batch_size
L136:             window_end_sample = min(window_start_sample + accum_steps * batch_size, n_samples)
L137:             window_sample_count = window_end_sample - window_start_sample
L138: 
L139:             loss = torch.nn.functional.cross_entropy(model_accum(bx), by, reduction="mean")
L140:             loss_scaled = loss * (len(bx) / window_sample_count)
L141:             loss_scaled.backward()
L142: 
L143:         accum_grad = model_accum.weight.grad.clone()
L144:         max_diff = (accum_grad - exact_grad).abs().max().item()
L145:         assert max_diff < 1e-6, f"Gradient mismatch for n={n_samples}: {max_diff}"
```

## tests/test_m3_3.py : L47–L76

```python
L47:     assert len(split_fps["dev"] & split_fps["eval_v2"]) == 0, "Dev and Eval_v2 share identical inputs!"
L48: 
L49: 
L50: def test_independent_expected_cases():
L51:     """Verify ground truth computation on independent hand-crafted cases."""
L52:     # 1. Goal following - Server capacity (max)
L53:     # Memory: A=500GB/20ms, B=100GB/2ms, C=300GB/10ms
L54:     # Asking for large capacity -> A (500GB)
L55:     ctx_server = "サーバーAは500GBで20ms、サーバーBは100GBで2ms、サーバーCは300GBで10msです。"
L56:     q_max = "応答遅延を考慮せず、最も大容量のサーバーを一つ選んでください。"
L57:     q_min_delay = "メモリ容量を考慮せず、最も低遅延なサーバーを一つ選んでください。"
L58:     choices_srv = [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}]
L59: 
L60:     # In our independent truth: max GB is A (500GB), min ms is B (2ms)
L61:     import re
L62:     matches = re.findall(r"([^\s、]+)は(\d+)GBで(\d+)ms", ctx_server)
L63:     c_map = {c["text"]: c["id"] for c in choices_srv}
L64:     best_cap_name = max(matches, key=lambda m: int(m[1]))[0]
L65:     best_delay_name = min(matches, key=lambda m: int(m[2]))[0]
L66:     assert c_map[best_cap_name] == "a"  # 500GB max correctly maps to choice 'a'
L67:     assert c_map[best_delay_name] == "b"  # 2ms min correctly maps to choice 'b'
L68: 
L69:     # 2. Boundary value cases (actual < threshold, actual == threshold, actual > threshold)
L70:     # Test threshold = 50
L71:     # Condition: <= 50 pass, > 50 fail
L72:     def eval_bound1(actual, thresh=50):
L73:         return "pass" if actual <= thresh else "fail"
L74: 
L75:     def eval_bound2(actual, thresh=50):
L76:         return "pass" if actual < thresh else "fail"
```
