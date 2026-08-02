# Architecture Decision Records

Per `ARCHITECTURE-CONSTITUTION.md` Section 8: the Constitution states
what must remain true regardless of when it's read. This folder
records why one specific decision was made, at one specific point,
including the alternatives considered and the consequences accepted —
a growing history of decisions, underneath a fixed statement of
identity.

An ADR can extend, implement, or refine anything in the Constitution.
An ADR can never contradict it. A genuinely good reason to change
something the Constitution declares invariant requires an explicit,
visible amendment to the Constitution itself — never a precedent
quietly built up across several ADRs.

## Index

| # | Title | Status |
|---|---|---|
| [0001](0001-artifact-registry-additive-shadow-index.md) | Artifact Registry as an additive shadow index, not a system of record | Accepted |
| [0002](0002-schema-contracts-stdlib-not-pydantic.md) | Schema Contracts as stdlib enum + hand-written validation, not Pydantic | Accepted |
| [0003](0003-wire-artifact-registry-into-daily-orchestrator-run.md) | Wire the Artifact Registry into the daily Orchestrator run | Accepted |
