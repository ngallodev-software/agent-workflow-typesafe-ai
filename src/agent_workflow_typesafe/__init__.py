"""Credential-free TypeSafe advisory plugin package."""

__version__ = "0.1.2"

from .evaluation import (
    load_corpus,
    neutral_observation,
    neutral_run_static_cases,
    observation,
    run_static_cases,
    shared_library_status,
    validate_observation,
)

__all__ = [
    "__version__",
    "load_corpus",
    "neutral_observation",
    "neutral_run_static_cases",
    "observation",
    "run_static_cases",
    "shared_library_status",
    "validate_observation",
]
