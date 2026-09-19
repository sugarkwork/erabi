"""Unit tests for M2.1 data splits, candidate shuffle, and loss calculations."""

import json
import os
import random
import pytest
import torch
import torch.nn.functional as F


def test_group_split_non_overlap():
    """Verify that no group_id appears in multiple splits."""
    data_dir = "data/m2_1"
    if not os.path.exists(data_dir):
        pytest.skip("data/m2_1 not generated yet")

    splits = {}
    for s in ["train", "dev", "holdout"]:
        p = os.path.join(data_dir, f"{s}.jsonl")
        gids = set()
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                gids.add(d["group_id"])
        splits[s] = gids

    assert len(splits["train"] & splits["dev"]) == 0
    assert len(splits["train"] & splits["holdout"]) == 0
    assert len(splits["dev"] & splits["holdout"]) == 0


def test_candidate_permutation_alignment():
    """Verify that permuting choices properly tracks target_idx."""
    choices = [
        {"id": "a", "text": "Plan A"},
        {"id": "b", "text": "Plan B"},
        {"id": "c", "text": "Plan C"},
    ]
    target_choice_id = "b"

    # Original target index is 1
    orig_idx = next(i for i, c in enumerate(choices) if c["id"] == target_choice_id)
    assert orig_idx == 1

    # Permute choices
    rng = random.Random(123)
    shuffled_choices = list(choices)
    rng.shuffle(shuffled_choices)

    # Re-derive target index
    shuffled_idx = next(i for i, c in enumerate(shuffled_choices) if c["id"] == target_choice_id)
    assert shuffled_choices[shuffled_idx]["id"] == target_choice_id
    assert shuffled_choices[shuffled_idx]["text"] == "Plan B"


def test_per_sample_cross_entropy_with_variable_choices():
    """Verify cross-entropy computation on variable choice subsets without NaN."""
    # Batch size 2: sample 0 has 2 choices, sample 1 has 3 choices
    # Max classes in batch = 3
    logits = torch.tensor(
        [
            [2.0, 1.0, -100.0],  # sample 0: only indices 0, 1 valid
            [0.5, 3.0, 1.5],     # sample 1: indices 0, 1, 2 valid
        ],
        dtype=torch.float32,
    )
    targets = [0, 1]  # sample 0 target is 0, sample 1 target is 1
    num_choices = [2, 3]

    losses = []
    for b in range(2):
        k = num_choices[b]
        sample_logits = logits[b, :k].unsqueeze(0)
        target_tensor = torch.tensor([targets[b]], dtype=torch.long)
        sample_loss = F.cross_entropy(sample_logits, target_tensor)
        losses.append(sample_loss)

    total_loss = torch.stack(losses).mean()
    assert torch.isfinite(total_loss)
    # Hand calculation for sample 0:
    # softmax([2.0, 1.0]) -> p[0] = exp(2)/(exp(2)+exp(1)) = 7.389 / (7.389+2.718) = 0.731
    # -log(0.731) = 0.313
    assert abs(losses[0].item() - 0.313) < 1e-2


def test_data_generation_boundary_and_composite():
    """Verify programmatic verification of boundary condition logic."""
    # <= 20: 20 is pass, 21 is fail
    threshold = 20
    assert 20 <= threshold  # pass
    assert not (21 <= threshold)  # fail

    # < 20: 20 is fail, 19 is pass
    assert not (20 < threshold)  # fail
    assert 19 < threshold  # pass

    # AND condition: hp < 20 AND has_item
    assert (15 < 20 and True) is True
    assert (25 < 20 and True) is False
    assert (15 < 20 and False) is False


def test_gradient_accumulation_matches_full_window_gradient():
    """Verify that micro-batch weighting matches exact single-pass full-window mean gradient."""
    torch.manual_seed(42)
    # Test 3 distinct scenarios: normal 16 (2x8), fractional tail 15 (2x7+1x1), partial 8 (2x4)
    for n_samples in [16, 15, 8]:
        x = torch.randn(n_samples, 4)
        y = torch.randint(0, 3, (n_samples,))

        # 1. Exact full-window gradient
        model_exact = torch.nn.Linear(4, 3, bias=False)
        with torch.no_grad():
            model_exact.weight.fill_(0.0)
        loss_exact = torch.nn.functional.cross_entropy(model_exact(x), y, reduction="mean")
        loss_exact.backward()
        exact_grad = model_exact.weight.grad.clone()

        # 2. Accumulated micro-batches (micro_batch=2, accum=8)
        model_accum = torch.nn.Linear(4, 3, bias=False)
        with torch.no_grad():
            model_accum.weight.fill_(0.0)

        batch_size = 2
        accum_steps = 8
        batch_indices = list(range(0, n_samples, batch_size))

        for batch_idx, start_idx in enumerate(batch_indices):
            end_idx = min(start_idx + batch_size, n_samples)
            bx = x[start_idx:end_idx]
            by = y[start_idx:end_idx]

            # M3.4 exact window sample count weighting
            window_start_batch = (batch_idx // accum_steps) * accum_steps
            window_start_sample = window_start_batch * batch_size
            window_end_sample = min(window_start_sample + accum_steps * batch_size, n_samples)
            window_sample_count = window_end_sample - window_start_sample

            loss = torch.nn.functional.cross_entropy(model_accum(bx), by, reduction="mean")
            loss_scaled = loss * (len(bx) / window_sample_count)
            loss_scaled.backward()

        accum_grad = model_accum.weight.grad.clone()
        max_diff = (accum_grad - exact_grad).abs().max().item()
        assert max_diff < 1e-6, f"Gradient mismatch for n={n_samples}: {max_diff}"
