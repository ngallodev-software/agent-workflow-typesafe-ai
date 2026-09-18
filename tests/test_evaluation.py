from __future__ import annotations

from types import SimpleNamespace

from agent_workflow_typesafe.evaluation import load_corpus, run_static_cases, validate_observation
from agent_workflow_typesafe.telemetry import evaluate_candidate


def test_static_runner_is_control_authoritative_and_reproducible_shape() -> None:
    cases = [{"case_id": "C1", "dataset_version": "v1", "task": "review"}]
    result = run_static_cases(cases, feature_id="routing-advice/v1", control=lambda _: {"route": "review"}, candidate=lambda _: {"route": "implementation"}, repetitions=2)
    assert len(result) == 2
    for item in result:
        validate_observation(item)
        assert item["comparison"]["candidate_applied"] is False
        assert item["comparison"]["authoritative_arm"] == "control"
        assert item["input"]["raw_input_persisted"] is False


def test_shipped_corpora_are_versioned_and_synthetic() -> None:
    cases = load_corpus("routing-v1")
    assert cases and all(case["dataset_version"] == "routing-v1.0.0" for case in cases)


def test_candidate_telemetry_is_bounded_and_uses_existing_advisory_service() -> None:
    class FakeClient:
        def system_one(self, state, questions, model=None):
            return SimpleNamespace(model="fake", answers={"task_class": SimpleNamespace(choice="review", confidence=1.0, probabilities={"review": 1.0})})

    result = evaluate_candidate("routing", {"task": "review this", "source_refs": ["C1"]}, "0.10.1", client=FakeClient())
    assert result["feature_id"] == "routing-advice/v1"
    assert result["receipt"]["policy_outcome"] == "no_action"
    assert result["usage"] == {}
    assert "review this" not in str(result)
