# Patient-Owned Monitoring Data Schema

## 1. Design requirements

- raw-first
- append-only session records
- nanosecond-capable timestamps where available
- original and corrected clocks both retained
- explicit units
- explicit missingness
- sensor and algorithm versioning
- source hashes on every derived artifact
- open serialization formats

Recommended storage:

- JSON Lines for manifests, events, references, and derived records
- Parquet or Arrow for high-volume tabular signals
- binary sensor blocks only when accompanied by an open decoder and manifest

## 2. Session manifest

```json
{
  "schema_version": "pom.session.v1",
  "session_id": "uuid",
  "subject_id": "user-controlled-pseudonym",
  "device_id": "wearable-001",
  "device_type": "wearable|pap-module|fluid-dock|cbc-workstation|reference",
  "firmware_version": "0.1.0",
  "hardware_revision": "A0",
  "start_time_utc": "2026-07-21T12:00:00.000000Z",
  "end_time_utc": null,
  "timezone": "America/Chicago",
  "monotonic_clock_hz": 1000000,
  "clock_sync_profile_id": "sync-uuid",
  "raw_files": [],
  "configuration": {},
  "created_by": "device|importer|operator",
  "manifest_sha256": ""
}
```

## 3. Raw signal frame

```json
{
  "schema_version": "pom.signal-frame.v1",
  "session_id": "uuid",
  "stream_id": "ecg-1",
  "sequence": 1204,
  "monotonic_start": 882001234,
  "wall_time_original_utc": "2026-07-21T12:00:01.234000Z",
  "wall_time_corrected_utc": "2026-07-21T12:00:01.233912Z",
  "clock_correction_us": -88,
  "sample_rate_hz": 500,
  "sample_count": 250,
  "unit": "uV",
  "encoding": "int24-le",
  "scale": 0.286,
  "offset": 0,
  "quality_flags": [],
  "payload_ref": "signals/ecg-1/000001204.bin",
  "payload_sha256": ""
}
```

## 4. Stream definition

Required stream names:

- `ecg`
- `ppg-red`
- `ppg-ir`
- `ppg-green`
- `imu-accel`
- `imu-gyro`
- `skin-temp`
- `contact-pressure`
- `eda`
- `spo2-reference`
- `mask-pressure`
- `mask-humidity`
- `room-humidity`
- `respiration`
- `jaw-position`

Each stream definition records:

- sensor model
- serial number where available
- channel
- sample rate
- ADC resolution
- gain
- units
- placement
- calibration profile
- operating range

## 5. Event record

```json
{
  "schema_version": "pom.event.v1",
  "event_id": "uuid",
  "session_id": "uuid",
  "event_type": "manual-marker|warning-start|episode|awakening|medication|meal|posture-change|reference-measurement",
  "start_time_utc": "2026-07-21T14:02:11.100000Z",
  "end_time_utc": null,
  "timestamp_source": "hardware-button|app|observer|algorithm|import",
  "timestamp_uncertainty_ms": 25,
  "severity": null,
  "attention_state": "low-stimulation|ordinary|high-focus|unknown",
  "posture": "supine|seated|standing|walking|unknown",
  "notes": "",
  "tags": [],
  "source_record_sha256": ""
}
```

## 6. Reference measurement

```json
{
  "schema_version": "pom.reference.v1",
  "reference_id": "uuid",
  "reference_type": "bp-cuff|ecg|pulse-oximeter|glucose-meter|cgm|lab-cbc|hemoglobin|hematocrit|pap-export",
  "device_manufacturer": "",
  "device_model": "",
  "device_id": "",
  "measurement_time_utc": "2026-07-21T14:10:00Z",
  "time_uncertainty_ms": 1000,
  "values": [
    {"name": "systolic", "value": 132, "unit": "mmHg"},
    {"name": "diastolic", "value": 84, "unit": "mmHg"},
    {"name": "pulse", "value": 76, "unit": "bpm"}
  ],
  "conditions": {
    "posture": "seated",
    "arm": "left",
    "cuff_size": "large",
    "activity_before_minutes": 5
  },
  "raw_attachment_refs": [],
  "record_sha256": ""
}
```

## 7. Pairing record

```json
{
  "schema_version": "pom.pairing.v1",
  "pairing_id": "uuid",
  "reference_id": "uuid",
  "source_session_ids": ["uuid"],
  "window_start_utc": "2026-07-21T14:05:00Z",
  "window_end_utc": "2026-07-21T14:12:00Z",
  "pairing_method": "protocol-defined",
  "dataset_partition": "calibration|development|validation|challenge",
  "quality_decision": "include|exclude|review",
  "quality_reasons": [],
  "operator": "",
  "pairing_sha256": ""
}
```

## 8. Derived feature record

```json
{
  "schema_version": "pom.feature.v1",
  "feature_id": "uuid",
  "session_id": "uuid",
  "feature_name": "pulse-arrival-time",
  "start_time_utc": "2026-07-21T14:09:59.000000Z",
  "end_time_utc": "2026-07-21T14:10:00.000000Z",
  "value": 182.4,
  "unit": "ms",
  "output_label": "calculated",
  "algorithm": {
    "name": "pat-extractor",
    "version": "0.1.0",
    "container_digest": "",
    "parameters": {}
  },
  "source_streams": ["ecg-1", "ppg-ir-1"],
  "source_window_sha256": "",
  "quality": {
    "score": 0.94,
    "flags": []
  }
}
```

## 9. Estimate record

```json
{
  "schema_version": "pom.estimate.v1",
  "estimate_id": "uuid",
  "estimate_type": "systolic-bp|diastolic-bp|hemodynamic-change|episode-probability|mouth-open-state",
  "time_utc": "2026-07-21T14:10:00Z",
  "value": -18.2,
  "unit": "mmHg-change",
  "output_label": "experimentally_inferred",
  "confidence": 0.81,
  "validation_class": "V2_REFERENCE_PAIRED",
  "model": {
    "name": "personal-hemodynamic-change",
    "version": "0.1.0",
    "calibration_profile_id": "uuid",
    "training_dataset_hash": ""
  },
  "source_feature_ids": [],
  "out_of_distribution": false,
  "flags": []
}
```

## 10. Fluid sample record

```json
{
  "schema_version": "pom.sample.v1",
  "sample_id": "uuid",
  "sample_type": "saliva|urine|capillary-blood|blood-smear|microhematocrit",
  "collection_start_utc": "2026-07-21T08:00:00Z",
  "collection_end_utc": "2026-07-21T08:05:00Z",
  "collection_method": "",
  "container_tare_g": 4.120,
  "sample_mass_g": 1.230,
  "sample_volume_ml": null,
  "lot_ids": [],
  "image_refs": [],
  "chain_of_custody": [],
  "sample_sha256": ""
}
```

## 11. CBC comparison record

```json
{
  "schema_version": "pom.cbc-comparison.v1",
  "comparison_id": "uuid",
  "sample_id": "uuid",
  "home_results": {},
  "laboratory_reference_id": "uuid",
  "time_difference_minutes": 25,
  "analysis_version": "0.1.0",
  "differences": {},
  "review_status": "pending|reviewed|accepted|rejected",
  "review_notes": ""
}
```

## 12. Required integrity rules

- sequence gaps are recorded, never silently interpolated
- corrected timestamps never overwrite original timestamps
- raw payloads are immutable after session closure
- every transformed dataset references source hashes
- excluded records remain present with exclusion reasons
- units are mandatory
- null means unavailable; zero is a measured value
- validation class is attached to every estimate
- algorithm changes create new versions and never rewrite prior results
