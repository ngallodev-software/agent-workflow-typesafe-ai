"""Secret-free, application-owned semantic evidence receipts."""

from __future__ import annotations

from typing import Any, Mapping

from .policy import outcome


SCHEMA = "semantic-advice/v1alpha1"


def receipt(*, kind: str, question_set_version: str, request_sha256: str, source_refs: list[str], host_version: str, status: str, fallback: str, answers: Mapping[str, object] | None = None, model: str | None = None, error: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "kind": kind,
        "question_set_version": question_set_version,
        "request_sha256": request_sha256,
        "source_refs": sorted(set(source_refs)),
        "host_version": host_version,
        "status": status,
        "fallback": fallback,
        "policy_outcome": outcome({}),
        "advisory": True,
        "answers": dict(answers or {}),
        "model": model,
    }
    if error:
        result["error"] = error
    return result


def validate_receipt(value: Mapping[str, object]) -> None:
    required = {"schema", "kind", "question_set_version", "request_sha256", "source_refs", "host_version", "status", "fallback", "policy_outcome", "advisory", "answers", "model"}
    if set(value) - (required | {"error"}) or required - set(value):
        raise ValueError("receipt has an invalid field set")
    if value["schema"] != SCHEMA or value["policy_outcome"] != "no_action" or value["advisory"] is not True:
        raise ValueError("receipt authority boundary is invalid")
    if not isinstance(value["request_sha256"], str) or len(value["request_sha256"]) != 64:
        raise ValueError("receipt request hash is invalid")
    if not isinstance(value["source_refs"], list) or not isinstance(value["answers"], dict):
        raise ValueError("receipt provenance or answers are invalid")
