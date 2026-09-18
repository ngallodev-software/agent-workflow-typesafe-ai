# P0-00 external contract baseline audit

Audit date: 2026-09-18

- Agent-Workflow: `0.10.0`, public plugin API `1`, entry point group
  `agent_workflow.plugins`; verified from the installed product and public
  `agent_workflow.plugin_api` source.
- TypeSafe: `typesafe-sdk 0.6.0`, Python `>=3.10`; verified from current PyPI
  package metadata on 2026-09-18.
- The plugin uses only `PluginCommand`, `PluginDescriptor`, and
  `PluginPackageResource` from the public host API. It imports no private host
  module and modifies no host repository.

No blocking API drift was found. The plugin qualifies only host `0.10.0` until
an explicit compatibility-matrix result adds another version.

