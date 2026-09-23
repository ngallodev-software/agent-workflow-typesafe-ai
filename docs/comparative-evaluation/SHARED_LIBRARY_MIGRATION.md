# Shared-Library Migration Notes

## Package split

- shared: `agent-workflow-comparative-eval==0.1.0`
- provider plugin: `agent-workflow-typesafe`

Base plugin installation remains independent from the shared library. Use the `eval` optional
extra when comparative evaluation is needed.

## Legacy behavior

The 0.1.0 generic implementation is retained internally as `_legacy_evaluation.py` solely so
existing base installations and public imports keep working before the shared library is
available. It is not a second canonical implementation.

## Canonical namespace

Legacy: `agent-workflow-typesafe/comparison-observation/v1`
Canonical: `agent-workflow-comparative-eval/comparison-observation/v1`

The compatibility facade preserves the legacy schema ID for existing `observation()` and
`run_static_cases()` callers. New callers should prefer `neutral_observation()` and
`neutral_run_static_cases()` with the `eval` extra installed.
