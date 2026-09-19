# Changelog

## 0.1.1

- Adopt the planned `agent-workflow-comparative-eval==0.1.0` shared-library boundary as an optional `eval` extra.
- Keep `agent_workflow_typesafe.evaluation` as a 0.1.x compatibility facade; delegate to the shared library when installed and retain the frozen 0.1.0 implementation only as a base-install fallback.
- Add canonical neutral comparative-evaluation helpers for new consumers.
- Keep TypeSafe/Jev execution and provider-specific candidate telemetry in this plugin.
- Retain the existing routing and skill-behavior corpora byte-for-byte as compatibility resources pending the shared-library release.
- Add shared-library compatibility diagnostics and metadata.
- Restore repository-level compatibility metadata to the source artifact.

No TypeSafe question-set, semantic receipt, routing authority, lifecycle, review, or acceptance behavior changes are introduced by this migration.
