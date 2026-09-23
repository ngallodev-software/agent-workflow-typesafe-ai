"""Compatibility is explicit; semver intuition is not a qualification signal."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def compatibility() -> dict[str, Any]:
    return json.loads(
        files("agent_workflow_typesafe").joinpath("resources/compatibility.json").read_text()
    )


def host_is_verified(host_version: str) -> bool:
    return host_version in compatibility()["agent_workflow"]["verified_products"]

