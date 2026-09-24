from scripts.train_exam_qa_weakness_v1 import production_candidate, retention_pass, select_replay


def metrics(weak_dev=0.5, weak_final=0.5, practical_dev=0.8, practical_eval=0.8, bridge=0.85, exam_dev=0.35, exam_final=0.35):
    return {
        "weakness_dev": {"accuracy": weak_dev},
        "weakness_final": {"accuracy": weak_final},
        "practical_dev": {"accuracy": practical_dev},
        "practical_eval": {"accuracy": practical_eval},
        "bridge": {"accuracy": bridge},
        "original_exam_dev": {"accuracy": exam_dev},
        "original_exam_final": {"accuracy": exam_final},
    }


def test_replay_is_deterministic_and_does_not_mutate_source():
    source = [{"id": f"x{i}", "group_id": f"g{i}", "split": "train"} for i in range(10)]
    selected = select_replay(source, 4, 7)
    assert selected == select_replay(source, 4, 7)
    assert all(row["id"].startswith("weakness_replay_") for row in selected)
    assert source[0]["id"] == "x0"


def test_promotion_requires_final_gain_and_retention():
    baseline = metrics()
    candidate = metrics(weak_dev=0.55, weak_final=0.56, practical_dev=0.79, practical_eval=0.795, bridge=0.84, exam_dev=0.34, exam_final=0.34)
    assert retention_pass(baseline, candidate)
    assert production_candidate(baseline, candidate)
    candidate["bridge"]["accuracy"] = 0.82
    assert not production_candidate(baseline, candidate)
