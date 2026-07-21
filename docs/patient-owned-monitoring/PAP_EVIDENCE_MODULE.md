# Independent PAP Evidence Module

## Purpose

Capture a patient-owned overnight record that can be aligned with PAP usage, awakenings, oral dryness, oxygenation, pulse, respiration, posture, mask pressure, and humidity.

## Channels

| Channel | Rate | Unit | Placement |
|---|---:|---|---|
| SpO2 waveform | 25–100 Hz | percent/raw counts | finger or ear |
| Pulse waveform | 25–100 Hz | raw optical counts | finger or ear |
| Mask pressure | 50–100 Hz | cmH2O | sampling port |
| Mask humidity | 1–10 Hz | %RH | mask interior edge |
| Mask temperature | 1–10 Hz | °C | mask interior edge |
| Room humidity | 0.2–1 Hz | %RH | bedside |
| Room temperature | 0.2–1 Hz | °C | bedside |
| Respiratory effort | 25–100 Hz | normalized/ohms | thorax |
| Jaw position | 25–100 Hz | degrees/vector | chin/mandible |
| Body position | 25–100 Hz | quaternion/vector | torso or wearable |
| Event marker | interrupt | event | bedside button/app |

## Derived records

- `mouth-open-state`
- `mask-pressure-loss`
- `humidity-decay-rate`
- `awakening-window`
- `oxygen-desaturation-window`
- `respiratory-discordance`

Every derived record references its raw windows and algorithm version.

## Synchronization

1. Start wearable, PAP module, and reference oximeter within the same five-minute interval.
2. Record a synchronization marker by pressing all available event buttons and tapping the mask pressure line three times.
3. Repeat the marker at session end.
4. Estimate linear clock offset and drift from the two marker groups.
5. Preserve original timestamps and write corrected timestamps into derived pairing records only.

## Validation sessions

### Bench pressure validation

- Connect the pressure sensor and a reference manometer to the same sealed line.
- Sweep 0–30 cmH2O in 2 cmH2O steps.
- Hold each step for 20 seconds.
- Repeat increasing and decreasing sweeps three times.
- Record bias, hysteresis, RMSE, and temperature dependence.

### Humidity validation

- Place module and reference hygrometer in the same enclosure.
- Test room ambient, humidified airflow, and condensation-prone conditions.
- Record steady-state error and response time to 10–90% transitions.

### Overnight oxygen validation

- Wear module sensor and recording reference oximeter simultaneously.
- Align raw pulse waveforms before comparing saturation summaries.
- Report coverage, dropout, pulse-rate error, saturation bias, and error by motion stratum.

### Mouth-opening validation

- Record synchronized video for short controlled sessions.
- Label mouth-open and mouth-closed intervals manually.
- Compare jaw sensor classification against video labels.
- Keep sleep validation separate from awake development data.

## Nightly report

The report must include:

- session duration;
- raw-channel coverage;
- clock correction and residual alignment error;
- number and timing of awakenings;
- mask pressure and humidity around each awakening;
- oxygen and pulse around each awakening;
- jaw and body position around each awakening;
- PAP export correlation when available;
- links and hashes for every raw file.

## Initial acceptance gates

- Pressure sensor bench RMSE ≤ 0.5 cmH2O across 0–30 cmH2O.
- Humidity median absolute error ≤ 5 %RH after equilibration.
- Clock residual alignment error ≤ 100 ms for waveform comparisons.
- Raw channel coverage ≥ 90% for an overnight session.
- Mouth-opening classifier sensitivity and specificity each ≥ 0.85 on held-out labeled sessions before personal-trend use.
