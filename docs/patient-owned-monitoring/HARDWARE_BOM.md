# Patient-Owned Monitoring Hardware BOM

## Revision A0 objective

Build a continuously recording, body-worn evidence recorder with synchronized ECG, multi-wavelength PPG, motion, posture, skin temperature, contact pressure, event marking, local storage, and reference-device pairing.

## Core wearable

| Function | Preferred component | Alternate | Interface | Initial rate |
|---|---|---|---|---:|
| MCU + BLE | Nordic nRF52840 module | ESP32-S3 module | native | control |
| ECG + synchronized PPG | MAX86150 evaluation module or custom board | ADS1292R + MAX86141 | SPI/I2C | ECG 256–512 Hz; PPG 100–400 Hz |
| Accelerometer + gyroscope | BMI270 | ICM-42688-P | SPI | 100–200 Hz |
| Skin temperature | MAX30208 | TMP117 | I2C | 1–4 Hz |
| Contact pressure | thin-film force sensor + 16-bit ADC | capacitive pressure sensor | ADC/I2C | 10–50 Hz |
| Real-time clock | RV-3028-C7 | DS3231M | I2C | 1 PPS/event |
| Local storage | industrial microSD + level-safe socket | SPI NOR flash | SPI | append-only |
| Event marker | sealed tactile button | capacitive button | GPIO | interrupt |
| Battery telemetry | MAX17048 fuel gauge | LC709203F | I2C | 0.1–1 Hz |
| Power | 500–1000 mAh LiPo + charger/protection | replaceable Li-ion | — | 24 h target |

## Mechanical layout

- Wrist or upper-arm enclosure with replaceable sensor-contact insert.
- ECG dry electrodes positioned to permit single-lead acquisition between two skin contacts.
- Optical block mechanically isolated from the enclosure to reduce ambient-light ingress.
- Contact-pressure sensor beneath the optical block to quantify coupling.
- Event button accessible without looking.
- USB-C charging and data recovery.
- microSD removable without opening the battery compartment.

## Sleep/PAP module

| Function | Component class | Placement | Initial rate |
|---|---|---|---:|
| Reference SpO2/pulse waveform | recording finger or ear sensor with export | finger/ear | 25–100 Hz waveform |
| Mask pressure | low-range differential pressure sensor | mask sampling port | 50–100 Hz |
| Mask humidity/temperature | fast digital RH/T sensor | inside mask edge, outside direct condensate | 1–10 Hz |
| Room humidity/temperature | digital RH/T sensor | bedside | 0.2–1 Hz |
| Respiratory effort | stretch/inductive belt or impedance channel | thorax | 25–100 Hz |
| Jaw position proxy | small IMU or Hall sensor | chin strap/mandible | 25–100 Hz |
| Audio envelope | MEMS microphone | bedside/mask exterior | 8–16 kHz raw or 100 Hz envelope |

## Fluid analytics dock

- Fixed-light enclosure with high-CRI LED illumination.
- Camera mount with fixed focal distance.
- Color reference card holder.
- 0.01 g scale with serial or BLE export.
- Strip tray with indexed timing positions.
- Refractometer image mount for urine specific gravity.
- QR or Data Matrix sample identifiers.

## CBC workstation A0

- Commercial capillary lancets and collection tubes.
- Microhematocrit capillary tubes and sealing clay.
- Enclosed microhematocrit centrifuge with fixed speed timer.
- Backlit imaging jig with millimeter scale for packed-cell-volume measurement.
- Optical hemoglobin meter with export or manual-entry reference.
- Microscope with motorized or indexed stage, 40x and 100x objectives, and camera.
- Slide-spreading jig with fixed angle and travel.
- Fixed staining timer and imaging white-balance target.

## Reference equipment

- Validated upper-arm blood-pressure cuff with correct cuff size and timestamped export or manual entry.
- Recording pulse oximeter.
- Commercial glucose meter and/or CGM with export.
- Laboratory CBC and hemoglobin results from the same sampling interval.
- PAP SD-card export when accessible.

## Power and storage targets

- Minimum 24-hour recording without charge.
- Minimum seven days of local raw storage.
- Brownout-safe append-only writes.
- Session manifest written at start; closure record written at clean shutdown.
- Recovery scanner reconstructs sessions after interrupted power.

## Procurement order

1. MCU module, IMU, RTC, storage, battery telemetry, event switch.
2. ECG/PPG evaluation hardware.
3. Pressure and temperature sensors.
4. Reference cuff and recording oximeter.
5. PAP pressure/humidity modules.
6. Fluid dock lighting, camera mount, scale, and strip tray.
7. CBC imaging and hematocrit fixtures.
