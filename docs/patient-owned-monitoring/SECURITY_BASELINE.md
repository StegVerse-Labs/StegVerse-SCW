# Patient-Owned Monitoring Security Baseline

_Status: mandatory engineering baseline_

## Policy

Federal requirements are the minimum acceptable floor. This system must meet applicable federal obligations and then apply stricter controls wherever technically feasible without undermining patient ownership, evidence availability, or recoverability.

This document is an engineering control baseline, not a legal determination that HIPAA or another statute applies to every deployment. Applicability is decided per deployment, but the controls below remain the default even when a deployment falls outside a covered-entity relationship.

## External baseline references

- HHS HIPAA Security Rule: administrative, physical, and technical safeguards protecting confidentiality, integrity, and availability of electronic protected health information.
- HHS risk-analysis guidance: risk analysis is foundational and must drive safeguard selection.
- NIST SP 800-53 Rev. 5, including current patch releases: security and privacy control catalog.
- NIST Cybersecurity Framework 2.0: Govern, Identify, Protect, Detect, Respond, and Recover outcomes.
- CISA Secure by Design principles: security ownership, secure defaults, and elimination of avoidable customer burden.

## StegVerse minimum profile

The enforceable machine-readable profile is `security/patient_owned_monitoring/security_profile.json`.

The default profile requires:

1. **Patient control and minimization**
   - Patient is the primary data authority.
   - Collection is limited to declared channels and purposes.
   - Raw evidence remains exportable in documented formats.
   - Secondary use requires an explicit, separately recorded authorization.

2. **Cryptography**
   - Data at rest uses authenticated encryption with keys separated from protected data.
   - Data in transit uses mutually authenticated encrypted transport where both endpoints are controlled.
   - Hashes alone never substitute for encryption.
   - Key rotation, revocation, backup, and recovery are documented and testable.
   - Production secrets and private keys are never committed to source control.

3. **Identity and access**
   - Least privilege and deny-by-default access.
   - Phishing-resistant multi-factor authentication for administrative or remote privileged access.
   - Short-lived service credentials where supported.
   - Separate patient, operator, service, support, and emergency roles.
   - Every emergency override is time-bounded, reason-coded, and auditable.

4. **Device and firmware integrity**
   - Signed firmware and verified boot on production hardware where platform support exists.
   - Unique device identity and revocable device authorization.
   - Anti-rollback protection for security-sensitive firmware.
   - Debug interfaces disabled or physically controlled in production mode.
   - Firmware build provenance and hashes retained with acquisition receipts.

5. **Evidence integrity**
   - Append-only sequencing and cryptographic record chaining for acquisition records.
   - Original timestamps retained alongside correction models.
   - Source, algorithm, calibration, hardware, and firmware versions bound to derived outputs.
   - Unknown values remain null or explicitly unknown; zero is never used as a missing-value substitute.

6. **Audit and detection**
   - Security-relevant access, export, configuration, key, firmware, and override events are logged.
   - Logs are tamper-evident, time synchronized, and retained separately from mutable application data.
   - Failed authentication, integrity failure, clock discontinuity, sequence gap, unexpected export, and policy bypass generate inspectable events.

7. **Availability and recovery**
   - Patient access and evidence recovery remain possible during loss of network connectivity.
   - Encrypted backups are integrity checked and recovery tested.
   - Failures fail closed for disclosure and privilege, but fail safe for acquisition continuity whenever doing so does not expose protected data.
   - Recovery does not erase provenance, audit history, or rejected records.

8. **Supply chain and development**
   - Dependency versions are pinned or otherwise deterministically resolved.
   - Build provenance and artifact hashes are retained.
   - Code changes pass syntax, unit, integration, security-profile, and secret-scanning gates.
   - Third-party components have explicit ownership, update, vulnerability, and removal paths.

9. **Incident response and disclosure**
   - Incident state is classified as SUSPECTED, CONTAINED, ERADICATED, RECOVERED, or CLOSED.
   - Compromise of confidentiality, integrity, device identity, keys, or evidence continuity creates a durable incident receipt.
   - Notification obligations are determined from deployment role and applicable law; absence of legal applicability never suppresses patient notification for a material security event.

10. **Security assurance above the floor**
    - Required controls cannot be waived merely because a federal rule describes them as addressable.
    - A control exception requires documented rationale, compensating controls, owner, expiration, and approval.
    - Missing evidence is a validation failure, not an implicit pass.
    - Production activation requires a completed threat model, risk register, recovery test, key-management test, and independent security review.

## Activation gates

The system is not security-activated until all of the following are evidenced:

- machine-readable profile passes validation;
- threat model and risk register are committed;
- secret scanning and dependency review are active;
- encryption and key lifecycle are implemented and tested;
- signed firmware/verified boot are demonstrated on the selected hardware, or an explicit blocked record identifies the unsupported platform;
- access-control and emergency-override tests pass;
- backup restoration and offline recovery are demonstrated;
- incident-response exercise receipt is committed;
- independent review findings are resolved or accepted through a time-bounded exception.

## Authority boundary

This baseline defines mandatory engineering controls. It does not claim deployment compliance, certification, authorization to operate, HIPAA applicability, FDA clearance, or federal approval. Those statuses require separate deployment-specific evidence and authority.
