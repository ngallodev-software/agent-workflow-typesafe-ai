"""Secret-free comparative evaluation helpers.

These helpers record control/candidate evidence without changing plugin policy.
The candidate is never applied to Agent-Workflow authority; callers own the
control result and may use this module only for static or shadow observations.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from importlib.resources import files

OBSERVATION_SCHEMA = "agent-workflow-typesafe/comparison-observation/v1"


def load_corpus(name: str) -> list[dict[str, Any]]:
    """Load a shipped, frozen synthetic corpus by name."""
    if name not in {"routing-v1", "skill-behavior-v1"}:
        raise ValueError("unknown evaluation corpus")
    value = json.loads(files("agent_workflow_typesafe").joinpath("resources", "evaluation", f"{name}.json").read_text())
    cases = value.get("cases")
    if not isinstance(cases, list) or not all(isinstance(case, dict) for case in cases):
        raise ValueError("evaluation corpus is invalid")
    return [dict(case, dataset_version=value["dataset_version"]) for case in cases]


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _arm(call: Callable[[], Mapping[str, Any]] | None) -> dict[str, Any]:
    if call is None:
        return {"status": "not_applicable", "duration_seconds": None, "result": None, "usage": {}}
    started = time.perf_counter()
    try:
        result = dict(call())
    except TimeoutError:
        return {"status": "timeout", "duration_seconds": time.perf_counter() - started, "result": None, "usage": {}}
    except Exception as exc:  # deliberately classify, never serialize exception text
        return {"status": "error", "duration_seconds": time.perf_counter() - started, "result": None, "usage": {}, "error_class": type(exc).__name__}
    duration = time.perf_counter() - started
    arm = {"status": "success", "duration_seconds": duration, "result": result, "usage": {}}
    for key in ("provider_elapsed_seconds", "first_output_latency_seconds", "usage"):
        if key in result and key != "usage":
            value = result[key]
            if isinstance(value, (int, float)) and value >= 0:
                arm[key] = float(value)
        elif key == "usage" and isinstance(result.get(key), Mapping):
            # Usage is accepted only as already-normalized numeric/null fields.
            arm[key] = {str(name): value for name, value in result[key].items() if value is None or isinstance(value, (int, float))}
    return arm


def observation(
    *,
    feature_id: str,
    mode: str,
    identity: Mapping[str, Any],
    source_input: Mapping[str, Any],
    projected_input: Mapping[str, Any],
    control: Callable[[], Mapping[str, Any]] | None,
    candidate: Callable[[], Mapping[str, Any]] | None,
    case_id: str | None = None,
    data_class: str = "synthetic",
    observation_id: str | None = None,
) -> dict[str, Any]:
    control_arm = _arm(control)
    candidate_arm = _arm(candidate)
    control_result = control_arm.get("result")
    candidate_result = candidate_arm.get("result")
    agreement = None if control_result is None or candidate_result is None else control_result == candidate_result
    return {
        "schema": OBSERVATION_SCHEMA,
        "observation_id": observation_id or str(uuid.uuid4()),
        "feature_id": feature_id,
        "mode": mode,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "identity": dict(identity),
        "input": {"case_id": case_id, "input_sha256": sha256(source_input), "projection_sha256": sha256(projected_input), "raw_input_persisted": False},
        "control": control_arm,
        "candidate": candidate_arm,
        "comparison": {"candidate_applied": False, "authoritative_arm": "control", "agreement": agreement, "normalized_control": control_result, "normalized_candidate": candidate_result},
        "privacy": {"data_class": data_class, "raw_content_stored": False, "secret_values_stored": False},
    }


def validate_observation(value: Mapping[str, Any]) -> None:
    required = {"schema", "observation_id", "feature_id", "mode", "recorded_at", "identity", "input", "control", "candidate", "comparison", "privacy"}
    if set(value) != required or value.get("schema") != OBSERVATION_SCHEMA:
        raise ValueError("invalid comparison observation fields")
    if value["comparison"].get("candidate_applied") is not False or value["comparison"].get("authoritative_arm") != "control":
        raise ValueError("candidate must remain unapplied and control-authoritative")
    if value["input"].get("raw_input_persisted") is not False or value["privacy"].get("raw_content_stored") is not False or value["privacy"].get("secret_values_stored") is not False:
        raise ValueError("observation privacy boundary is invalid")
    for name in ("input_sha256", "projection_sha256"):
        digest = value["input"].get(name)
        if not isinstance(digest, str) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValueError("observation input digest is invalid")


def run_static_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    feature_id: str,
    control: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    candidate: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    repetitions: int = 1,
) -> list[dict[str, Any]]:
    if repetitions < 1:
        raise ValueError("repetitions must be positive")
    observations: list[dict[str, Any]] = []
    for case in cases:
        case_id = case.get("case_id")
        for repetition in range(repetitions):
            identity = {"dataset_version": case.get("dataset_version", "unknown"), "repetition": repetition}
            observations.append(observation(feature_id=feature_id, mode="static", identity=identity, source_input=case, projected_input=case, case_id=case_id if isinstance(case_id, str) else None, control=lambda case=case: control(case), candidate=lambda case=case: candidate(case)))
    return observations
