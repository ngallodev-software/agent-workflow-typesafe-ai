"""Agent-Workflow public-plugin boundary; import is credential-free and inert."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from agent_workflow.plugin_api import PluginCommand, PluginDescriptor, PluginPackageResource

from . import __version__
from .compatibility import compatibility, host_is_verified
from .evaluation import shared_library_status
from .receipts import validate_receipt
from .service import advise_routing, evaluate_skill


def _resource_digest(name: str) -> str:
    return hashlib.sha256(files("agent_workflow_typesafe").joinpath("resources", name).read_bytes()).hexdigest()


def _json_input(path: str) -> dict[str, Any]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def configure(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="typesafe_command", required=True)
    commands.add_parser("compatibility", help="show verified compatibility contract")
    commands.add_parser("doctor", help="report credential-free capability diagnostics")
    for name, help_text in (("advise-routing", "emit advisory routing evidence"), ("evaluate-skill", "emit advisory skill evidence")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--input", required=True, help="bounded JSON input path")
        command.add_argument("--model")


def execute(args: argparse.Namespace, context: Any) -> dict[str, Any]:
    if args.typesafe_command == "compatibility":
        return compatibility()
    if args.typesafe_command == "doctor":
        import importlib.util
        import os
        return {"plugin": "agent-workflow-typesafe", "host_version": context.host_version, "host_verified": host_is_verified(context.host_version), "typesafe_sdk_installed": importlib.util.find_spec("typesafe_sdk") is not None, "api_key_configured": bool(os.environ.get("TYPESAFE_API_KEY")), "semantic_execution": "available" if host_is_verified(context.host_version) else "refused_unverified_host", "comparative_evaluation": shared_library_status()}
    source = _json_input(args.input)
    result = advise_routing(source, context.host_version, model=args.model) if args.typesafe_command == "advise-routing" else evaluate_skill(source, context.host_version, model=args.model)
    validate_receipt(result)
    return result


def plugin() -> PluginDescriptor:
    return PluginDescriptor(
        name="agent-workflow-typesafe",
        version=__version__,
        commands=(PluginCommand("typesafe", "TypeSafe advisory semantic evidence", configure, execute),),
        resources=("agent-workflow-typesafe://compatibility/v1", "agent-workflow-typesafe://semantic-advice/v1alpha1"),
        package_resources=(
            PluginPackageResource("schema", "agent-workflow-typesafe/semantic-advice/v1alpha1", "agent_workflow_typesafe", "resources/semantic-advice-v1alpha1.schema.json", "d5552fab3f2cf759fe9dab5f4079d5a048600cff67ff5ca6399b1e45c6ef48b2"),
            PluginPackageResource("asset", "agent-workflow-typesafe/compatibility/v1", "agent_workflow_typesafe", "resources/compatibility.json", "089c8fddcc8bb76205bcff748b87d0fd6d21f2eab44578dbbd8795881fff5e03"),
        ),
        metadata={"authority": "advisory-only", "receipt_schema": "semantic-advice/v1alpha1"},
    )
