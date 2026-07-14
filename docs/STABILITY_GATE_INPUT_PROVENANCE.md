# Stability Gate Input Provenance

## Status

This document defines the first authoritative provenance contract for Stability Gate inputs. It does not define the final measurement algorithms for D, M, E, or A.

## Required metrics

Every complete provenance object covers:

- `deliberation_capacity`
- `model_fidelity`
- `environmental_volatility`
- `action_magnitude`

Each metric declares:

- `derivation_class`
- `producer`
- `method`
- `evidence_refs`

## Derivation classes

### `CALLER_ASSERTED`

The value is supplied directly by the caller and has not been independently reconstructed. Evidence references may be empty. This class is suitable for dry-run observation only and is not sufficient for enforcement activation.

### `DERIVED`

The value is computed from identified source evidence by a named method. At least one evidence reference is required.

### `RECONSTRUCTED`

The value is independently recomputed from canonical artifacts or records. At least one evidence reference is required. This is the preferred class for enforcement-sensitive decisions.

## Evidence references

Evidence references must be durable identifiers or repository-relative artifact paths. A reference must identify the evidence used, not merely a general documentation page.

Examples:

```text
artifacts/telemetry/run-123.json
receipts/input/sha256-abc123.json
policy/stability/measurement-v1.json
```

## Activation rule

Dry-run mode may observe `CALLER_ASSERTED`, `DERIVED`, or `RECONSTRUCTED` inputs.

Enforcement must remain disabled until a separate reviewed policy establishes:

1. which derivation classes are admissible for each metric;
2. maximum evidence age;
3. authorized producers and methods;
4. reconstruction and disagreement handling;
5. failure behavior when evidence is unavailable.

## Machine-readable contract

- Python validation: `engine/stability_gate/provenance.py`
- JSON Schema: `schemas/stability_gate_input_provenance.schema.json`

## Non-claim

This contract makes provenance explicit and testable. It does not establish that the underlying measurement method is scientifically valid, calibrated, or independently verified.