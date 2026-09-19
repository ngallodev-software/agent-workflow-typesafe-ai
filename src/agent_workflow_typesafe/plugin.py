"""Agent-Workflow public-plugin boundary; import is credential-free and inert."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

from agent_workflow.plugin_api import (
    PluginCommand, PluginDecisionEvidence, PluginDecisionMode, PluginDecisionProvider,
    PluginDescriptor, PluginPackageResource, PluginDecisionRequest, PluginDecisionContext,
)

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
    log_path = str(context.settings.typesafe_api_call_log) if context.settings.typesafe_api_call_log else None
    result = advise_routing(source, context.host_version, model=args.model, log_path=log_path) if args.typesafe_command == "advise-routing" else evaluate_skill(source, context.host_version, model=args.model, log_path=log_path)
    validate_receipt(result)
    return result



_ROUTING_IDS = {
    "routing.task_class": "task_class",
    "routing.interaction_required": "interaction_needed",
    "routing.semantic_risk": "semantic_risk",
}
_SKILL_IDS = {
    "skill.behavior_satisfied": "behavior_supported",
    "skill.completeness": "completeness",
    "skill.actionability": "actionability",
}

def _decision_status(receipt: dict[str, Any]) -> str:
    status = str(receipt.get("status", "service_failure"))
    return {
        "advisory": "success",
        "no_match": "no_match",
        "invalid_input": "invalid_input",
        "unverified_host": "policy_rejected",
        "sdk_or_key_unavailable": "service_failure",
        "service_failure": "service_failure",
    }.get(status, status)

def _decision_provider(request: PluginDecisionRequest, context: PluginDecisionContext) -> dict[str, PluginDecisionEvidence]:
    decision_ids = set(request.decision_ids)
    if decision_ids <= set(_ROUTING_IDS):
        log_path = str(context.settings.typesafe_api_call_log) if context.settings.typesafe_api_call_log else None
        receipt = advise_routing(request.state, context.host_version, log_path=log_path)
        mapping = _ROUTING_IDS
    elif decision_ids <= set(_SKILL_IDS):
        log_path = str(context.settings.typesafe_api_call_log) if context.settings.typesafe_api_call_log else None
        receipt = evaluate_skill(request.state, context.host_version, log_path=log_path)
        mapping = _SKILL_IDS
    else:
        raise ValueError("TypeSafe decision requests may not mix routing and skill question sets")
    status = _decision_status(receipt)
    answers = receipt.get("answers", {}) if isinstance(receipt.get("answers"), dict) else {}
    result: dict[str, PluginDecisionEvidence] = {}
    for decision_id in request.decision_ids:
        answer = answers.get(mapping[decision_id]) if status == "success" else None
        semantic_type = "choice" if decision_id == "routing.task_class" else "noul" if decision_id in {"routing.interaction_required", "skill.behavior_satisfied"} else "score"
        value = confidence = probability = None
        distribution: dict[str, float] = {}
        if isinstance(answer, dict):
            if semantic_type == "choice":
                value = answer.get("choice")
                confidence = answer.get("confidence") if isinstance(answer.get("confidence"), (int, float)) else None
            elif semantic_type == "noul":
                probability = answer.get("probability") if isinstance(answer.get("probability"), (int, float)) else None
                value = probability
            else:
                value = answer.get("score")
                confidence = answer.get("confidence") if isinstance(answer.get("confidence"), (int, float)) else None
            probs = answer.get("probabilities")
            if isinstance(probs, dict):
                distribution = {str(k): float(v) for k, v in probs.items() if isinstance(v, (int, float))}
        result[decision_id] = PluginDecisionEvidence(
            decision_id=decision_id, status=status, semantic_type=semantic_type, value=value,
            confidence=float(confidence) if confidence is not None else None,
            probability=float(probability) if probability is not None else None,
            distribution=distribution, model=receipt.get("model") if isinstance(receipt.get("model"), str) else None,
            question_set_version=str(receipt.get("question_set_version") or ""),
            request_sha256=str(receipt.get("request_sha256") or "") or None,
            source_refs=tuple(str(x) for x in receipt.get("source_refs", []) if isinstance(x, str)),
            error_class=str(receipt.get("error")) if receipt.get("error") else None,
        )
    return result

def plugin() -> PluginDescriptor:
    return PluginDescriptor(
        name="agent-workflow-typesafe",
        version=__version__,
        commands=(PluginCommand("typesafe", "TypeSafe advisory semantic evidence", configure, execute),),
        resources=("agent-workflow-typesafe://compatibility/v1", "agent-workflow-typesafe://semantic-advice/v1alpha1"),
        package_resources=(
            PluginPackageResource("schema", "agent-workflow-typesafe/semantic-advice/v1alpha1", "agent_workflow_typesafe", "resources/semantic-advice-v1alpha1.schema.json", "d5552fab3f2cf759fe9dab5f4079d5a048600cff67ff5ca6399b1e45c6ef48b2"),
            PluginPackageResource("asset", "agent-workflow-typesafe/compatibility/v1", "agent_workflow_typesafe", "resources/compatibility.json", "576b88ee622296d093b95289e13e0fbbcd0d250b48faa3e25d002f040c6efced"),
        ),
        decision_providers=(PluginDecisionProvider(
            "typesafe",
            tuple((*_ROUTING_IDS.keys(), *_SKILL_IDS.keys())),
            _decision_provider,
        ),),
        decision_modes=(
            PluginDecisionMode("typesafe", "TypeSafe semantic evidence consumed by Agent-Workflow policy", "typesafe", "automated"),
            PluginDecisionMode("comparative", "TypeSafe semantic evidence shadowed against deterministic control", "typesafe", "shadow", capture_comparison=True),
        ),
        metadata={"authority": "semantic-evidence-only", "receipt_schema": "semantic-advice/v1alpha1", "decision_policy_owner": "agent-workflow"},
    )
