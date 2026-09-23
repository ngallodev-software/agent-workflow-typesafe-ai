from __future__ import annotations

from types import SimpleNamespace

from agent_workflow_typesafe.evaluation import (
    CANONICAL_OBSERVATION_SCHEMA,
    LEGACY_OBSERVATION_SCHEMA,
    load_corpus,
    neutral_observation,
    run_static_cases,
    shared_library_status,
    validate_observation,
)
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


def test_base_install_uses_explicit_legacy_compatibility_backend() -> None:
    status = shared_library_status()
    assert status["distribution"] == "agent-workflow-comparative-eval"
    assert status["specifier"] == "==0.1.0"
    if not status["installed"]:
        assert status["backend"] == "legacy-compatibility"


def test_shared_library_facade_delegates_and_preserves_legacy_schema(monkeypatch) -> None:
    import sys
    from types import ModuleType
    import agent_workflow_typesafe.evaluation as evaluation

    fake = ModuleType("agent_workflow_comparative_eval")
    fake.__version__ = "0.1.0"
    fake.load_corpus = lambda name: [{"case_id": "shared", "dataset_version": "routing-v1.0.0"}]
    fake.sha256 = lambda value: "a" * 64
    fake.observation = lambda **kwargs: {
        "schema": CANONICAL_OBSERVATION_SCHEMA,
        "observation_id": kwargs.get("observation_id") or "shared-observation",
        "feature_id": kwargs["feature_id"],
        "mode": kwargs["mode"],
        "recorded_at": "2026-09-18T00:00:00+00:00",
        "identity": dict(kwargs["identity"]),
        "input": {"case_id": kwargs.get("case_id"), "input_sha256": "b" * 64, "projection_sha256": "c" * 64, "raw_input_persisted": False},
        "control": {"status": "success", "duration_seconds": 0.1, "result": {"route": "review"}, "usage": {}},
        "candidate": {"status": "success", "duration_seconds": 0.2, "result": {"route": "review"}, "usage": {}},
        "comparison": {"candidate_applied": False, "authoritative_arm": "control", "agreement": True, "normalized_control": {"route": "review"}, "normalized_candidate": {"route": "review"}},
        "privacy": {"data_class": "synthetic", "raw_content_stored": False, "secret_values_stored": False},
    }
    fake.validate_observation = lambda value: None
    fake.run_static_cases = lambda cases, **kwargs: [fake.observation(feature_id=kwargs["feature_id"], mode="static", identity={"dataset_version": "v1", "repetition": 0}, source_input=cases[0], projected_input=cases[0], control=None, candidate=None, case_id=cases[0].get("case_id"))]
    monkeypatch.setitem(sys.modules, "agent_workflow_comparative_eval", fake)

    assert evaluation.shared_library_status()["backend"] == "shared"
    assert evaluation.load_corpus("routing-v1")[0]["case_id"] == "shared"
    legacy = evaluation.observation(feature_id="routing-advice/v1", mode="static", identity={}, source_input={}, projected_input={}, control=None, candidate=None)
    assert legacy["schema"] == LEGACY_OBSERVATION_SCHEMA
    neutral = neutral_observation(feature_id="routing-advice/v1", mode="static", identity={}, source_input={}, projected_input={}, control=None, candidate=None)
    assert neutral["schema"] == CANONICAL_OBSERVATION_SCHEMA


def test_neutral_api_requires_eval_extra_when_shared_library_missing(monkeypatch) -> None:
    import agent_workflow_typesafe.evaluation as evaluation
    monkeypatch.setattr(evaluation, "_shared_module", lambda: None)
    try:
        evaluation.neutral_observation(feature_id="routing-advice/v1", mode="static", identity={}, source_input={}, projected_input={}, control=None, candidate=None)
    except RuntimeError as exc:
        assert "[eval]" in str(exc)
    else:
        raise AssertionError("neutral API must require the shared comparative-eval package")
