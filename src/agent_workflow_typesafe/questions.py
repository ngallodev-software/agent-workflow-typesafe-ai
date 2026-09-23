"""Versioned, self-contained semantic questions with bounded answer spaces."""

from __future__ import annotations


ROUTING_VERSION = "routing/v1alpha1"
SKILL_VERSION = "skill-evaluation/v1alpha1"


def routing_questions() -> dict[str, object]:
    return {
        "task_class": {"type": "choice", "instructions": "Classify this task by its primary requested work. Choose other when no listed class fits.", "criteria": {"implementation": "Change product code or configuration.", "diagnosis": "Investigate a failure without changing product behavior.", "review": "Assess existing evidence or changes.", "documentation": "Create or revise explanatory material.", "other": "No listed task class applies."}},
        "interaction_needed": {"type": "noul", "instructions": "Would completing this task require a material user decision or authorization not present in the supplied task?", "criteria": {"true": "A missing decision or authorization is required.", "false": "The supplied task permits completion."}},
        "semantic_risk": {"type": "score", "instructions": "Assess the semantic consequence of misunderstanding this task, using the ordered rubric.", "criteria": ["Low consequence; easily reversible.", "Moderate consequence; requires careful verification.", "High consequence; could affect authority, security, or irreversible state."]},
    }


def skill_questions() -> dict[str, object]:
    return {
        "behavior_supported": {"type": "noul", "instructions": "Does the supplied skill text actually direct the stated requirement, rather than merely containing related words?", "criteria": {"true": "The instructions direct the required behavior.", "false": "The instructions do not direct the required behavior."}},
        "completeness": {"type": "score", "instructions": "Assess completeness of the skill guidance for the stated requirement.", "criteria": ["Missing or misleading.", "Partially useful but omits material guidance.", "Complete enough to perform the required behavior."]},
        "actionability": {"type": "score", "instructions": "Assess whether the skill gives actionable direction for the stated requirement.", "criteria": ["No usable action.", "Some action but important ambiguity remains.", "Clear action a worker can follow."]},
    }

