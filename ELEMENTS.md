## Backend
### Class Hierarchy

```
ABC
├── Bus
├── Shunt_Element
│   ├── Load
│   ├── Generation
│   ├── Battery
│   └── Shunt
├── Branch
│   ├── Line
│   ├── Transformer
│   └── SOP
└── Measurement
    ├── Bus_Measurement
    └── Branch_Measurement
```

### Abstract Base Classes

The power system topology is built upon four main classes that inherit from Python's ABC (Abstract Base Class), each modeling a fundamental component of electrical power systems:

1. Bus (ABC) - Power System Node

| Property Name              | Data Type | Explanation                                                |
|---------------------------|-----------|-----------------------------------------------------------|
| bus_idx                   | int       | Bus number for unique identification                       |
| voltage_level_kv          | float     | Nominal line-to-line voltage level of the bus in kV       |
| load_flow_type            | str       | Bus type for power flow analysis (PQ/PV/Slack)            |
| bus_name                  | str       | Descriptive name of the bus (defaults to 'Bus {bus_idx}') |
| set_voltage_magnitude_kv  | float     | Target voltage magnitude for voltage regulation           |
| set_voltage_angle_degree  | float     | Target voltage angle (significant for Slack bus)          |
| voltage_magnitude_pu      | float     | Actual voltage in per-unit (base: voltage_level_kv)      |
| voltage_angle_degree      | float     | Actual voltage phase angle (0° for Slack bus)            |
| coordinates               | tuple     | (x,y) coordinates for network visualization               |

**Bus Types in Power Flow:**
- PQ Bus: Load bus with constant active and reactive power consumption
- PV Bus: Generator bus with constant active power and regulated voltage
- Slack Bus: Reference bus providing system voltage and angle reference

2. Shunt_Element (ABC) - Single Bus Connected Devices

| Property Name | Data Type | Explanation                                           |
|--------------|-----------|-------------------------------------------------------|
| idx          | int       | Unique identifier for the shunt element               |
| bus          | Bus       | Reference to the connection bus                       |
| name         | str       | Descriptive name (defaults to 'NA')                   |

#### Derived Classes from Shunt_Element
- Load: Consumer of power
  - p_mw: Active power demand (positive for consumption)
  - q_mvar: Reactive power demand (positive for inductive loads)
  
- Generation: Power producer with voltage control
  - p_mw: Active power output (negative for generation)
  - voltage_magnitude_kv: Terminal voltage setpoint for AVR
  
- Battery: Energy storage system
  - p_mw: Instantaneous power (+ charging, - discharging)
  - p_charge_max_mw: Maximum charging rate
  - p_discharge_max_mw: Maximum discharge rate
  - soc: State of Charge (0-100%)
  - capacity_mwh: Energy storage capacity
  
- Shunt: Reactive power compensation device
  - p_mw: Active power losses
  - q_mvar: Reactive power (+ capacitive, - inductive)

3. Branch (ABC) - Two Bus Connected Devices

| Property Name | Data Type | Explanation                                           |
|--------------|-----------|-------------------------------------------------------|
| idx          | int       | Unique identifier for the branch                      |
| from_bus     | Bus       | Source/sending end bus                               |
| to_bus       | Bus       | Destination/receiving end bus                        |
| closed       | bool      | Operational status (True=in service)                  |

#### Derived Classes from Branch
- Line: AC Transmission/Distribution Line
  - r_ohm: Series resistance (temperature dependent)
  - x_ohm: Series reactance (geometry dependent)
  - b_total_mho: Total shunt susceptance (π-model)

- Transformer: Voltage Level Controller
  - z_base: Base impedance for per-unit conversion
  - r_pu, x_pu: Series impedance
  - gm_pu, bm_pu: Magnetizing admittance
  - tap: Voltage ratio control (e.g., 0.9-1.1)
  - phase_shift: Phase angle control (degrees)

- SOP (Soft Open Point): Power Electronic Device
  - rated_s: VA capacity
  - p_mw: Active power transfer
  - q_mvar_from_to, q_mvar_to_from: Independent reactive power control
  - efficiency: Power conversion efficiency

4. Measurement (ABC) - System State Observers

#### Bus_Measurement (ABC)
| Property Name     | Data Type | Explanation                                           |
|------------------|-----------|-------------------------------------------------------|
| measurement_idx  | int       | Unique identifier for measurement point               |
| bus             | Bus       | Monitored bus                                        |
| std_dev         | float     | Measurement uncertainty (1σ)                         |
| value_pu        | float     | Measured quantity in per-unit                        |
| measurement_type | str       | Type of measurement (see below)                      |

**Bus Measurement Types:**
- v: Voltage magnitude
- θ: Voltage angle
- p: Active power injection
- q: Reactive power injection

#### Branch_Measurement (ABC)
| Property Name     | Data Type | Explanation                                           |
|------------------|-----------|-------------------------------------------------------|
| measurement_idx  | int       | Unique identifier for measurement point               |
| from_bus        | Bus       | Flow measurement sending bus                          |
| to_bus          | Bus       | Flow measurement receiving bus                        |
| std_dev         | float     | Measurement uncertainty (1σ)                         |
| value_pu        | float     | Measured quantity in per-unit                        |
| measurement_type | str       | Type of measurement (see below)                      |

**Branch Measurement Types:**
- i: Current magnitude
- pf: Active power flow
- qf: Reactive power flow

Note: Measurement classes provide input for state estimation algorithms. Bus_Measurement handles nodal quantities (voltages, injections), while Branch_Measurement handles flow quantities (currents, power flows). The standard deviation (std_dev) represents measurement uncertainty used in weighted least squares estimation.

