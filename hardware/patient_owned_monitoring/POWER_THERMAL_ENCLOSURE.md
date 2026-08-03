# Patient-Owned Monitoring Power, Thermal, and Enclosure Contract

Status: A0 design and verification contract; physical validation remains blocked.

## Power budget

The hardware lane must record measured current for boot, idle, ordinary acquisition, peak acquisition, storage write, radio transfer, recovery, and fault states. A 24-hour operating claim requires measured energy with at least 20% reserve after battery aging and temperature derating.

Required machine-readable fields: battery chemistry, nominal and minimum capacity, charge limit, discharge cutoff, regulator efficiency, state currents, state durations, projected runtime, measured runtime, test temperature, firmware version, and instrumentation.

## Charging and battery protection

- Cell protection must cover overcharge, over-discharge, overcurrent, and short circuit.
- Charging must stop or derate outside the cell manufacturer's allowed temperature range.
- Acquisition while charging is disabled by default unless patient isolation and noise performance are verified.
- Swelling, enclosure deformation, abnormal temperature, or protection trips block body-worn use.

## Thermal limits

The design must measure enclosure skin-contact temperature during maximum sensor, radio, storage, and charging loads. Firmware must record thermal warnings and enter a safe reduced-power state before the approved contact-temperature limit is exceeded. Unknown sensor state blocks thermal assurance.

## Enclosure requirements

- Separate battery access from removable evidence storage where practical.
- Prevent accidental electrode, optical, or pressure-sensor movement.
- Provide strain relief and keyed connectors.
- Make the event marker operable without visual attention.
- Document ingress, sweat, cleaning-agent, drop, strap, and repeated-opening tests.
- Tamper indicators must not interfere with patient access to their own evidence.
- Recovery access must remain available without defeating battery protection or evidence authentication.

## Mechanical artifacts

Commit source CAD, export format, dimensional drawing, materials, fasteners, gasket/adhesive specification, sensor-contact insert, tolerance notes, and artifact hashes. Prototype prints are not production evidence.

## Required tests

1. measured runtime under the protocol acquisition profile;
2. brownout during storage write;
3. charger connect/disconnect transitions;
4. maximum-load thermal soak;
5. blocked vent or insulating-cover challenge;
6. drop and strap-pull test;
7. sweat/cleaning exposure;
8. storage removal without battery-compartment exposure;
9. recovery access after host/application loss.

Failures and exclusions remain in the receipt with reasons; they are not deleted from the record.