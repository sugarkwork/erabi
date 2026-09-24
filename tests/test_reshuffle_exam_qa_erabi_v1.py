from scripts.reshuffle_exam_qa_erabi_v1 import OFFICIAL_KIND, make_splits


def record(group: str, index: int, language: str = "ja", generated: bool = False) -> dict:
    return {
        "id": f"r-{group}-{index}",
        "group_id": group,
        "language": language,
        "source": {"source_id": f"s-{group}-{index}"},
        "provenance": {"transform_kind": "deepseek_distractors_official_target" if generated else OFFICIAL_KIND},
    }


def test_three_way_split_is_deterministic_disjoint_and_holdouts_are_official_only():
    rows = []
    for index in range(20):
        language = "ja" if index % 2 == 0 else "en"
        rows.extend([record(f"g-{index}", 0, language), record(f"g-{index}", 1, language, generated=index % 3 == 0)])
    pilot = {"s-g-0-0"}
    one, manifest_one = make_splits(rows, pilot, seed=17)
    two, manifest_two = make_splits(rows, pilot, seed=17)
    assert one == two
    assert manifest_one == manifest_two
    groups = {name: {row["group_id"] for row in one[name]} for name in ("train", "dev", "final_test")}
    assert groups["train"].isdisjoint(groups["dev"] | groups["final_test"])
    assert groups["dev"].isdisjoint(groups["final_test"])
    assert "g-0" in groups["train"]
    assert all(row["provenance"]["transform_kind"] == OFFICIAL_KIND for name in ("dev", "final_test") for row in one[name])
    assert manifest_one["counts"]["train"] + manifest_one["counts"]["dev"] + manifest_one["counts"]["final_test"] + manifest_one["counts"]["excluded"] == len(rows)
