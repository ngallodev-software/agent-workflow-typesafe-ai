"""Credential-free TypeSafe advisory plugin package."""

__version__ = "0.1.0"

from .evaluation import load_corpus, observation, run_static_cases, validate_observation

__all__ = ["__version__", "load_corpus", "observation", "run_static_cases", "validate_observation"]
