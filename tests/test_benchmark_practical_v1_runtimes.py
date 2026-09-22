"""Small offline checks for the reproducible runtime benchmark helpers."""

import json

from scripts.benchmark_practical_v1_runtimes import load_stratified, percentile


def test_load_stratified_balances_family_and_language(tmp_path):
    path = tmp_path / "cases.jsonl"
    rows = [
        {"id": "a1", "family": "a", "language": "ja"},
        {"id": "a2", "family": "a", "language": "ja"},
        {"id": "b1", "family": "b", "language": "en"},
        {"id": "b2", "family": "b", "language": "en"},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    assert [row["id"] for row in load_stratified(path, 3)] == ["a1", "b1", "a2"]


def test_percentile_uses_linear_interpolation():
    assert percentile([1.0, 2.0, 3.0, 4.0], 0.5) == 2.5
