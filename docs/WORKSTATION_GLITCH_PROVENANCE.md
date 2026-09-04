# Workstation Glitch Provenance

## Purpose

The StegVerse workstation environment should support a simple user command such as `add this glitch` that converts a transient observed failure into a durable, browsable, provenance-preserving incident record.

The capability is intended for ordinary users, maintainers, SMEs, AI systems, and downstream governance/research tooling. It is not a claim that every observed glitch has a known cause or verified fix.

## Core principle

A workstation incident must keep distinct:

1. observed behavior;
2. suspected cause;
3. reproduced behavior;
4. confirmed root cause;
5. workaround;
6. fix availability;
7. fix verification;
8. supersession or closure.

A workaround must never be promoted to a root-cause finding or permanent-fix claim without independent evidence.

## Candidate command semantics

`add this glitch` means:

> Capture the current issue context, classify it, preserve evidence provenance, search for related existing incidents, append rather than duplicate when appropriate, publish the non-sensitive portion to the relevant browsable knowledge surface, and later attach verified remediation evidence.

The command should be context-aware but fail closed on sensitive information, private credentials, personal data, unsupported causal claims, and publication authority.

## Canonical lifecycle

```text
OBSERVED
-> CORRELATED
-> REPRODUCED
-> ROOT_CAUSED
-> FIX_AVAILABLE
-> FIX_VERIFIED
-> SUPERSEDED_OR_CLOSED
```

Not every incident must pass through every state. State transitions require evidence appropriate to the claim being made.

## Minimum incident object

```json
{
  "incident_id": "stable-unique-id",
  "observed_at": "RFC3339",
  "surface": "product/platform/component",
  "environment": {},
  "symptom": "human-readable observed behavior",
  "classification": [],
  "observation_evidence_refs": [],
  "reproduction": {
    "state": "UNKNOWN|NOT_REPRODUCED|REPRODUCED",
    "steps": [],
    "evidence_refs": []
  },
  "suspected_causes": [],
  "root_cause": {
    "state": "UNKNOWN|CANDIDATE|CONFIRMED",
    "description": null,
    "evidence_refs": []
  },
  "workarounds": [],
  "fix": {
    "state": "NONE|AVAILABLE|VERIFIED",
    "description": null,
    "evidence_refs": []
  },
  "related_incident_refs": [],
  "public_projection": {},
  "private_evidence_refs": [],
  "provenance": {},
  "status": "OBSERVED"
}
```

## Public and SME projections

The same canonical incident should support multiple views rather than duplicated records.

### User-facing view

- concise symptom;
- affected environment;
- known workaround;
- whether the cause is known;
- whether a permanent fix has been verified;
- links to related incidents.

### SME/maintainer view

- exact environment and version observations;
- recurrence and correlation information;
- reproduction evidence;
- candidate and confirmed causes kept separate;
- fix provenance;
- regression history;
- linked artifacts, logs, screenshots, traces, or receipts where disclosure is authorized.

### Machine/governance view

- stable identifiers;
- claim/evidence relationships;
- lifecycle transitions;
- confidence and admissibility state;
- immutable or reconstruction-capable provenance;
- redaction/publication policy;
- downstream repository references.

## Cross-repository behavior

A glitch should exist as one canonical incident object with references from relevant repositories or public knowledge surfaces. Repositories should not independently rewrite the incident into incompatible copies.

Potential StegVerse projections include:

- workstation/SCW documentation and tooling;
- StegIndex capability discovery;
- Site/public knowledge views;
- ERL when an incident has research significance;
- Publisher for public projection;
- admissibility-wiki for evidence/claim treatment;
- stegguardian-wiki for governance and failure-mode projection.

Cross-repository propagation must preserve the distinction between observation, inference, verified cause, workaround, and verified remediation.

## Initial motivating observation

Observed incident:

```text
Surface: ChatGPT iOS message composer
Symptom: the + attachment selector was temporarily absent
Observed recovery: force-close and restart the app; the + selector returned
Root cause: UNKNOWN
Current interpretation: transient UI/composer-state glitch
Workaround status: OBSERVED SUCCESS
Permanent fix status: UNVERIFIED
Suggested classification:
  UI / iOS / ChatGPT / composer / attachment-control / transient-state-recovery
```

This example demonstrates why the model must not equate a successful recovery action with a confirmed cause or permanent fix.

## Workstation integration direction

The workstation should eventually expose this as a low-friction capture action available from the current working context. The user should not need to manually choose a repository, write an issue template, or know which downstream knowledge surfaces are relevant.

A governed resolver can determine:

1. whether the observation matches an existing incident;
2. whether to append evidence or create a new incident;
3. which evidence is private, shareable, or public;
4. which repositories should reference the canonical record;
5. what lifecycle state is justified;
6. what additional evidence would be needed to advance the state;
7. whether later evidence represents a workaround, actual fix, regression, or unrelated event.

## Non-authority boundary

Creating or documenting an incident does not itself establish:

- root cause;
- vendor acknowledgement;
- remediation validity;
- public release authority;
- downstream repository acceptance;
- runtime activation;
- security severity;
- admissibility of every attached claim.

Those claims require their own evidence and governed transitions.

## Implementation candidates

Future implementation should consider:

```text
schemas/workstation-incident.schema.json
schemas/workstation-incident-transition.schema.json
data/workstation-incidents/
scripts/capture_workstation_incident.py
scripts/correlate_workstation_incidents.py
scripts/project_workstation_incident.py
workstation UI action: Add this glitch
public incident browser/search surface
SME evidence/provenance inspection surface
```

These paths are candidates only and are not claimed as implemented by this document.
