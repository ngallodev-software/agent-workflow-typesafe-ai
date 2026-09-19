# Comparative Evaluation Ownership

Comparative evaluation is shared infrastructure, not TypeSafe-specific application authority.

Canonical owner: `agent-workflow-comparative-eval` (`agent_workflow_comparative_eval`).

The shared library owns neutral schemas/models, legacy artifact upgrades, canonical hashing,
pairing/cohort identity, reusable metrics/statistics, and frozen oracle datasets. This plugin
owns TypeSafe/Jev projection, questions, SDK calls, semantic receipts, and candidate telemetry.
Agent-Workflow owns control execution, shadow scheduling, lifecycle storage/outcome joins,
review, and acceptance authority.

## Compatibility window

`agent_workflow_typesafe.evaluation` remains available during the 0.1.x series. With
`agent-workflow-typesafe[eval]`, it delegates generic operations to the shared library while
translating canonical observations back to the historical TypeSafe schema ID for old callers.
The `neutral_observation` and `neutral_run_static_cases` helpers require the shared library and
return canonical neutral artifacts.

The packaged `resources/evaluation/*.json` corpora are retained byte-for-byte as compatibility
copies until consumers have migrated. Their canonical future home is the shared library.

## Privacy and authority

Comparative evidence never grants workflow authority. Shadow candidates remain unapplied unless
an independently approved host policy changes that behavior. Raw task/skill text and API keys
must not be persisted in comparative evidence.
