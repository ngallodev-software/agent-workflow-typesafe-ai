"""Deterministic bounded state projection; raw caller state never enters a receipt."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

_SECRET_KEYS = {"authorization", "api_key", "apikey", "token", "password", "secret"}
_MAX_TEXT = 8_000


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def request_hash(state: Mapping[str, object], questions: Mapping[str, object], version: str, model: str | None) -> str:
    payload = {"state": state, "questions": questions, "question_set_version": version, "requested_model": model}
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()


def _safe(value: Any, *, key: str = "") -> Any:
    if key.lower().replace("-", "_") in _SECRET_KEYS:
        return "[redacted]"
    if isinstance(value, str):
        return value[:_MAX_TEXT]
    if isinstance(value, list):
        return [_safe(item) for item in value[:100]]
    if isinstance(value, dict):
        return {str(name): _safe(item, key=str(name)) for name, item in value.items()}
    return value


def project_routing(source: Mapping[str, object]) -> tuple[dict[str, object], list[str]]:
    text = source.get("task") or source.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("routing input requires non-empty task or text")
    refs = source.get("source_refs", [])
    if not isinstance(refs, list) or not all(isinstance(item, str) for item in refs):
        raise ValueError("source_refs must be a list of stable strings")
    return {"task": _safe(text), "declared_metadata": _safe(source.get("metadata", {}))}, list(refs)


def project_skill(source: Mapping[str, object]) -> tuple[dict[str, object], list[str]]:
    required = ("scenario_id", "requirement", "skill_text")
    if not all(isinstance(source.get(name), str) and source[name].strip() for name in required):
        raise ValueError("skill input requires scenario_id, requirement, and skill_text")
    refs = source.get("source_refs", [source["scenario_id"]])
    if not isinstance(refs, list) or not all(isinstance(item, str) for item in refs):
        raise ValueError("source_refs must be a list of stable strings")
    return {name: _safe(source[name]) for name in required}, list(refs)

