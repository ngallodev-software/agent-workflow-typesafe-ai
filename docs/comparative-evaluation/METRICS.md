# Comparative Metrics

## Correctness

Use an independent oracle/adjudication for correctness claims.

Binary: accuracy, TP/TN/FP/FN, precision, recall, F1, control-only-correct, candidate-only-correct, both-correct, both-wrong.

Choice/classification: top-1 accuracy, confusion matrix, no-match/other rate, control-only-correct and candidate-only-correct.

Ordered Score: mean absolute ordinal error, signed bias, within-one-level accuracy when labeled levels exist.

## Calibration

When probabilities exist: Noul Brier score, reliability bins/ECE when sample size supports it, and multiclass Brier/log loss for complete Choice probability vectors.

## Efficiency

Paired: control duration, candidate duration, provider elapsed time, first-output latency, total observed overhead, input/output/total tokens, retries, provider billed cost, local estimated cost.

Report absolute and percentage deltas where meaningful. Use p50 normally; p90 only at >=20 pairs and p95 only at >=40 pairs, matching current Agent-Workflow conventions.

## Reliability

Candidate success, timeout, transport/service error, fallback, no-decision/other, missing usage evidence, repeated-case stability, sampled/skipped rate.

## Normal-usage downstream outcomes

Join later: completion, deterministic evaluation, review disposition, acceptance, total run time, total tokens/cost, retry/restart count, intervention/steering count, and whether interaction was ultimately required.

While TypeSafe remains shadow-only, these are descriptive outcome proxies, not causal proof.

## Required segmentation

Never silently pool different feature/question-set versions, plugin/host revisions, TypeSafe SDK/models, static vs normal-usage modes, or materially different task/risk cohorts.
