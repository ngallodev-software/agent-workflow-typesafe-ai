# Evaluation and live contract policy

The default offline suite uses fake TypeSafe responses and exercises projection,
redaction, request hashing, typed normalization, no-match, host mismatch, and
failure fallback. It never needs a key and proves every receipt has
`policy_outcome: no_action`.

Live tests are opt-in: set both `TYPESAFE_API_KEY` and
`TYPESAFE_LIVE_TEST=1`, then install the `typesafe` extra. They are a transport
contract check only; they cannot qualify a host or set automation thresholds.
Calibration tracks no-match/uncertainty, disagreement, and false-accept versus
false-reject consequences before any future policy change.

