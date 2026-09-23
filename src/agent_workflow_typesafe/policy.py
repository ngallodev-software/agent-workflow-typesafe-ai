"""The sole v0.1.0 policy: semantic evidence may not cause an action."""

from __future__ import annotations

from collections.abc import Mapping


def outcome(_: Mapping[str, object]) -> str:
    return "no_action"
