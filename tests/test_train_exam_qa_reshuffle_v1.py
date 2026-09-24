from scripts.train_exam_qa_reshuffle_v1 import production_candidate, retention_pass, select_replay


def metrics(exam=0.5, practical_dev=0.8, practical_eval=0.75, bridge=0.9):
    return {
        "dev": {"accuracy": exam},
        "final_test": {"accuracy": exam},
        "practical_dev": {"accuracy": practical_dev},
        "practical_eval": {"accuracy": practical_eval},
        "bridge": {"accuracy": bridge},
    }


def test_replay_is_deterministic_and_renamed():
    rows = [{"id": str(i), "group_id": str(i)} for i in range(10)]
    assert select_replay(rows, 4, 7) == select_replay(rows, 4, 7)
    assert all(row["id"].startswith("reshuffle_replay_") for row in select_replay(rows, 4, 7))


def test_production_gate_requires_meaningful_final_gain_and_retention():
    baseline = metrics()
    assert retention_pass(baseline, metrics(exam=0.6, practical_dev=0.79, bridge=0.89))
    assert production_candidate(baseline, metrics(exam=0.56, practical_dev=0.79, practical_eval=0.745, bridge=0.89))
    assert not production_candidate(baseline, metrics(exam=0.54, practical_dev=0.79, practical_eval=0.745, bridge=0.89))
    assert not production_candidate(baseline, metrics(exam=0.56, practical_dev=0.79, practical_eval=0.73, bridge=0.89))
