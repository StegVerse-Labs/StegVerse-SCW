# StegVerse Risk Register (v1.0)

This file is a human-readable index of key risks and mitigations.
It should be kept in sync with `compliance_rules.yaml`.

---

## R-001: Misconfigured Payments

- Area: Finance / Payments
- Risk: Incorrect Stripe or Coinbase configuration causes lost revenue or security issues.
- Mitigations:
  - Use StegTV vault for secrets.
  - Economy workers validate config at startup.
  - All webhook events logged to Continuity and StegLedger.

---

## R-002: AI Worker Misbehavior

- Area: AI Workforce
- Risk: A worker applies incorrect patches or misinterprets intent.
- Mitigations:
  - Strict scopes via worker classes (infra, builder, compliance, economy).
  - Dry-run modes + human approval for high-impact changes.
  - Change logs viewable in Continuity.

---

## R-003: Regulatory Drift

- Area: Compliance
- Risk: Laws/policies change, leaving rules outdated.
- Mitigations:
  - Compliance workers periodically re-scan policies.
  - Changes to compliance_rules.yaml require explicit review and logging.
