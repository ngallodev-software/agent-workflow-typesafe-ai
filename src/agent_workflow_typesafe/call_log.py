"""Opt-in, bounded logging for TypeSafe API calls."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ENV = "TYPESAFE_API_CALL_LOG"
_SECRET_KEYS = {"authorization", "api_key", "apikey", "token", "password", "secret"}
_MAX_TEXT = 8_000
_MAX_ITEMS = 100
_MAX_DEPTH = 8


def enabled() -> bool:
    """Whether the opt-in JSONL sink is configured."""
    return bool(os.environ.get(_ENV, "").strip())


def _safe(value: Any, *, key: str = "", depth: int = 0) -> Any:
    normalized_key = key.lower().replace("-", "_")
    if normalized_key in _SECRET_KEYS or any(marker in normalized_key for marker in ("api_key", "apikey", "authorization", "password", "secret", "token")):
        return "[redacted]"
    if depth >= _MAX_DEPTH:
        return "[depth_limit]"
    if isinstance(value, str):
        return value[:_MAX_TEXT]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, dict):
        return {
            str(name)[:200]: _safe(item, key=str(name), depth=depth + 1)
            for name, item in list(value.items())[:_MAX_ITEMS]
        }
    if isinstance(value, (list, tuple)):
        return [_safe(item, depth=depth + 1) for item in value[:_MAX_ITEMS]]
    return f"[unsupported:{type(value).__name__}]"


def record(*, kind: str, request_sha256: str, question_set_version: str,
           host_version: str, requested_model: str | None, state: object,
           questions: object, status: str, resolved_model: str | None = None,
           outputs: object | None = None, error_class: str | None = None,
           duration_ms: float | None = None, path: str | None = None) -> None:
    """Append one sanitized call record; logging is disabled by default."""
    path_text = (path or os.environ.get(_ENV, "")).strip()
    if not path_text:
        return
    try:
        payload: dict[str, Any] = {
            "schema": "agent-workflow-typesafe/typesafe-api-call/v1",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            "request_sha256": request_sha256,
            "question_set_version": question_set_version,
            "host_version": host_version,
            "requested_model": requested_model,
            "resolved_model": resolved_model,
            "input": {"state": _safe(state), "questions": _safe(questions)},
            "output": _safe(outputs),
            "status": status,
        }
        if error_class:
            payload["error_class"] = error_class
        if duration_ms is not None:
            payload["duration_ms"] = round(max(0.0, duration_ms), 3)
        path = Path(path_text)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    except (OSError, TypeError, ValueError):
        return
