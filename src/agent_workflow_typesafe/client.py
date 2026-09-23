"""Optional TypeSafe adapter; no import or network activity occurs until live use."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class DecisionClient(Protocol):
    def system_one(self, state: Mapping[str, object], questions: Mapping[str, object], model: str | None = None) -> Any: ...


class TypeSafeDecisionClient:
    def __init__(self) -> None:
        try:
            from typesafe_sdk import TypeSafeClient
        except ImportError as exc:
            raise RuntimeError("typesafe_sdk_unavailable") from exc
        self._client = TypeSafeClient()

    def system_one(self, state: Mapping[str, object], questions: Mapping[str, object], model: str | None = None) -> Any:
        return self._client.system_one(state=state, questions=questions, model=model)


def normalize_response(response: Any) -> tuple[str | None, dict[str, object]]:
    model = getattr(response, "model", None)
    answers = getattr(response, "answers", None)
    if not isinstance(answers, Mapping):
        raise ValueError("TypeSafe response has no answer mapping")
    normalized: dict[str, object] = {}
    for name, answer in answers.items():
        if hasattr(answer, "choice"):
            normalized[str(name)] = {"type": "choice", "choice": answer.choice, "confidence": answer.confidence, "probabilities": dict(answer.probabilities)}
        elif hasattr(answer, "noul"):
            normalized[str(name)] = {"type": "noul", "probability": answer.noul}
        elif hasattr(answer, "score"):
            normalized[str(name)] = {"type": "score", "score": answer.score, "confidence": answer.confidence, "probabilities": {str(key): value for key, value in answer.probabilities.items()}}
        else:
            raise ValueError("TypeSafe response has unsupported answer type")
    return model if isinstance(model, str) else None, normalized

