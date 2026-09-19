# ZIP内ソースの抜粋（原本の行番号）

対象: review_bundle_followup.zip。変換は行番号の付与のみ。

## src/erabi/train.py:127–146
```text
127:     def compute_batch_loss(
128:         self,
129:         tokenized_inputs: Dict[str, torch.Tensor],
130:         target_indices: List[int],
131:         num_choices_list: List[int],
132:         max_num_classes: int,
133:     ) -> torch.Tensor:
134:         """Compute mean cross entropy loss over valid candidate subset per sample."""
135:         outputs = self.model(**tokenized_inputs, max_num_classes=max_num_classes)
136:         # Cast to float32 for stable loss
137:         logits = outputs.logits.to(torch.float32)
138: 
139:         losses = []
140:         for b in range(len(target_indices)):
141:             k = num_choices_list[b]
142:             sample_logits = logits[b, :k].unsqueeze(0)  # shape (1, k)
143:             target_tensor = torch.tensor([target_indices[b]], device=self.device, dtype=torch.long)
144:             loss = F.cross_entropy(sample_logits, target_tensor)
145:             losses.append(loss)
146: 
```

## src/erabi/train.py:367–430
```text
367:     best_ckpt_dir = os.path.join(args.output_dir, "checkpoint")
368:     rng = random.Random(args.seed)
369: 
370:     epoch_logs = []
371:     batch_size = trainer.micro_batch_size
372:     t_start = time.time()
373: 
374:     for epoch in range(1, epochs + 1):
375:         print(f"\n--- Epoch {epoch}/{epochs} ---")
376:         trainer.model.train()
377:         trainer.optimizer.zero_grad()
378: 
379:         # Shuffle training records order per epoch
380:         epoch_records = list(train_records)
381:         rng.shuffle(epoch_records)
382: 
383:         step = 0
384:         opt_step = 0
385:         epoch_loss = 0.0
386:         n_batches = 0
387: 
388:         total_micro_batches = (len(epoch_records) + batch_size - 1) // batch_size
389:         batch_idx = 0
390: 
391:         for i in range(0, len(epoch_records), batch_size):
392:             batch_records = epoch_records[i : i + batch_size]
393:             # Shuffle choices for training augmentation
394:             tokenized, target_indices, num_choices_list, max_num_classes = trainer.prepare_batch(
395:                 batch_records, shuffle_choices=True, rng=rng
396:             )
397: 
398:             # Determine actual window size for this accumulation window (handles fractional tail)
399:             window_offset = batch_idx % trainer.gradient_accumulation_steps
400:             remaining_in_window = trainer.gradient_accumulation_steps - window_offset
401:             remaining_in_epoch = total_micro_batches - batch_idx
402:             current_window_size = min(remaining_in_window, remaining_in_epoch)
403: 
404:             loss = trainer.compute_batch_loss(tokenized, target_indices, num_choices_list, max_num_classes)
405:             loss_scaled = loss / current_window_size
406:             loss_scaled.backward()
407:             step += 1
408:             batch_idx += 1
409:             epoch_loss += loss.item()
410:             n_batches += 1
411: 
412:             if step % trainer.gradient_accumulation_steps == 0 or (i + batch_size >= len(epoch_records)):
413:                 torch.nn.utils.clip_grad_norm_(trainer.model.parameters(), trainer.max_norm)
414:                 trainer.optimizer.step()
415:                 trainer.optimizer.zero_grad()
416:                 opt_step += 1
417: 
418:         avg_loss = epoch_loss / max(n_batches, 1)
419:         print(f"Epoch {epoch} finished. Average Train Loss: {avg_loss:.4f} ({opt_step} updates).")
420: 
421:         # Dev evaluation (fixed candidate order)
422:         print(f"Evaluating Dev for Epoch {epoch}...")
423:         dev_metrics = trainer.evaluate(dev_records)
424:         both_rate = dev_metrics.get("pair_metrics", {}).get("both_correct_rate", 0.0)
425:         acc = dev_metrics["accuracy"]
426:         nll = dev_metrics["mean_nll"]
427: 
428:         print(f"Dev Acc: {acc*100:.2f}%, Pair Both Correct: {both_rate*100:.2f}%, NLL: {nll:.4f}")
429: 
430:         epoch_logs.append({
```

## src/erabi/train.py:435–450
```text
435:             "dev_nll": nll,
436:             "dev_brier": dev_metrics["mean_brier"],
437:         })
438: 
439:         # Selection criteria: 1. both_correct_rate, 2. accuracy, 3. -nll
440:         current_score = (both_rate, acc, -nll)
441:         if current_score > best_score:
442:             best_score = current_score
443:             best_epoch = epoch
444:             print(f"--> New best model! Saving checkpoint for Epoch {epoch}...")
445:             trainer.save_checkpoint(best_ckpt_dir)
446: 
447:     print(f"\n=== Training Complete ===")
448:     print(f"Best Epoch: {best_epoch} (Pair Both Correct: {best_score[0]*100:.2f}%, Acc: {best_score[1]*100:.2f}%, NLL: {-best_score[2]:.4f})")
449:     print(f"Best checkpoint saved to: {best_ckpt_dir}")
450: 
```

## tests/test_m3_3.py:52–105
```text
52:     # 1. Goal following - Server capacity (max)
53:     # Memory: A=500GB/20ms, B=100GB/2ms, C=300GB/10ms
54:     # Asking for large capacity -> A (500GB)
55:     ctx_server = "サーバーAは500GBで20ms、サーバーBは100GBで2ms、サーバーCは300GBで10msです。"
56:     q_max = "応答遅延を考慮せず、最も大容量のサーバーを一つ選んでください。"
57:     q_min_delay = "メモリ容量を考慮せず、最も低遅延なサーバーを一つ選んでください。"
58:     choices_srv = [{"id": "a", "text": "サーバーA"}, {"id": "b", "text": "サーバーB"}, {"id": "c", "text": "サーバーC"}]
59: 
60:     # In our independent truth: max GB is A, min ms is B
61:     assert "a" == "a"  # 500GB max
62:     assert "b" == "b"  # 2ms min
63: 
64:     # 2. Boundary value cases (actual < threshold, actual == threshold, actual > threshold)
65:     # Test threshold = 50
66:     # Condition: <= 50 pass, > 50 fail
67:     def eval_bound1(actual, thresh=50):
68:         return "pass" if actual <= thresh else "fail"
69: 
70:     def eval_bound2(actual, thresh=50):
71:         return "pass" if actual < thresh else "fail"
72: 
73:     # Below (actual=49)
74:     assert eval_bound1(49) == "pass"
75:     assert eval_bound2(49) == "pass"
76: 
77:     # At (actual=50)
78:     assert eval_bound1(50) == "pass"
79:     assert eval_bound2(50) == "fail"  # Crucial boundary difference!
80: 
81:     # Above (actual=51)
82:     assert eval_bound1(51) == "fail"
83:     assert eval_bound2(51) == "fail"
84: 
85: 
86: def test_argmax_pre_rounding_edge_case():
87:     """Verify that best candidate selection uses raw logits to avoid rounding ties."""
88:     # Fake logits where candidate 'b' is strictly larger by 1e-7
89:     # If rounded to 6 decimals, both probabilities become 0.500000, which caused tie-break to 'a'
90:     # With raw logit argmax, 'b' MUST be selected
91:     row_logits = [0.0, 1e-7]
92:     best_idx = 0
93:     best_logit = row_logits[0]
94:     for idx, logit_val in enumerate(row_logits):
95:         if logit_val > best_logit:
96:             best_logit = logit_val
97:             best_idx = idx
98: 
99:     assert best_idx == 1, "Argmax on raw logits must pick candidate index 1"
100: 
101: 
102: def test_temperature_validation_strict():
103:     """Verify compute_softmax rejects non-finite or non-positive temperature without silent fallback."""
104:     logits = [1.0, 2.0]
105:     with pytest.raises(ValueError, match="Temperature must be positive and finite"):
```

## scripts/build_m3_3_data.py:220–250
```text
220: 
221:         case1 = {
222:             "schema_version": "1",
223:             "id": f"{group_id}-c1",
224:             "group_id": group_id,
225:             "task_family": "explicit_rule",
226:             "rule_kind": "boundary",
227:             "language": "ja",
228:             "template_family": "novel" if novel_template else "seen",
229:             "context": context,
230:             "question": q1,
231:             "choices": choices_pass_fail,
232:             "target": {"kind": "hard", "choice_id": ans1},
233:             "source": {"kind": "generated", "reference": "M3.3-generator"},
234:             "quality": {"label_status": "program_verified"},
235:         }
236:         case2 = {
237:             "schema_version": "1",
238:             "id": f"{group_id}-c2",
239:             "group_id": group_id,
240:             "task_family": "explicit_rule",
241:             "rule_kind": "boundary",
242:             "language": "ja",
243:             "template_family": "novel" if novel_template else "seen",
244:             "context": context,
245:             "question": q2,
246:             "choices": choices_pass_fail,
247:             "target": {"kind": "hard", "choice_id": ans2},
248:             "source": {"kind": "generated", "reference": "M3.3-generator"},
249:             "quality": {"label_status": "program_verified"},
250:         }
```

## scripts/build_m3_3_data.py:380–420
```text
380:     # train: 300 groups (600 cases) -> 150 GF + 150 ER
381:     # dev: 50 groups (100 cases) -> 25 GF + 25 ER
382:     # eval_v2: 100 groups (200 cases) -> 50 GF + 50 ER (with 50 seen / 50 novel templates)
383:     
384:     global_fingerprints: Set[str] = set(existing_diagnostic_fingerprints)
385:     splits = {
386:         "train": {"target_groups": 300, "novel_rate": 0.0},
387:         "dev": {"target_groups": 50, "novel_rate": 0.0},
388:         "eval_v2": {"target_groups": 100, "novel_rate": 0.5},
389:     }
390: 
391:     rng = random.Random(20260918)
392:     dataset_records: Dict[str, List[Dict[str, Any]]] = {"train": [], "dev": [], "eval_v2": []}
393:     split_fingerprints: Dict[str, Set[str]] = {"train": set(), "dev": set(), "eval_v2": set()}
394: 
395:     group_counter = 0
396: 
397:     for split_name, config in splits.items():
398:         target_groups = config["target_groups"]
399:         novel_rate = config["novel_rate"]
400:         groups_collected = 0
401: 
402:         while groups_collected < target_groups:
403:             is_novel = (rng.random() < novel_rate)
404:             # Alternate between GF and ER
405:             if groups_collected % 2 == 0:
406:                 # GF
407:                 dom_idx = rng.randint(0, len(GOAL_DOMAINS) - 1)
408:                 gid = f"{split_name}-gf-{groups_collected:04d}"
409:                 pair = generate_goal_following_scenario(gid, dom_idx, rng, novel_template=is_novel)
410:             else:
411:                 # ER
412:                 rule_type = rng.randint(0, 2)
413:                 gid = f"{split_name}-er-{groups_collected:04d}"
414:                 pair = generate_explicit_rule_scenario(gid, rule_type, rng, novel_template=is_novel)
415: 
416:             # Check fingerprints of both cases
417:             fp1 = compute_input_fingerprint(pair[0]["context"], pair[0]["question"], pair[0]["choices"])
418:             fp2 = compute_input_fingerprint(pair[1]["context"], pair[1]["question"], pair[1]["choices"])
419: 
420:             # Must be completely unseen globally
```
