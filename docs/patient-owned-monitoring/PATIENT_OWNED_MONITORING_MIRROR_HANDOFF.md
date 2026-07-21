# Patient-Owned Monitoring Mirror Handoff

_Last updated: 2026-07-21_

## Repository

- Organization: `StegVerse-Labs`
- Repository: `StegVerse-SCW`
- Module path: `docs/patient-owned-monitoring/`
- Continuation authority: this file is the source of truth for the patient-owned monitoring build until superseded by a newer committed handoff.

## Purpose

Build a patient-owned, continuously recording health evidence system that preserves raw data, correlates multiple sensors, and validates every derived metric against a known reference device worn or operated at the same time.

The system is intended to support investigation of long warning periods and brief episodes by preserving synchronized evidence rather than reducing observations to summary scores.

## Active goal

Deliver the first complete engineering baseline for:

1. Continuous wearable ECG + PPG + IMU + temperature acquisition.
2. Experimental continuous hemodynamic-change detection and cuffless blood-pressure estimation.
3. Independent overnight PAP evidence capture: oxygen, pulse, respiration, mask pressure, humidity, body position, and awakening markers.
4. Glucose ingestion from a reference CGM or meter.
5. Low-cost saliva, urine, and finger-stick test capture.
6. A staged CBC research workstation beginning with hemoglobin, hematocrit, and standardized blood-smear imaging.
7. A validation framework based on simultaneous reference-device measurements, raw-data retention, error analysis, drift analysis, and explicit acceptance criteria.

## Operating rules

- Build what can be built.
- Preserve raw signals before calculating summaries.
- Every calculated or inferred metric must identify its source signals, algorithm version, calibration state, and validation status.
- Validation must use simultaneous paired measurements against a known reference device or laboratory result.
- Unknown, unmeasured, estimated, and validated values must remain distinct.
- No black-box score may replace exportable raw data.
- Device clocks must be synchronized and clock drift measured.
- Reference measurements must be timestamped and linked to the corresponding raw-signal window.
- Calibration data must never be mixed silently with validation data.
- Personal baselines and population models must be versioned separately.

## Initial build order

### Phase 1 — Evidence recorder

- Synchronized ECG, PPG, IMU, skin temperature, contact pressure, and event marker.
- Local append-only raw storage.
- Open timestamped data format.
- Battery and data-loss telemetry.

### Phase 2 — Reference pairing and validation harness

- Import upper-arm cuff readings.
- Import reference pulse oximeter data.
- Import reference ECG timestamps where available.
- Pair sensor windows with references.
- Compute bias, mean absolute error, root mean square error, correlation, Bland-Altman limits, coverage, dropout, and motion-stratified performance.

### Phase 3 — Sleep/PAP evidence module

- Overnight SpO2 and pulse waveform.
- Respiration signal.
- Body position.
- Mask pressure and humidity.
- Room humidity and temperature.
- Mouth-opening or jaw-position proxy.
- Awakening markers.

### Phase 4 — Fluid analytics

- Saliva flow by timed mass or volume.
- Saliva and urine strip imaging under fixed lighting.
- Urine specific gravity integration.
- Finger-stick meter imports.
- Sample identifiers and chain-of-custody records.

### Phase 5 — CBC research workstation

- Capillary sample identification.
- Hemoglobin import or optical measurement.
- Microhematocrit imaging and calculation.
- Standardized blood-smear preparation and imaging.
- Cell image segmentation and human-review interface.
- Paired validation against laboratory CBC results.

## Initial validation references

- Blood pressure: validated upper-arm cuff used during calibration and validation sessions.
- ECG and heart rate: clinical ECG or validated single-lead reference when available.
- Oxygen saturation: recording pulse oximeter used simultaneously.
- Glucose: commercial meter or CGM paired with timestamped readings.
- Hemoglobin and CBC: accredited laboratory result from the same sampling interval.
- PAP: machine SD-card export when accessible plus independent mask-pressure and oxygen capture.

## Required data labels

Every output must carry one of:

- `measured`
- `reference_measured`
- `calculated`
- `estimated`
- `experimentally_inferred`
- `validated_for_personal_trend`
- `validated_against_reference`

## Known remaining files

- `SYSTEM_ARCHITECTURE.md`
- `VALIDATION_PROTOCOL.md`
- `DATA_SCHEMA.md`
- `HARDWARE_BOM.md`
- `CBC_WORKSTATION.md`
- `PAP_EVIDENCE_MODULE.md`
- reference-pairing scripts
- synthetic and paired test fixtures
- hardware firmware and enclosure files

## Destination

`StegVerse-Labs/StegVerse-SCW/docs/patient-owned-monitoring/`

## Ownership

Continuation may be performed by any authorized session or automation that reads this handoff first and records changes and validation evidence here.
