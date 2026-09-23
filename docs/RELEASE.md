# Release policy

Compatibility is explicit in `compat/compatibility.json`; add an Agent-Workflow
release only after host qualification evidence. Build from a clean committed
revision, record wheel SHA-256, and smoke-install against the claimed host.
Do not tag or publish from Phase 3. Live TypeSafe checks are opt-in and cannot
qualify a host or promote advisory evidence into authority.

