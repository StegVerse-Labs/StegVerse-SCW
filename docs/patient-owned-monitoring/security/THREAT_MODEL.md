# Patient-Owned Monitoring Threat Model

_Last reviewed: 2026-08-02_

## Security objective

Applicable federal requirements are the minimum floor. The patient-owned monitoring system must exceed that floor through patient-controlled encryption, fail-closed evidence handling, hardware-rooted identity where available, independently inspectable receipts, and explicit activation gates.

## Protected assets

1. Raw physiological waveforms and images.
2. Derived measurements, calibration state, and personal baselines.
3. Patient identity and device-pairing records.
4. Encryption keys, signing keys, recovery material, and device credentials.
5. Firmware, configuration, algorithms, model versions, and update metadata.
6. Audit records, custody chains, validation receipts, and reference-device evidence.
7. Availability of local recording during network, account, cloud, or clinic outages.

## Trust boundaries

- Sensor to recorder.
- Recorder secure storage to analysis process.
- Device to paired patient controller.
- Local system to optional cloud synchronization.
- Build system to firmware/software release channel.
- Monitoring output to reference-device/laboratory evidence.
- Patient authority to emergency delegate or recovery operator.

Every boundary requires authenticated endpoints, explicit authorization, replay resistance, integrity verification, and an inspectable failure record.

## Adversaries

- Opportunistic thief with temporary or permanent device possession.
- Malicious application or process on a paired device.
- Remote attacker targeting exposed services, update channels, or credentials.
- Supply-chain attacker modifying source, dependencies, build actions, firmware, or hardware.
- Insider or delegated user exceeding authorized access.
- Data broker, platform operator, or service provider attempting secondary use.
- Ransomware or destructive actor attempting denial, deletion, or evidence corruption.
- Faulty sensor, clock, algorithm, or model producing plausible but incorrect output.

## Threats and required controls

| Threat | Security effect | Required controls | Activation evidence |
|---|---|---|---|
| Device theft | Disclosure and unauthorized control | Encrypted storage, hardware-backed keys, local authentication, rapid revocation, minimal lock-screen disclosure | Lost-device exercise and revocation receipt |
| Credential phishing | Account takeover | Phishing-resistant MFA for privileged access; no SMS-only privileged recovery | Authentication policy and test receipt |
| Malicious update | Persistent compromise | Signed release manifests, verified boot where available, anti-rollback, reproducible or independently verifiable builds | Firmware/software signature verification receipt |
| Sensor spoofing or replay | False clinical evidence | Device identity, session nonce, monotonic sequence, authenticated records, clock-drift evidence | Replay and sequence-gap tests |
| Record alteration or deletion | Integrity and availability loss | Append-only hashes, signed checkpoints, immutable/offline backup, deletion receipts, recovery testing | Tamper and restore test receipts |
| Cloud or clinic outage | Loss of monitoring | Local-first capture, offline export, queued synchronization, patient-held recovery path | Offline operation and recovery receipt |
| Privilege escalation | Unauthorized access or override | Least privilege, explicit roles, dual control for exceptional access, expiring emergency override | Access matrix and override exercise |
| Dependency or CI compromise | Build contamination | Pinned actions, minimal workflow permissions, dependency inventory, secret scan, review gates, provenance receipt | CI security receipt and reviewed dependency changes |
| Secondary use or overcollection | Privacy loss | Data minimization, purpose binding, patient consent, export/delete controls, no hidden telemetry | Data-flow review and consent-control test |
| Algorithmic misclassification | Unsafe inference | Raw evidence retention, provenance labels, partition isolation, confidence/quality output, reference validation, human review where required | Validation report and acceptance decision |

## Abuse cases

- A service refuses patient export unless an account remains active.
- A caregiver or emergency delegate silently gains permanent access.
- A synthetic fixture is represented as physical validation.
- Missing data is converted to zero and treated as measured.
- A proposed image boundary becomes effective without operator review.
- A security exception remains active without an owner, compensating control, or expiration.
- A workflow passes despite missing receipts or skipped checks.

These cases must fail closed and produce durable evidence.

## Security invariants

1. Unknown is never encoded as measured zero.
2. Unauthenticated or replayed sensor data cannot become trusted evidence.
3. A failed signature, hash, sequence, timestamp, or authorization check blocks ingestion or activation.
4. Patient export remains possible without continued cloud or clinic cooperation.
5. Emergency access is visible, time-limited, attributable, and revocable.
6. Security profile validity does not imply operational security activation.
7. No production activation occurs while a critical risk lacks verified mitigation or an approved expiring exception.

## Review triggers

Review this model after any new sensor, wireless interface, storage backend, cloud service, firmware platform, privilege role, recovery mechanism, reference-device integration, or material security incident. Review is also required before any production release.