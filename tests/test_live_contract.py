"""Explicit opt-in only; this suite must never make a default network call."""

from __future__ import annotations

import os

import pytest

from agent_workflow_typesafe.service import advise_routing


pytestmark = pytest.mark.skipif(
    os.environ.get("TYPESAFE_LIVE_TEST") != "1" or not os.environ.get("TYPESAFE_API_KEY"),
    reason="requires explicit TYPESAFE_LIVE_TEST=1 and TYPESAFE_API_KEY",
)


def test_live_result_stays_advisory() -> None:
    result = advise_routing({"task": "classify this bounded request", "source_refs": ["live-contract"]}, "0.10.0")
    assert result["policy_outcome"] == "no_action"
    assert result["advisory"] is True

