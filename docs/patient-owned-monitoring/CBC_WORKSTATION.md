# CBC Research Workstation

## Build objective

Create a staged capillary-blood workstation that records sample identity, measures hematocrit and hemoglobin, images standardized blood smears, and validates every result against a laboratory CBC from the same sampling interval.

## Stage 1 — Sample and hematocrit station

### Hardware

- QR-labelled sample cards and capillary tubes.
- 0.001 g scale for sample and reagent verification.
- Enclosed microhematocrit centrifuge.
- Fixed backlight and camera jig.
- Tube holder with known geometry and calibration scale.

### Processing

1. Create `pom.sample.v1` record before collection.
2. Record tube lot, lancet lot, collection times, and image references.
3. Centrifuge using a versioned speed/time profile.
4. Image the complete tube against the fixed scale.
5. Segment packed red cells, buffy coat, and plasma.
6. Calculate hematocrit as packed-red-cell length divided by total blood-column length.
7. Preserve original image, segmentation mask, operator correction, and algorithm version.

### Validation

- Collect paired samples during the same laboratory draw interval.
- Compare workstation hematocrit to laboratory hematocrit.
- Minimum development set: 30 paired samples covering the observed personal range.
- Hold back at least 20% as validation data.
- Report bias, MAE, RMSE, Bland–Altman limits, repeatability, and operator-review frequency.

## Stage 2 — Hemoglobin station

### Inputs

- Export from a commercial capillary hemoglobin meter, or
- fixed-path optical cartridge with controlled dilution and wavelength capture.

### Records

- raw optical intensity or meter export;
- cartridge and reagent lot;
- temperature;
- replicate measurements;
- laboratory reference result;
- calibration profile and partition.

### Validation

- Three replicates per sample during development.
- Separate within-run repeatability from between-day drift.
- Report error by hematocrit range and sample age.

## Stage 3 — Blood-smear imaging

### Hardware

- Fixed-angle slide-spreading jig.
- Timed drying and staining station.
- Microscope with indexed or motorized stage.
- Camera with locked exposure, gain, white balance, and calibration slide.

### Image workflow

1. Capture full-slide overview.
2. Identify monolayer candidate regions.
3. Acquire tiled high-resolution fields.
4. Segment red cells, white cells, platelets, debris, and overlaps.
5. Store every candidate crop with class probabilities.
6. Provide human correction and retain both original and corrected labels.

### Initial outputs

- red-cell morphology distributions;
- approximate white-cell differential counts;
- platelet candidates per field;
- image-quality and stain-quality metrics;
- explicit review-required flags.

## Stage 4 — Cell-counting cartridge

### Prototype path

- controlled isotonic dilution;
- microfluidic focusing channel;
- optical interruption or impedance sensing;
- reference particles for volume and count calibration;
- bubble, clot, and coincidence detection;
- disposable cartridge ID and lot traceability.

### Paired validation

Each cartridge run must be paired with:

- laboratory RBC, WBC, platelet, hemoglobin, hematocrit, and differential;
- exact collection and processing times;
- dilution volumes and scale readings;
- sensor raw stream;
- cartridge images before and after run.

## Data partitions

- `calibration`: optics, geometry, dilution, and sensor scaling.
- `development`: algorithm selection and thresholds.
- `validation`: untouched paired samples used once for formal evaluation.
- `challenge`: difficult samples, delayed processing, artifacts, and out-of-range conditions.

## Acceptance gates for personal-trend use

### Hematocrit

- replicate coefficient of variation ≤ 3%;
- validation MAE ≤ 3 hematocrit percentage points;
- no unflagged gross error greater than 6 points.

### Hemoglobin

- replicate coefficient of variation ≤ 3%;
- validation MAE ≤ 1.0 g/dL;
- drift control sample remains within predefined lot limits.

### Smear imaging

- ≥ 90% of accepted fields meet focus and stain criteria;
- white-cell classification performance reported per class on held-out labeled images;
- every low-confidence field remains reviewable from the original image.

## Required files to implement next

- `tools/patient_owned_monitoring/hematocrit_image.py`
- `tools/patient_owned_monitoring/sample_manifest.py`
- `tools/patient_owned_monitoring/smear_tile_index.py`
- camera and scale calibration fixtures;
- paired laboratory fixture set;
- validation report generator.
