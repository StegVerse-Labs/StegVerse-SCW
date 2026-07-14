# Stability Gate Mirror Handoff

## Authority

This document is the current continuation source of truth for integrating the Stability Gate into `StegVerse-Labs/StegVerse-SCW`.

## Decision record

The Stability Gate is an execution-time admissibility boundary derived from the protected deliberation interval described by the OODA Observe–Orient–Decide–Act model.

Baseline score:

`S = (D × M) / (E × A)`

- `D`: deliberation capacity or protected pause
- `M`: model fidelity
- `E`: environmental volatility
- `A`: action magnitude

The score is an experimental policy signal, not a proven universal control-law stability theorem. Initial enforcement uses a repository-configured threshold and must fail closed when required inputs are absent, invalid, stale, or non-finite.

## Target installation

Primary repository: `StegVerse-Labs/StegVerse-SCW`

Planned code location:

- `engine/stability_gate/`
- tests: `tests/stability_gate/`
- runtime evidence: `artifacts/receipts/stability_gate/`

The actual SCW execution insertion point must be identified from the repository's current orchestrator and ingestion paths before enforcement is connected. No generic `apply_bundle()` location is assumed.

## Work completed in the originating session

Prototype bundles v1 through v16 were generated outside GitHub. The last prototype introduced:

- a typed state model;
- score computation;
- ALLOW/BLOCK evaluation;
- canonical JSON hashing;
- receipt chaining through `previous_hash`;
- deterministic receipt verification;
- score replay and drift detection;
- proposed install paths under `engine/stability_gate/` and `artifacts/receipts/`.

These sandbox ZIPs are not authoritative releases and are not retained as the production source.

## Accuracy correction

Earlier prototype descriptions overstated implementation maturity. The following are not production implementations in the generated bundles:

- zero-knowledge proofs;
- PBFT or Byzantine-fault-tolerant consensus;
- secure cryptographic identity and key management;
- hardware-enclave identity;
- network transport or gossip synchronization;
- durable distributed leases;
- exactly-once distributed execution;
- economic settlement or slashing;
- cross-network federation.

Any such feature must be implemented, tested, reviewed, and documented independently before being claimed.

## Current build scope

The authorized first integration slice is local and deterministic:

1. canonical state validation;
2. score computation with explicit threshold policy;
3. ALLOW, DELAY, BLOCK, or FAIL_CLOSED decision;
4. chained receipt generation;
5. deterministic replay verification;
6. unit tests and fixtures;
7. discovery of the real SCW pre-mutation boundary;
8. dry-run integration before enforcement.

## Required files/modules

Destination: `StegVerse-Labs/StegVerse-SCW`

- `engine/stability_gate/__init__.py`
- `engine/stability_gate/model.py`
- `engine/stability_gate/policy.py`
- `engine/stability_gate/receipt.py`
- `engine/stability_gate/replay.py`
- `tests/stability_gate/test_policy.py`
- `tests/stability_gate/test_receipt.py`
- an integration adapter at the verified SCW pre-mutation boundary
- fixtures for ALLOW, DELAY, BLOCK, and FAIL_CLOSED

## Blockers

- Repository code search did not identify an existing Stability Gate handoff.
- Repository code search did not identify a literal `apply_bundle()` integration point.
- The real pre-mutation boundary remains to be located and documented.
- Runtime input derivation for D, M, E, and A is not yet defined by authoritative schemas.

## Ownership

Current owner: Stability Gate integration task in `StegVerse-Labs/StegVerse-SCW`.

The next session may modify only the local deterministic slice above until the pre-mutation boundary and input schemas are verified.

## Validation requirements

Before enforcement activation:

- all unit tests pass;
- canonical serialization reproduces hashes;
- malformed, missing, stale, NaN, and infinite inputs fail closed;
- receipt chains verify from genesis to head;
- replay reproduces the stored score and decision;
- dry-run output is observed on representative SCW tasks;
- no existing mutation path is bypassed unintentionally.

## Release state

Status: pre-alpha integration scaffold.

Do not tag a release until the local deterministic slice is integrated, tested, and verified in dry-run mode.

## Ecosystem follow-through after release readiness

When release criteria are met, create a verification task to determine whether relevant public or operational information must be propagated to:

- `StegVerse-Labs/Site`
- `BCAT-GCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `stegguardian-wiki`

## Archival continuity

This handoff preserves the originating session's decisions, completed prototype work, known overclaims, blockers, permitted continuation scope, ownership, and validation requirements.