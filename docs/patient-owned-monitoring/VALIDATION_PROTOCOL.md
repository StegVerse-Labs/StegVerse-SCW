# Validation Protocol

## 1. Purpose

Validate each sensor and derived metric for its intended use by collecting simultaneous paired measurements against a known reference device or laboratory result.

The first intended use is personal longitudinal evidence and episode correlation. Each metric may later receive a broader validation class only after separate testing.

## 2. Validation classes

- `V0_CAPTURE`: raw signal is stored with timestamps and quality flags.
- `V1_REPEATABLE`: repeated measurements under the same condition are stable.
- `V2_REFERENCE_PAIRED`: simultaneous paired reference data exist.
- `V3_PERSONAL_TREND`: direction and magnitude of change are reliable for the individual.
- `V4_PERSONAL_ABSOLUTE`: absolute values meet predefined error limits for the individual.
- `V5_MULTI_PERSON`: performance is validated across multiple people and conditions.

## 3. Dataset partitioning

Each paired record must be assigned before model fitting to one of:

- calibration
- development
- validation
- challenge

No validation or challenge record may be used to tune the model.

Recommended first personal dataset split:

- 50% calibration
- 20% development
- 20% validation
- 10% challenge conditions

Split by session or day, not by random individual beats, to prevent leakage.

## 4. Clock validation

Before physiological validation:

1. Generate a common visible or electrical synchronization event.
2. Record it on every device.
3. Calculate initial clock offset.
4. Repeat after 2, 8, 12, and 24 hours.
5. Fit clock drift in milliseconds per hour.
6. Correct timestamps while retaining original timestamps.

Initial acceptance target:

- paired-device alignment error under 100 ms for beat-level ECG/PPG work
- under 1 second for cuff, glucose, saliva, urine, and CBC pairing

## 5. Wearable signal validation

### 5.1 Heart rate

Reference:

- simultaneous ECG-derived heart rate

Conditions:

- seated rest
- standing
- slow walking
- ordinary household movement
- postural transition
- controlled paced breathing
- low-stimulation seated period

Metrics:

- beat detection sensitivity
- positive predictive value
- heart-rate mean absolute error
- dropout percentage
- performance by motion class

Initial personal acceptance target:

- resting HR MAE at or below 3 bpm
- active HR MAE at or below 5 bpm
- valid coverage above 90% during rest and 75% during ordinary movement

### 5.2 PPG morphology

Reference:

- stable reference pulse oximeter waveform or research PPG channel

Metrics:

- waveform correlation after alignment
- pulse-foot timing error
- pulse-amplitude repeatability
- morphology-feature coefficient of variation
- saturation and contact-loss rates

### 5.3 Oxygen saturation

Reference:

- simultaneous recording pulse oximeter

Protocol:

- overnight paired wear
- stable rest periods
- posture changes
- repeated nights

Metrics:

- bias
- MAE
- percentage within 2 and 3 percentage points of reference
- dropout and low-perfusion failure rates

### 5.4 Posture and motion

Reference:

- scripted labeled movements and optional synchronized video

Classes:

- lying left
- lying right
- supine
- prone where applicable
- sitting
- standing
- walking
- transition
- stillness

Metrics:

- confusion matrix
- precision and recall per class
- transition timing error

## 6. Blood-pressure and hemodynamic validation

### 6.1 Reference collection

Use a validated upper-arm cuff during calibration sessions while the wearable records continuously.

For each cuff reading:

1. Mark cuff inflation start.
2. Mark result time.
3. Preserve the raw wearable window from five minutes before through two minutes after.
4. Record posture, arm position, activity, medication timing, food, hydration, and symptoms.
5. Reject readings only through predefined quality rules.

### 6.2 Conditions

Collect paired readings across:

- morning and evening
- before and after medication
- seated rest
- supine rest
- standing at 1, 3, 5, and 10 minutes
- after mild activity
- long warning phases
- symptom-free periods

### 6.3 Minimum first dataset

- 100 paired cuff readings
- at least 10 separate days
- at least 20 standing or postural-transition readings
- at least 20 readings during warning phases where practical
- full pressure range represented rather than repeated near-identical values

### 6.4 Metrics

Absolute estimation:

- systolic and diastolic bias
- MAE
- RMSE
- Bland-Altman limits of agreement
- error by posture, motion, temperature, contact pressure, and time since calibration

Change detection:

- sensitivity for reference-confirmed decreases
- false-alert rate per hour
- detection latency
- magnitude correlation
- area under precision-recall curve

### 6.5 Initial useful acceptance criteria

Personal trend detector:

- at least 85% sensitivity for reference-confirmed systolic changes of 15 mmHg or more
- no more than one false major-change alert per eight recording hours
- median detection latency under 30 seconds for abrupt signal changes

Absolute personal estimate:

- define only after held-out validation
- publish measured bias and limits rather than assigning a pass label without evidence

## 7. Episode validation

An episode record must include:

- manual event marker or independently observed timestamp
- pre-event raw window
- event raw window
- recovery raw window
- attention/stimulation state
- posture
- medication timing
- sleep duration
- reference measurements available near the event

Analysis compares:

- event versus personal baseline
- event versus matched non-event low-stimulation periods
- warning phase versus immediate event
- stimulant-present versus stimulant-absent periods when naturally occurring and documented

Primary outputs:

- signals that consistently change before events
- earliest detectable deviation
- within-person repeatability
- false positives during non-event periods

## 8. PAP module validation

Reference pairing:

- PAP machine SD-card data when available
- reference recording pulse oximeter
- synchronized awakening markers

Validate:

- mask-pressure waveform timing
- humidity measurement
- respiratory rate
- body position
- mouth-opening proxy
- awakening detection

A PAP evidence session should preserve the entire night and identify:

- dry-mouth awakening time
- mask pressure and humidity preceding awakening
- oxygen and pulse changes
- body and jaw position
- recovery after mask removal or repositioning

## 9. Fluid-test validation

### 9.1 Saliva flow

Reference method:

- fixed-duration collection measured both by volume and by mass using water-equivalent approximation, with container tare recorded

Validation:

- duplicate collections
- operator repeatability
- before/after PAP comparisons
- scale calibration with known masses

### 9.2 Strip imaging

Reference:

- manufacturer color chart plus laboratory result where available

Validation controls:

- fixed illumination
- fixed camera distance
- color calibration card
- exact reagent-pad timing
- duplicate image capture

Metrics:

- category agreement
- weighted kappa
- repeatability across lighting sessions

### 9.3 Glucose and ketones

Reference:

- commercial meter or CGM export

Pair within the shortest supported timing window and record sample source, meal timing, and device lot where available.

## 10. CBC workstation validation

### 10.1 Hematocrit

- collect capillary microhematocrit sample
- image packed-cell and plasma columns
- calculate ratio automatically
- compare with laboratory hematocrit from the closest practical sampling interval

Metrics:

- bias
- MAE
- image segmentation repeatability
- inter-operator repeatability

### 10.2 Hemoglobin

- import or capture a commercial point-of-care hemoglobin reading
- pair with laboratory hemoglobin
- retain cartridge lot, device ID, timestamp, and sample conditions

### 10.3 Smear imaging

Reference:

- laboratory CBC differential and, where available, expert smear review

Validation:

- blinded image set
- human-corrected labels
- cell-level precision and recall
- slide-level count agreement
- morphology disagreement log

## 11. Reporting

Every validation report must include:

- intended use
- device versions
- firmware and algorithm versions
- dataset dates
- calibration/development/validation split
- exclusions and reasons
- missing-data rate
- all predefined metrics
- confidence intervals where practical
- failure-condition examples
- raw-data hashes
- reproducible analysis command

## 12. Promotion rule

A metric advances to a higher validation class only through a committed report containing the paired dataset description, analysis version, results, and acceptance decision.
