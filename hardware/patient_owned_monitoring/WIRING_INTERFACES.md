# Patient-Owned Monitoring Wiring and Bus Interface Contract

Status: A0 implementation contract; schematic and bench conformance remain unvalidated.

## Bus allocation

| Bus | Device class | Requirements |
|---|---|---|
| SPI0 | ECG/PPG front end | dedicated chip select, data-ready interrupt, bounded DMA, no shared removable storage |
| SPI1 | microSD or SPI flash | separate power domain where feasible, brownout-safe write policy |
| SPI2 | IMU | dedicated chip select and interrupt |
| I2C0 | RTC, temperature, fuel gauge | address inventory, pull-up calculation, bus recovery |
| ADC | contact-pressure channel | protected input, documented scale and saturation flags |
| GPIO | event button, tamper, power-fail | debounced or interrupt-latched; state transitions receipted |
| USB | charge and governed recovery | data path disabled by default or authenticated before access |

## Electrical safety and integrity

- Patient-contact analog front ends must use the component manufacturer's reference protection, current limiting, ESD protection, and isolation guidance.
- No mains-connected debug, charge, or measurement equipment may be attached during body-worn acquisition unless the complete isolation path is verified for that configuration.
- ECG electrode paths and optical/contact sensors must be protected from charger and USB fault domains.
- Sensor rails must have test points and current measurement access without bypassing protection.
- Shared grounds, shielding, cable length, and return paths must be documented in the schematic receipt.

## Required nets

Each schematic must identify battery raw, protected battery, regulated rails, analog ground, digital ground, charger status, power-fail, RTC interrupt, front-end data-ready, IMU interrupt, storage chip select, event input, debug enable, and tamper input.

## Fault behavior

- Bus lockup invokes bounded recovery and records the affected bus and devices.
- Storage failure does not block event marking; it raises an explicit evidence-loss state.
- Sensor disconnects produce null values and fault flags, not synthetic zeros.
- Repeated faults trigger a safe recording degradation state with an operator-visible receipt.

## Wiring artifact requirements

The hardware lane must commit:

1. source schematic;
2. human-readable PDF or image export;
3. netlist or machine-readable connection table;
4. connector pinout;
5. approved substitutions;
6. protection and isolation notes;
7. measured rail voltages and idle/acquisition currents;
8. wiring hash in the bench receipt.

No wiring diagram is considered validated until continuity, short-circuit, rail, and sensor-enumeration checks are recorded.