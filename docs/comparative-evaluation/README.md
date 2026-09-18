# TypeSafe Comparative Evaluation Layer for Agent-Workflow

This is an **additional layer**. It does not modify or replace the existing TypeSafe plugin implementation pack or Agent-Workflow host-integration pack.

It supplies two new single-repository prompt packs:

- `agent-workflow-typesafe-eval-plugin-prompt-pack`: plugin-side measurement contracts, static labeled semantic corpora, and a candidate telemetry adapter.
- `agent-workflow-typesafe-eval-host-prompt-pack`: static paired control-vs-candidate evaluation, normal-usage shadow capture, delayed outcome joins, and comparative reports.

## Core experiment model

For every TypeSafe-assisted feature, preserve the same input identity and record two arms:

- **control**: the original Agent-Workflow implementation;
- **candidate**: the TypeSafe-assisted implementation/advice.

During ordinary usage the control remains authoritative. TypeSafe is shadow-only and `candidate_applied=false` until a separately approved guarded experiment exists.

Static controlled evidence and normal-usage shadow evidence remain separate cohorts.

## Initial feature registry

1. `routing-advice/v1`: compare original deterministic route with a counterfactual TypeSafe-assisted route passed through the **same deterministic Agent-Workflow policy**.
2. `skill-behavior-eval/v1`: compare deterministic regex checks with semantic behavior judgment against independently labeled cases.

Future TypeSafe features register the same control/candidate/oracle/metrics/capture contract.
