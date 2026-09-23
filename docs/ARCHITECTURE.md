# Architecture and security boundary

The plugin projects bounded, redacted caller input into TypeSafe Choice, Noul,
and Score questions. It normalizes the response into a secret-free receipt.
The receipt is advisory `no_action` evidence: it cannot route work, select a
model/executor, mutate lifecycle state, pass an evaluation, review, or accept
work. Agent-Workflow remains authoritative for all of those actions.

The TypeSafe SDK is a lazy optional extra. Plugin discovery, `compatibility`,
`doctor`, package imports, base installs, and offline tests never import it or
make a network request. `TYPESAFE_API_KEY` is only read at live execution time;
receipts record neither raw state, key values, nor headers.

