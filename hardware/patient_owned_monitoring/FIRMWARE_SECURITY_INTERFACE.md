# Patient-Owned Monitoring Firmware Security Interface

Status: implementation contract; physical conformance remains unvalidated.

## Required boot chain

1. Immutable ROM or vendor root of trust verifies the first mutable boot stage.
2. Every mutable firmware image is signed by an approved offline release key.
3. Verification failure stops execution and emits a recovery receipt; unsigned fallback is prohibited.
4. Anti-rollback uses a monotonic security version stored in protected nonvolatile state.
5. Recovery images are separately signed, version-bounded, and cannot disable evidence integrity controls.

## Device identity and keys

- Each unit has a unique non-exportable device identity key generated or injected in a controlled provisioning lane.
- Patient-data encryption keys are distinct from firmware-signing, transport, and device-identity keys.
- Long-lived private keys must not be stored in source, ordinary filesystem files, logs, crash dumps, or removable media.
- Key rotation and revocation create append-only receipts.
- Loss of key status is represented as unknown or blocked, never as successful verification.

## Storage and evidence integrity

- Raw evidence is encrypted at rest with authenticated encryption.
- Every frame includes session ID, stream ID, sequence, original timestamp, and authentication tag.
- Sequence gaps, replay, duplicate frames, authentication failures, and clock discontinuities are recorded explicitly.
- Clean shutdown writes a closure record. Brownout recovery reconstructs only authenticated records.
- Export preserves ciphertext/source hashes and creates a custody receipt.

## Runtime protections

- Production debug ports are disabled or require an authenticated, time-bounded service authorization.
- Debug authorization records operator, device, reason, approver, start, expiration, and resulting evidence hashes.
- Watchdog, brownout, storage exhaustion, sensor fault, and clock fault enter defined fail-safe states.
- A failed sensor cannot silently emit zeros; unavailable values remain null with quality flags.
- Remote commands cannot erase raw evidence without a separately authorized and receipted patient action.

## Update protocol

An update manifest must contain image hash, signer key ID, hardware compatibility, minimum security version, release ID, dependency/SBOM reference, validation receipt, and rollback policy. The device verifies all fields before installation and records pre-update and post-update state hashes.

## Offline and recovery requirements

- Core recording remains functional without cloud or account access.
- A patient-controlled offline recovery package contains verified decoder, manifests, public verification material, and recovery instructions.
- Recovery testing must demonstrate restoration from interrupted writes and loss of the primary host application.

## Required bench evidence

- signed image accepted;
- unsigned and modified images rejected;
- older security version rejected;
- debug access denied without authorization;
- encrypted storage unreadable without authorized key path;
- replayed and reordered frames detected;
- brownout recovery preserves authenticated records;
- offline export verifies independently.

Passing this document review does not prove hardware implementation. `POM-HW-001` remains blocked until bench receipts exist.