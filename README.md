# Agent-Workflow TypeSafe

`agent-workflow-typesafe` is an external Agent-Workflow plugin that produces
bounded TypeSafe semantic evidence. It is intentionally advisory: it never
changes Agent-Workflow routing, model policy, lifecycle, evaluation, review,
or acceptance.

Install the base package for discovery, compatibility checks, receipts, and
offline tests. Install `agent-workflow-typesafe[typesafe]` only to make live
TypeSafe calls. `TYPESAFE_API_KEY` is read only by the optional live adapter;
it is never written to configuration, receipts, or logs.

Enable it in Agent-Workflow configuration:

```toml
[plugins]
enabled = ["agent-workflow-typesafe"]
```

Then use `agent-workflow typesafe compatibility`, `doctor`, `advise-routing`,
or `evaluate-skill`. Live calls require both the optional extra and the normal
runtime environment key. All outcomes remain `no_action` advisory evidence.

