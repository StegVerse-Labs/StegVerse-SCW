# Patient-Owned Monitoring System Architecture

## 1. System objective

Create a modular, continuously recording system that can capture long warning phases, short episodes, sleep/PAP behavior, and paired fluid-test results while preserving raw evidence and explicit provenance.

## 2. Core modules

### 2.1 Wearable evidence recorder

Sensors:

- single-lead ECG
- multiwavelength PPG
- 6-axis IMU
- skin temperature
- skin-contact pressure
- optional galvanic skin response
- physical event button

Core functions:

- common hardware clock
- local append-only storage
- configurable sampling rates
- packet sequence numbers
- battery voltage and charge state
- sensor saturation and contact-quality flags
- BLE synchronization without making BLE the sole storage path

Recommended prototype stack:

- MCU: Nordic nRF52840-class controller
- ECG/PPG AFE: MAX86150/MAX86176-class synchronized optical and ECG front end, or ADS1292R plus separate PPG AFE
- IMU: low-power 6-axis accelerometer/gyroscope
- storage: microSD or high-endurance SPI flash
- real-time clock: temperature-compensated RTC where practical

### 2.2 Reference pairing station

Inputs:

- validated upper-arm cuff readings
- reference pulse oximeter export
- commercial glucose meter or CGM export
- clinical or validated single-lead ECG timestamps
- laboratory CBC/hemoglobin results

Functions:

- clock-offset estimation
- measurement-window linking
- calibration/validation partitioning
- quality-control review
- paired-record export

### 2.3 Sleep/PAP evidence module

Sensors:

- overnight finger or ear PPG
- respiratory effort belt or impedance respiration
- mask pressure sensor
- in-mask temperature/humidity sensor
- room temperature/humidity sensor
- head or mask IMU
- optional jaw-position sensor
- awakening/event marker

Outputs:

- raw SpO2 and pulse waveform
- respiratory waveform
- body position
- mask-pressure waveform
- humidity trajectory
- leak proxies
- awakening correlation windows

### 2.4 Fluid analytics dock

Functions:

- fixed-lighting image capture
- calibration-card detection
- timed strip reading
- sample mass or volume capture
- barcode or QR sample identity
- immutable sample timestamp

Supported first-stage assays:

- saliva flow
- saliva pH
- urine dipstick imaging
- urine specific gravity import
- glucose/ketone meter import
- hemoglobin meter import

### 2.5 CBC research workstation

Stage 1:

- capillary sample tracking
- hemoglobin reference import
- microhematocrit tube imaging
- hematocrit calculation

Stage 2:

- standardized smear-spreading jig
- fixed stain timing
- microscope camera
- motorized or indexed stage
- cell candidate segmentation
- human review and correction

Stage 3:

- experimental optical or impedance microfluidic counting cartridge
- reference beads
- dilution tracking
- clot/bubble detection

## 3. Data flow

1. Each device writes raw frames locally.
2. Frames contain monotonic timestamp, wall-clock timestamp, sequence number, sensor configuration, and quality flags.
3. Sync events estimate clock offset and drift.
4. Reference readings are imported without alteration.
5. Pairing records link a reference value to a defined raw-data window.
6. Algorithms generate derived features and estimates into separate versioned records.
7. Validation runs compare estimates to held-out reference records.
8. Reports retain links back to raw source windows.

## 4. Minimum raw sampling targets

- ECG: 250 Hz minimum; 500 Hz preferred for development
- PPG: 100 Hz minimum; 200 Hz preferred for morphology work
- IMU: 50–100 Hz
- temperature: 1 Hz
- contact pressure: 10–25 Hz
- mask pressure: 50–100 Hz
- room and mask humidity: 1 Hz
- event button: interrupt-driven with timestamp latency measured

## 5. Hemodynamic feature pipeline

Raw inputs:

- ECG R-wave timing
- PPG foot, peak, notch, width, area, slope, and amplitude
- pulse arrival time
- pulse transit proxies
- beat-to-beat interval
- contact pressure
- temperature
- posture and motion

Derived layers:

1. beat detection
2. signal-quality scoring
3. morphology extraction
4. rolling personal baseline
5. abrupt-change detector
6. slow-drift detector
7. experimental systolic/diastolic estimator
8. confidence and out-of-distribution score

## 6. Episode capture behavior

The system must preserve:

- at least 30 minutes before an event marker
- the full marked event
- at least 60 minutes after the event
- continuous low-rate summaries for the full day
- full-rate raw signals for configurable rolling windows or all-day storage when capacity permits

Automatic triggers should include:

- pulse-wave amplitude collapse
- abrupt pulse-arrival-time shift
- heart-rate discontinuity
- motion-to-stillness transition
- posture change
- oxygen decline
- manual event marker

## 7. Data provenance

Every derived record must include:

- algorithm name and version
- source file hashes
- source time range
- calibration profile ID
- device firmware version
- sensor configuration
- quality exclusions
- output label
- validation status

## 8. Security and ownership

- local-first storage
- user-held encryption keys
- exportable open formats
- append-only evidence logs
- cryptographic hashes for raw sessions
- explicit, granular sharing bundles
- no required vendor cloud for core operation

## 9. Initial implementation boundary

The first implementation target is a recorder and validation harness, not a polished consumer device. Success means:

- synchronized raw signals are captured reliably;
- reference readings can be paired reproducibly;
- signal quality and dropouts are measurable;
- algorithm outputs are traceable;
- validation can be repeated from stored data.
