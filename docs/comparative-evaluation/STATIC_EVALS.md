# Static Evaluation Design

Freeze every dataset version before observing results. Result-affecting fixture/label changes create a new dataset version.

## Routing cases

Include clear implementation/review/exploration, mixed intent, interaction-required and explicitly noninteractive cases, high-risk noninteractive work, ambiguous/other, adversarial prompt-like text, explicit metadata agreement/conflict, and policy-restricted routes.

Compare:
1. original deterministic route;
2. TypeSafe semantic advice;
3. TypeSafe-assisted counterfactual route after the same deterministic host policy;
4. oracle route dimensions when authoritative labels exist.

## Skill behavior cases

Include exact-correct, regex-hit/wrong-behavior, correct paraphrase, missing critical constraint, conflicting/prohibited instruction, order requirement, acknowledgement/evidence requirement, recovery behavior, misleading example, buried behavior, and adversarial content.

Ground truth is behavior compliance, not keyword presence.

Repeated semantic calls measure stability; they are never used to cherry-pick a preferred answer.
