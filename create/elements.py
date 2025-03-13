from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# region Bus Classes
@dataclass(kw_only=True)
class Bus(ABC):
    bus_idx: int
    voltage_level_kv: float
    load_flow_type: str
    bus_name: str = 'NA'
    set_voltage_magnitude_kv: float
    set_voltage_angle_degree: float
    voltage_magnitude_pu: float = field(init=False, default=1)
    voltage_angle_degree: float = field(init=False, default=0)
    coordinates: tuple = (0, 0)

    def __post_init__(self):
        if self.bus_name == 'NA':
            self.bus_name = f'Bus {self.bus_idx}'
# endregion


# region Shunt Classes
@dataclass(kw_only=True)
class Shunt_Element(ABC):  # TODO: If two of the same type of shunt element is connected to the same bus give them an internal ID (Bus 1 Load 1, Bus 1 Load 2 etc.)
    idx: int
    bus: Bus
    name: str = 'NA'


@dataclass
class Load(Shunt_Element):
    p_mw: float
    q_mvar: float

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Load {self.idx} '


@dataclass
class Generation(Shunt_Element):
    p_mw: float
    voltage_magnitude_kv: float

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Generation {self.idx} '


@dataclass
class Battery(Shunt_Element):
    p_mw: float
    p_charge_max_mw: float  # Max Charge Value (Positive)
    p_discharge_max_mw: float  # Max Discharge Value (Negative)
    soc: float
    capacity_mwh: float

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Battery {self.idx} '


@dataclass
class Shunt(Shunt_Element):
    p_mw: float
    q_mvar: float

    def __post_init__(self):
        if self.name == 'NA':
            self.name = f'Shunt {self.idx} '

# endregion


# region Branch Classes
@dataclass(kw_only=True)
class Branch(ABC):
    idx: int
    from_bus: Bus
    to_bus: Bus
    closed: bool = True  # True means switches are closed and the branch is active


@dataclass
class Line(Branch):
    r_ohm: float = 0
    x_ohm: float = 0
    b_total_mho: float = 0


@dataclass
class Transformer(Branch):  # from_bus is HV and to_bus is LV
    z_base: float
    r_pu: float = 0
    x_pu: float = 0
    gm_pu: float = 0
    bm_pu: float = 0
    tap: float = 1
    phase_shift: float = 0


@dataclass
class SOP(Branch):
    rated_s: float
    p_mw: float = 0
    q_mvar_from_to: float = 0
    q_mvar_to_from: float = 0
    efficiency: float = 100
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
