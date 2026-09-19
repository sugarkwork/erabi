"""CPU gradient accumulation verification script for ERABI M3.4.

Verifies that the micro-batch loss weighting:
    loss_scaled = loss * (len(batch_records) / window_sample_count)
produces mathematically identical parameter gradients (within 1e-6 tolerance)
to computing the full-window batch mean in a single forward/backward pass.

Tests 5 scenarios:
1. Normal window: 16 samples, micro_batch=2, accum=8 (2x8)
2. Partial/tail window: 8 samples, micro_batch=2, accum=8 (2x4)
3. Fractional last micro-batch: 15 samples, micro_batch=2, accum=8 (2x7 + 1x1)
4. Multi-window with tail: 23 samples, micro_batch=2, accum=8 (16 full + 7 tail)
5. Accumulation = 1: 8 samples, micro_batch=8, accum=1

Saves results to runs/m3_4_gradfix/gradient_check.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import torch
import torch.nn as nn

ROOT_DIR = Path(__file__).resolve().parent.parent


class TinyLinearModel(nn.Module):
    """Deterministic linear classification model for CPU gradient verification."""

    def __init__(self, in_features: int = 4, num_classes: int = 3):
        super().__init__()
        self.fc = nn.Linear(in_features, num_classes, bias=False)
        # Initialize weights deterministically
        with torch.no_grad():
            self.fc.weight.fill_(0.0)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc(x)


def compute_accumulated_gradients(
    samples_x: torch.Tensor,
    samples_y: torch.Tensor,
    micro_batch_size: int,
    gradient_accumulation_steps: int,
    mode: str = "fixed",  # "fixed" (M3.4 fix), "old" (M3.3 bug)
) -> Tuple[torch.Tensor, List[float]]:
    """Simulate training accumulation loop."""
    model = TinyLinearModel(in_features=samples_x.size(1), num_classes=3)
    loss_fn = nn.CrossEntropyLoss(reduction="mean")

    total_samples = samples_x.size(0)
    batch_indices = list(range(0, total_samples, micro_batch_size))
    total_micro_batches = len(batch_indices)

    recorded_losses = []

    for batch_idx, start_idx in enumerate(batch_indices):
        end_idx = min(start_idx + micro_batch_size, total_samples)
        batch_x = samples_x[start_idx:end_idx]
        batch_y = samples_y[start_idx:end_idx]
        batch_count = end_idx - start_idx

        # Forward
        logits = model(batch_x)
        loss = loss_fn(logits, batch_y)
        recorded_losses.append(loss.item())

        if mode == "fixed":
            # M3.4 fixed formula
            window_start_batch = (batch_idx // gradient_accumulation_steps) * gradient_accumulation_steps
            window_start_sample = window_start_batch * micro_batch_size
            window_end_sample = min(
                window_start_sample + gradient_accumulation_steps * micro_batch_size,
                total_samples,
            )
            window_sample_count = window_end_sample - window_start_sample
            loss_scaled = loss * (batch_count / window_sample_count)
        elif mode == "old":
            # M3.3 buggy formula
            window_offset = batch_idx % gradient_accumulation_steps
            remaining_in_window = gradient_accumulation_steps - window_offset
            remaining_in_epoch = total_micro_batches - batch_idx
            current_window_size = min(remaining_in_window, remaining_in_epoch)
            loss_scaled = loss / current_window_size
        else:
            raise ValueError(f"Unknown mode: {mode}")

        loss_scaled.backward()

    grad = model.fc.weight.grad.clone()
    return grad, recorded_losses


def compute_exact_window_gradient(
    samples_x: torch.Tensor,
    samples_y: torch.Tensor,
) -> torch.Tensor:
    """Compute exact gradient from a single forward-backward pass of the full window mean."""
    model = TinyLinearModel(in_features=samples_x.size(1), num_classes=3)
    loss_fn = nn.CrossEntropyLoss(reduction="mean")

    logits = model(samples_x)
    loss = loss_fn(logits, samples_y)
    loss.backward()

    return model.fc.weight.grad.clone()


def main():
    print("=== Running CPU Gradient Accumulation Verification ===")
    torch.manual_seed(42)

    # Scenarios to test
    scenarios = [
        {
            "name": "1. Normal Window (16 samples: 2x8)",
            "num_samples": 16,
            "micro_batch_size": 2,
            "accum_steps": 8,
        },
        {
            "name": "2. Partial Tail Window (8 samples: 2x4)",
            "num_samples": 8,
            "micro_batch_size": 2,
            "accum_steps": 8,
        },
        {
            "name": "3. Fractional Tail (15 samples: 2x7 + 1x1)",
            "num_samples": 15,
            "micro_batch_size": 2,
            "accum_steps": 8,
        },
        {
            "name": "4. Multi-Window with Tail (23 samples: 16 full + 7 tail)",
            "num_samples": 23,
            "micro_batch_size": 2,
            "accum_steps": 8,
        },
        {
            "name": "5. Accumulation=1 (8 samples: 8x1)",
            "num_samples": 8,
            "micro_batch_size": 8,
            "accum_steps": 1,
        },
    ]

    results = []

    for sc in scenarios:
        n = sc["num_samples"]
        mbs = sc["micro_batch_size"]
        accum = sc["accum_steps"]

        # Deterministic diverse synthetic dataset
        x = torch.randn(n, 4, dtype=torch.float32)
        y = torch.randint(0, 3, (n,), dtype=torch.long)

        # 1. Exact full-window gradient
        # If multi-window, exact gradient is computed per window
        total_batches = (n + mbs - 1) // mbs
        exact_grads = []
        for w_start in range(0, n, accum * mbs):
            w_end = min(w_start + accum * mbs, n)
            wx = x[w_start:w_end]
            wy = y[w_start:w_end]
            exact_grads.append(compute_exact_window_gradient(wx, wy))

        # 2. Fixed implementation (simulated)
        fixed_grad_total, fixed_losses = compute_accumulated_gradients(x, y, mbs, accum, mode="fixed")

        # 3. Old buggy implementation (simulated)
        old_grad_total, old_losses = compute_accumulated_gradients(x, y, mbs, accum, mode="old")

        # For single window (scenarios 1, 2, 3, 5), compare directly with exact_grads[0]
        if len(exact_grads) == 1:
            exact = exact_grads[0]
            max_diff_fixed = (fixed_grad_total - exact).abs().max().item()
            max_diff_old = (old_grad_total - exact).abs().max().item()
            fixed_matches = max_diff_fixed < 1e-6
            old_matches = max_diff_old < 1e-6
        else:
            # Multi-window: sum of window gradients
            exact_sum = sum(exact_grads)
            max_diff_fixed = (fixed_grad_total - exact_sum).abs().max().item()
            max_diff_old = (old_grad_total - exact_sum).abs().max().item()
            fixed_matches = max_diff_fixed < 1e-6
            old_matches = max_diff_old < 1e-6

        res_entry = {
            "scenario": sc["name"],
            "num_samples": n,
            "micro_batch_size": mbs,
            "accum_steps": accum,
            "fixed_implementation_matches_exact": fixed_matches,
            "fixed_max_abs_diff": max_diff_fixed,
            "old_implementation_matches_exact": old_matches,
            "old_max_abs_diff": max_diff_old,
        }
        results.append(res_entry)
        print(f"\n{sc['name']}:")
        print(f"  Fixed matches exact: {fixed_matches} (max diff: {max_diff_fixed:.2e})")
        print(f"  Old matches exact:   {old_matches} (max diff: {max_diff_old:.2e})")

    all_fixed_passed = all(r["fixed_implementation_matches_exact"] for r in results)
    print(f"\nAll fixed scenarios passed: {all_fixed_passed}")

    # Output to runs/m3_4_gradfix/gradient_check.json
    out_dir = ROOT_DIR / "runs" / "m3_4_gradfix"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "gradient_check.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "all_passed": all_fixed_passed,
            "tolerance": 1e-6,
            "results": results,
        }, f, indent=2)

    print(f"Saved gradient check results to: {out_file}")


if __name__ == "__main__":
    main()
