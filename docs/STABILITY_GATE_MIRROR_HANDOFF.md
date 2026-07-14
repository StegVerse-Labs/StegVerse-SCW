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

Installed code locations:

- `engine/stability_gate/`
- tests: `tests/stability_gate/`
- runtime evidence: `artifacts/receipts/stability_gate/`
- reports: `artifacts/reports/stability_gate/`
- schemas: `schemas/stability_gate_input_provenance.schema.json`

## Verified SCW boundary

The current SCW command path is:

1. `.github/workflows/scw_orchestrator.yml` checks out the repository and runs `python scw/scw_core.py`.
2. `scw/scw_core.py` normalizes the workflow or repository-dispatch command, target repository, and JSON arguments.
3. The Stability Gate dry-run executes immediately after context normalization and before command dispatch in `main()`.
4. Existing command handlers then execute unchanged.

This is the verified pre-dispatch boundary for the current SCW core. The current handlers are predominantly stubs, so this is not yet proof of a real repository mutation boundary. Enforcement remains prohibited until a concrete mutating handler is implemented and separately reviewed.

The repository also contains `.github/workflows/ingestion-orchestrator.yml`, but its run job currently contains only a TODO echo rather than real ingestion or mutation logic. It is therefore not an active mutation boundary.

## Work completed

Prototype bundles v1 through v16 were generated outside GitHub. They are not authoritative releases and are not retained as the production source.

The authoritative repository implementation now includes:

- `engine/stability_gate/__init__.py`
- `engine/stability_gate/model.py`
- `engine/stability_gate/policy.py`
- `engine/stability_gate/receipt.py`
- `engine/stability_gate/failure_receipt.py`
- `engine/stability_gate/replay.py`
- `engine/stability_gate/adapter.py`
- `engine/stability_gate/storage.py`
- `engine/stability_gate/provenance.py`
- `tests/stability_gate/test_policy.py`
- `tests/stability_gate/test_receipt.py`
- `tests/stability_gate/test_adapter.py`
- `tests/stability_gate/test_storage.py`
- `tests/stability_gate/test_provenance.py`
- ALLOW, DELAY, BLOCK, and FAIL_CLOSED JSON fixtures
- `scripts/stability_gate_fixture_run.py`
- `docs/STABILITY_GATE_INPUT_PROVENANCE.md`
- `schemas/stability_gate_input_provenance.schema.json`

Implemented behavior:

- typed and validated runtime input;
- explicit ALLOW, DELAY, BLOCK, and FAIL_CLOSED decisions;
- stale, malformed, invalid-range, zero-volatility, NaN, and infinite inputs fail closed;
- canonical JSON serialization and SHA-256 receipt hashes;
- normal decision receipts and hashed context-failure receipts;
- receipt parent chaining;
- deterministic replay and chain verification;
- idempotent local receipt persistence;
- SCW dry-run evaluation before command dispatch;
- representative four-case evidence generation;
- workflow unit-test and evidence-generation steps;
- 30-day GitHub Actions artifact retention for generated dry-run receipts and reports;
- machine-readable provenance validation for all four metrics.

## Accuracy boundary

The following are not production implementations and must not be claimed:

- zero-knowledge proofs;
- PBFT or Byzantine-fault-tolerant consensus;
- secure cryptographic identity and key management;
- hardware-enclave identity;
- network transport or gossip synchronization;
- durable distributed leases;
- exactly-once distributed execution;
- economic settlement or slashing;
- cross-network federation.

Any such feature must be implemented, tested, reviewed, and documented independently.

## Current build scope

The authorized integration slice remains local and deterministic:

1. canonical state validation;
2. score computation with explicit threshold policy;
3. ALLOW, DELAY, BLOCK, or FAIL_CLOSED decision;
4. chained receipt generation for both valid and invalid contexts;
5. deterministic replay verification;
6. unit tests and fixtures;
7. explicit provenance classification;
8. dry-run integration at the verified command-dispatch boundary;
9. observation before any enforcement activation.

## Runtime input contract

SCW accepts explicit metrics only through `args.stability_gate`:

- `deliberation_capacity`
- `model_fidelity`
- `environmental_volatility`
- `action_magnitude`
- optional `source`

No values are inferred. Missing metrics produce FAIL_CLOSED in dry-run output, generate a hashed failure receipt, and do not block existing SCW execution.

## Provenance contract

The first authoritative provenance shape is defined by:

- `engine/stability_gate/provenance.py`
- `schemas/stability_gate_input_provenance.schema.json`
- `docs/STABILITY_GATE_INPUT_PROVENANCE.md`

Each metric must declare a derivation class, producer, method, and evidence references. Supported classes are:

- `CALLER_ASSERTED`
- `DERIVED`
- `RECONSTRUCTED`

Derived and reconstructed values require evidence references. Caller-asserted values may be observed in dry-run mode but are not sufficient for enforcement activation.

Final measurement algorithms, authorized producers, evidence-age limits, and disagreement rules remain unresolved.

## Remaining work and blockers

- Execute the Stability Gate test suite in GitHub Actions and retain run evidence.
- Dispatch representative SCW runs for ALLOW, DELAY, BLOCK, and FAIL_CLOSED inputs.
- Confirm receipt and report artifacts are uploaded and replayable after download.
- Integrate the provenance object into runtime arguments and decision receipts.
- Define the actual measurement algorithms and authorized producers for D, M, E, and A.
- Identify the first concrete SCW handler that performs a mutation.
- Place a second dry-run observation immediately before that handler's irreversible boundary.
- Verify no alternate mutation path bypasses the gate.
- Preserve the Stability Gate validation path if PR #20 consolidates workflows.
- Keep enforcement disabled until representative observations and schema review are complete.

## Ownership

Current owner: Issue #21, Stability Gate integration in `StegVerse-Labs/StegVerse-SCW`.

Continuation may modify only this local deterministic slice until input schemas and a concrete mutation boundary are verified.

## Validation requirements

Before enforcement activation:

- all unit tests pass in GitHub Actions;
- canonical serialization reproduces hashes;
- malformed, missing, stale, zero, NaN, and infinite inputs fail closed;
- valid and invalid contexts both produce verifiable receipts;
- receipt chains verify from genesis to head;
- replay reproduces the stored score and decision;
- dry-run output is observed on representative SCW tasks;
- receipt and report artifacts survive the workflow run;
- provenance classifications and evidence references validate;
- no existing mutation path is bypassed unintentionally.

## Release state

Status: pre-alpha dry-run integration.

Do not tag a release until the local deterministic slice is tested and representative dry-run evidence is retained. Do not activate enforcement until authoritative input derivation and the first concrete mutation boundary are verified.

## Ecosystem follow-through after release readiness

When release criteria are met, create a verification task to determine whether relevant public or operational information must be propagated to:

- `StegVerse-Labs/Site`
- `BCAT-GCAT-Engine/Publisher`
- `StegVerse-Labs/admissibility-wiki`
- `stegguardian-wiki`

## Archival continuity

This handoff preserves the decisions, completed implementation, verified command boundary, accuracy limits, blockers, permitted continuation scope, ownership, and validation requirements.