"""Application policy boundary: every semantic result remains advisory no-action evidence."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from .client import DecisionClient, TypeSafeDecisionClient, normalize_response
from .compatibility import host_is_verified
from .projection import project_routing, project_skill, request_hash
from .questions import ROUTING_VERSION, SKILL_VERSION, routing_questions, skill_questions
from .receipts import receipt


def _advise(kind: str, source: Mapping[str, object], host_version: str, *, model: str | None = None, client: DecisionClient | None = None) -> dict[str, Any]:
    projector, questions, version = (project_routing, routing_questions(), ROUTING_VERSION) if kind == "routing" else (project_skill, skill_questions(), SKILL_VERSION)
    try:
        state, source_refs = projector(source)
    except ValueError as exc:
        return receipt(kind=kind, question_set_version=version, request_sha256="0" * 64, source_refs=[], host_version=host_version, status="invalid_input", fallback="no_action", error=str(exc))
    digest = request_hash(state, questions, version, model)
    if not host_is_verified(host_version):
        return receipt(kind=kind, question_set_version=version, request_sha256=digest, source_refs=source_refs, host_version=host_version, status="unverified_host", fallback="no_action")
    if client is None and not os.environ.get("TYPESAFE_API_KEY"):
        return receipt(kind=kind, question_set_version=version, request_sha256=digest, source_refs=source_refs, host_version=host_version, status="sdk_or_key_unavailable", fallback="no_action")
    try:
        resolved_model, answers = normalize_response((client or TypeSafeDecisionClient()).system_one(state, questions, model))
    except Exception as exc:
        return receipt(kind=kind, question_set_version=version, request_sha256=digest, source_refs=source_refs, host_version=host_version, status="service_failure", fallback="no_action", error=type(exc).__name__)
    status = "no_match" if any(answer.get("choice") == "other" for answer in answers.values() if isinstance(answer, dict)) else "advisory"
    return receipt(kind=kind, question_set_version=version, request_sha256=digest, source_refs=source_refs, host_version=host_version, status=status, fallback="no_action", answers=answers, model=resolved_model)


def advise_routing(source: Mapping[str, object], host_version: str, *, model: str | None = None, client: DecisionClient | None = None) -> dict[str, Any]:
    return _advise("routing", source, host_version, model=model, client=client)


def evaluate_skill(source: Mapping[str, object], host_version: str, *, model: str | None = None, client: DecisionClient | None = None) -> dict[str, Any]:
    return _advise("skill_evaluation", source, host_version, model=model, client=client)

