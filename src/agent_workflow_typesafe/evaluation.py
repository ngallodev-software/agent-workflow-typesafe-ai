"""Compatibility facade for comparative evaluation.

The canonical implementation is the optional ``agent-workflow-comparative-eval``
shared library.  The base plugin remains lightweight: when that optional package
is absent this module falls back to the frozen 0.1.0 implementation so existing
``agent_workflow_typesafe.evaluation`` imports keep working during the 0.1.x
migration window.

New integrations should install ``agent-workflow-typesafe[eval]`` and consume
neutral shared-library artifacts.  Legacy TypeSafe schema IDs are retained here
only as a compatibility surface.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from . import _legacy_evaluation as _legacy

SHARED_LIBRARY_DISTRIBUTION = "agent-workflow-comparative-eval"
SHARED_LIBRARY_IMPORT = "agent_workflow_comparative_eval"
SHARED_LIBRARY_SPECIFIER = "==0.1.0"
SHARED_LIBRARY_VERSION = "0.1.0"
LEGACY_OBSERVATION_SCHEMA = "agent-workflow-typesafe/comparison-observation/v1"
CANONICAL_OBSERVATION_SCHEMA = "agent-workflow-comparative-eval/comparison-observation/v1"
OBSERVATION_SCHEMA = LEGACY_OBSERVATION_SCHEMA


def _shared_module() -> Any | None:
    try:
        module = importlib.import_module(SHARED_LIBRARY_IMPORT)
    except ImportError as exc:
        # Only suppress absence of the optional top-level package. Import
        # failures inside an installed shared library are real installation
        # errors and must remain visible.
        if exc.name == SHARED_LIBRARY_IMPORT:
            return None
        raise
    version = _shared_version(module)
    if version != SHARED_LIBRARY_VERSION:
        raise RuntimeError(
            f"unsupported {SHARED_LIBRARY_DISTRIBUTION} version {version!r}; "
            f"expected {SHARED_LIBRARY_VERSION}"
        )
    return module


def _shared_version(module: Any | None = None) -> str | None:
    module = module if module is not None else _shared_module()
    if module is None:
        return None
    value = getattr(module, "__version__", None)
    return value if isinstance(value, str) and value else None


def shared_library_status() -> dict[str, Any]:
    try:
        module = _shared_module()
        version = _shared_version(module)
        return {
            "distribution": SHARED_LIBRARY_DISTRIBUTION,
            "import_package": SHARED_LIBRARY_IMPORT,
            "specifier": SHARED_LIBRARY_SPECIFIER,
            "installed": module is not None,
            "compatible": module is not None,
            "version": version,
            "backend": "shared" if module is not None else "legacy-compatibility",
            "error_class": None,
        }
    except Exception as exc:
        return {
            "distribution": SHARED_LIBRARY_DISTRIBUTION,
            "import_package": SHARED_LIBRARY_IMPORT,
            "specifier": SHARED_LIBRARY_SPECIFIER,
            "installed": True,
            "compatible": False,
            "version": None,
            "backend": "unavailable",
            "error_class": type(exc).__name__,
        }


def _call_shared(name: str, *args: Any, **kwargs: Any) -> Any:
    module = _shared_module()
    if module is None:
        raise RuntimeError(
            "comparative evaluation shared library unavailable; install "
            "agent-workflow-typesafe[eval]"
        )
    fn = getattr(module, name, None)
    if not callable(fn):
        raise RuntimeError(f"shared comparative-eval library has no callable {name}")
    return fn(*args, **kwargs)


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        converted = to_dict()
        if isinstance(converted, Mapping):
            return dict(converted)
    raise TypeError("shared comparative-eval result is not a mapping")


def _legacy_schema(value: Any) -> dict[str, Any]:
    result = _mapping(value)
    if result.get("schema") == CANONICAL_OBSERVATION_SCHEMA:
        result["schema"] = LEGACY_OBSERVATION_SCHEMA
    return result


def sha256(value: object) -> str:
    module = _shared_module()
    if module is not None and callable(getattr(module, "sha256", None)):
        return str(module.sha256(value))
    return _legacy.sha256(value)


def load_corpus(name: str) -> list[dict[str, Any]]:
    module = _shared_module()
    if module is not None and callable(getattr(module, "load_corpus", None)):
        cases = module.load_corpus(name)
        if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)):
            raise TypeError("shared evaluation corpus is not a sequence")
        return [_mapping(case) for case in cases]
    return _legacy.load_corpus(name)


def observation(
    *,
    feature_id: str,
    mode: str,
    identity: Mapping[str, Any],
    source_input: Mapping[str, Any],
    projected_input: Mapping[str, Any],
    control: Callable[[], Mapping[str, Any]] | None,
    candidate: Callable[[], Mapping[str, Any]] | None,
    case_id: str | None = None,
    data_class: str = "synthetic",
    observation_id: str | None = None,
) -> dict[str, Any]:
    """Return the legacy 0.1.x observation shape for compatibility.

    When the shared library is installed, generic execution is delegated there
    and the neutral schema ID is translated back to the historical TypeSafe ID
    for this compatibility API only.
    """
    module = _shared_module()
    if module is None or not callable(getattr(module, "observation", None)):
        return _legacy.observation(
            feature_id=feature_id,
            mode=mode,
            identity=identity,
            source_input=source_input,
            projected_input=projected_input,
            control=control,
            candidate=candidate,
            case_id=case_id,
            data_class=data_class,
            observation_id=observation_id,
        )
    return _legacy_schema(
        module.observation(
            feature_id=feature_id,
            mode=mode,
            identity=identity,
            source_input=source_input,
            projected_input=projected_input,
            control=control,
            candidate=candidate,
            case_id=case_id,
            data_class=data_class,
            observation_id=observation_id,
        )
    )


def neutral_observation(**kwargs: Any) -> dict[str, Any]:
    """Create the canonical neutral observation; requires the ``eval`` extra."""
    result = _mapping(_call_shared("observation", **kwargs))
    if result.get("schema") == LEGACY_OBSERVATION_SCHEMA:
        result["schema"] = CANONICAL_OBSERVATION_SCHEMA
    return result


def validate_observation(value: Mapping[str, Any]) -> None:
    schema = value.get("schema")
    module = _shared_module()
    if schema == CANNICAL_OBSERVATION_SCHEMA:
        if module is None:
            raise RuntimeError(
                "canonical comparative-eval observations require "
                "agent-workflow-typesafe[eval]"
            )
        _call_shared("validate_observation", value)
        return
    if schema != LEGACY_OBSERVATION_SCHEMA:
        raise ValueError("unknown comparation observation schema")
    # Preserve exact 0.1.0 validation semantics for the compatibility shape.
    _legacy.validate_observation(value)


def run_static_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    feature_id: str,
    control: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    candidate: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    repetitions: int = 1,
) -> list[dict[str, Any]]:
    module = _shared_module()
    if module is None or not callable(getattr(module, "run_static_cases", None)):
        return _legacy.run_static_cases(
            cases,
            feature_id=feature_id,
            control=control,
            candidate=candidate,
            repetitions=repetitions,
        )
    values = module.run_static_cases(
        cases,
        feature_id=feature_id,
        control=control,
        candidate=candidate,
        repetitions=repetitions,
    )
    return [_legacy_schema(value) for value in values]


def neutral_run_static_cases(
    cases: Sequence[Mapping[str, Any]],
    *,
    feature_id: str,
    control: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    candidate: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    repetitions: int = 1,
) -> list[dict[str, Any]]:
    """Run the canonical shared-library static path; requires the eval extra."""
    values = _call_shared(
        "run_static_cases",
        cases,
        feature_id=feature_id,
        control=control,
        candidate=candidate,
        repetitions=repetitions,
    )
    result: list[dict[str, Any]] = []
    for value in values:
        item = _mapping(value)
        if item.get("schema") == LEGACY_OBSERVATION_SCHEMA:
            item["schema"] = CANONICAL_OBSERVATION_SCHEMA
        result.append(item)
    return result
