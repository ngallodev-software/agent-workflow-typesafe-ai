"""Opt-in plugin-side candidate telemetry adapter.

It accepts the already projected state used by the service and returns the
normal advisory receipt plus bounded timing/version metadata. It never imports
Agent-Workflow internals or writes host lifecycle state.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from .service import advise_routing, evaluate_skill


def evaluate_candidate(
    kind: str,
    source: Mapping[str, object],
    host_version: str,
    *,
    model: str | None = None,
    client: Any = None,
) -> dict[str, Any]:
    if kind not in {"routing", "skill_evaluation"}:
        raise ValueError("unsupported candidate kind")
    started = time.perf_counter()
    fn = advise_routing if kind == "routing" else evaluate_skill
    receipt = fn(source, host_version, model=model, client=client)
    result: dict[str, Any] = {
        "receipt": receipt,
        "feature_id": "routing-advice/v1" if kind == "routing" else "skill-behavior-eval/v1",
        "question_set_version": receipt["question_set_version"],
        "model": receipt.get("model"),
        "duration_seconds": time.perf_counter() - started,
        "provider_elapsed_seconds": None,
        "first_output_latency_seconds": None,
        "usage": {},
        "error_class": receipt.get("error") if receipt.get("status") == "service_failure" else None,
    }
    return result
