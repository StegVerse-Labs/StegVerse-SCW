# Stability Gate Runtime Binding

## Status

The SCW dry-run adapter now requires two sibling argument objects:

```json
{
  "stability_gate": {
    "deliberation_capacity": 1.0,
    "model_fidelity": 0.9,
    "environmental_volatility": 0.8,
    "action_magnitude": 1.0,
    "source": "caller-defined-source"
  },
  "stability_gate_provenance": {
    "deliberation_capacity": {
      "derivation_class": "CALLER_ASSERTED",
      "producer": "example-producer",
      "method": "example-method",
      "evidence_refs": []
    },
    "model_fidelity": {
      "derivation_class": "CALLER_ASSERTED",
      "producer": "example-producer",
      "method": "example-method",
      "evidence_refs": []
    },
    "environmental_volatility": {
      "derivation_class": "CALLER_ASSERTED",
      "producer": "example-producer",
      "method": "example-method",
      "evidence_refs": []
    },
    "action_magnitude": {
      "derivation_class": "CALLER_ASSERTED",
      "producer": "example-producer",
      "method": "example-method",
      "evidence_refs": []
    }
  }
}
```

## Decision behavior

- Missing or invalid metrics produce `FAIL_CLOSED` and a hashed failure receipt.
- Missing or invalid provenance produces `FAIL_CLOSED` and a hashed failure receipt.
- Valid metrics plus valid provenance produce a version-2 decision receipt.
- The decision receipt hash binds the metric values, provenance, policy, result, node identity, and parent hash.
- Deterministic replay validates both the receipt hash and provenance structure.

## Receipt schema

Normal decision receipts now use:

```text
stegverse.stability-gate.receipt.v2
```

The v2 receipt adds a canonical `provenance` object. Any change to producer, method, derivation class, or evidence references changes the receipt hash.

Failure receipts continue to use:

```text
stegverse.stability-gate.failure-receipt.v1
```

They preserve the rejected runtime context and exact failure reason.

## Current authority limit

All representative fixtures use `CALLER_ASSERTED` provenance. Their evidence demonstrates deterministic plumbing only. It does not establish independent reconstruction, scientific calibration, or enforcement readiness.

Enforcement remains disabled until authorized producers, actual measurement methods, evidence-age rules, and the first concrete mutation boundary are reviewed and recorded.