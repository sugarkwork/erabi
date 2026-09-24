from scripts.split_exam_qa_weakness_v1 import split_rows


def make_rows() -> list[dict]:
    rows = []
    serial = 0
    for domain in ("math", "reading"):
        for language in ("ja", "en"):
            for _ in range(20):
                rows.append({"id": f"x{serial}", "group_id": f"g{serial}", "domain": domain, "language": language})
                serial += 1
    return rows


def test_split_is_deterministic_complete_and_group_disjoint():
    rows = make_rows()
    first = split_rows(rows, 7)
    assert first == split_rows(rows, 7)
    assert {name: len(value) for name, value in first.items()} == {"train": 56, "dev": 12, "final_test": 12}
    ids = [{row["id"] for row in first[name]} for name in ("train", "dev", "final_test")]
    assert not ids[0] & ids[1]
    assert not ids[0] & ids[2]
    assert not ids[1] & ids[2]
    assert set().union(*ids) == {row["id"] for row in rows}
    assert all(row["split"] == name for name, values in first.items() for row in values)
