from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# region Bus Classes
@dataclass(kw_only=True)
class Bus(ABC):
    bus_idx: int  # Bus ID
    voltage_level_kv: float  # Line-to-line voltage level
    coordinates: str  # Bus coordinates in geojson string format
    bus_name: str = 'NA'  # Bus name
    energized: bool = True
    voltage_magnitude_pu: float = field(init=False, default=1)  # Simulation instant voltage magnitude
    voltage_angle_rad: float = field(init=False, default=0)  # Simulation instant voltage angle

    def __post_init__(self):
        if self.bus_name == 'NA':
            self.bus_name = f'Bus {self.bus_idx}'
# endregion


# region Shunt Classes
@dataclass(kw_only=True)
class Shunt_Element(ABC):  # TODO: If two of the same type of shunt element is connected to the same bus give them an internal ID (Bus 1 Load 1, Bus 1 Load 2 etc.)
    idx: int   # Equipment ID
    bus: Bus  # Bus clss instant that the shunt equipment is connected
    name: str = 'NA'  # Name of the equipment


@dataclass
class Load(Shunt_Element):
    s_rated_mva: float  # Rated S of the load
    p_mw: float = field(init=False, default=0.0)  # Simulation instant P
    q_mvar: float = field(init=False, default=0.0)  # Simulation instant Q

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Load {self.idx} '


@dataclass
class Generator(Shunt_Element):
    min_p_mw: float  # Generator minimum P limit
    max_p_mw: float  # Generator maximum P limit
    min_q_mvar: float  # Generator minimum Q limit
    max_q_mvar: float  # Generator maximum Q limit
    p_mw: float = field(init=False, default=0.0)  # Simulation instant P
    q_mvar: float = field(init=False, default=0.0)  # Simulation instant Q

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Generator {self.idx} '


@dataclass
class Battery(Shunt_Element):
    p_mw: float = field(init=False, default=0.0)  # Simulation instant P
    p_charge_mw: float  # Max Charge Value (Positive)
    p_discharge_mw: float  # Max Discharge Value (Negative)
    soc: float  # State of charge (0-1)
    capacity_mwh: float  # Energy capacity

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Battery {self.idx} '


@dataclass
class Shunt(Shunt_Element):
    p_mw: float  # Shunt element P
    q_mvar: float  # Shunt element Q

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Shunt {self.idx} '

# endregion


# region Branch Classes
@dataclass(kw_only=True)
class Branch(ABC):
    idx: int  # Branch element ID
    from_bus: Bus  # Bus class instant of the "from" bus
    to_bus: Bus  # Bus class instant of the "to" bus
    closed: bool = True  # True means switches are closed and the branch is active


@dataclass
class Line(Branch):
    r_ohm: float = 0  # Series resistance
    x_ohm: float = 0   # Series reactance
    b_total_mho: float = 0  # Shunt admittance of pi model


@dataclass
class Transformer(Branch):  # from_bus is HV and to_bus is LV
    v_rated_high_kv: float  # high voltage side line-to-line rated voltage
    v_rated_low_kv: float  # low voltage side line-to-line rated voltage
    rated_s_mva: float  # rated power of the transformer
    r_pu: float = 0  # Copper losses
    x_pu: float = 0  # leakage losses
    gm_pu: float = 0  # Core loss resistance
    bm_pu: float = 0  # Magnetizing reactance loss
    tap: float = 1  # Tap changing transformer tap in pu
    phase_shift: float = 0  # Phase shifting transformer phase shift in degrees


@dataclass
class SOP(Branch):
    rated_s: float  # rated power of SOP
    pf_mw: float = 0  # Simulation instant P to the "from" side
    pt_mw: float = 0  # Simulation instant P to the "to" side
    qf_mvar: float = 0  # Simulation instant Q to the "from" side
    qt_mvar: float = 0  # Simulation instant Q to the "to" side
    efficiency: float = 1  # Efficiency that binds "pf_mw" and "pt_mw" together (0-1)
# endregion


# region Bus Measurements
@dataclass(kw_only=True)
class Bus_Measurement(ABC):
    measurement_idx: int
    bus: Bus
    std_dev: float
    value_pu: float
    measurement_type: str
# endregion


# region Branch Measurements
@dataclass
class Branch_Measurement(ABC):
    measurement_idx: int
    from_bus: Bus
    to_bus: Bus
    std_dev: float
    value_pu: float
    measurement_type: str


# endregion
