# Normal-Usage Shadow Capture

1. Generate `observation_id`.
2. Canonicalize a bounded input/projection and persist only SHA-256 plus safe metadata.
3. Execute the original/control path normally.
4. If explicitly enabled and sampled, run the TypeSafe candidate with a bounded timeout/budget.
5. Never apply the candidate in shadow mode.
6. Persist `comparison-observation/v1`.
7. Later join completion/evaluation/review outcomes by writing a separate immutable `comparison-outcome/v1`.

Record control duration, candidate duration, provider elapsed time, first-output latency, and whether candidate execution was sequential or concurrent. Do not call sequential shadow delay a future production critical-path estimate if the future design would run concurrently.

Default persistence contains no raw task/skill text, API key, or environment dump. Normal-usage capture is opt-in, sampleable, budgetable, and disableable without uninstalling the plugin.
