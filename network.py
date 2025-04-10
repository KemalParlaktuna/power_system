import numpy as np
from scipy.sparse.linalg import inv
import math


class Net:
    def __init__(self, s_base_mva=1, frequency_hz=50, network_name='Emtpy Network'):
        # System Parameters
        self._network_name = network_name
        self._s_base_mva = s_base_mva
        self._frequency_hz = frequency_hz

        # Bus Elements
        self._buses = {}

        # Shunt Elements
        self._generations = {}
        self._loads = {}
        self._shunts = {}
        self._batteries = {}

        # Branch Elements
        self._lines = {}
        self._transformers = {}
        self._soft_open_points = {}

        # Measurements
        self._bus_measurements = {}
        self._branch_measurements = {}

        # Network Matrices
        self._full_y_bus = None
        self._full_y_bus_shunt = None
        self._y_bus = None
        self._y_bus_from_to = None
        self._y_bus_to_from = None

        self._from_buses = []  # Maybe not needed to store as an attribute
        self._to_buses = []

        # Load Flow Types
        self._pq_buses = None  # Maybe not needed to store as an attribute
        self._pv_buses = None
        self._slack_buses = None

        # Load Flow Results
        self._vm = None  # Could store as bus attribute
        self._va = None

        # Load Flow Scheduled Powers
        self.p_scheduled_pu = None  # Maybe not needed to store as an attribute.
        self.q_scheduled_pu = None

        # State Estimation Results
        self._vm_estimated = None
        self._va_estimated = None

    def __repr__(self):
        return (f'System Properties\n'
                f'-------------------------\n'
                f'System Name: {self.network_name}\n'
                f'Base MVA: {self.s_base_mva} MVA\n'
                f'System Frequency: {self.frequency_hz} Hz\n'
                f'-------------------------\n'
                f'Bus Elements\n'
                f'-------------------------\n'
                f'- Number of Buses: {len(self.buses)}\n'
                f'- Number of Loads: {len(self.loads)}\n'
                f'- Number of Generations: {len(self.generations)}\n'
                f'- Number of Shunts: {len(self.shunts)}\n'
                f'-------------------------\n'
                f'Branch Elements\n'
                f'-------------------------\n'
                f'Number of Lines: {len(self.lines)}\n'
                f'Number of Transformers: {len(self.transformers)}\n'
                f'Number of SOPs: {len(self.soft_open_points)}\n')

    # region Base Conversions
    def mw_to_pu(self, mw):
        return mw/self.s_base_mva

    def ohm_to_pu(self, ohm, vn_kv):
        zBase = ((vn_kv * 1e3) ** 2) / (self.s_base_mva*1e6)
        return ohm/zBase

    def ampere_to_pu(self, A, vn_kv):
        iBase = self.s_base_mva*1e6/(math.sqrt(3)*vn_kv*12.66)
        return A/iBase

    def mho_to_pu(self, mho, vn_kv):
        yBase = (self.s_base_mva*1e6)/((vn_kv*1e3)**2)
        return mho/yBase

    def pu_to_mw(self, pu):
        return pu*self.s_base_mva

    def pu_to_ohm(self, pu, vn_kv):
        zBase = ((vn_kv * 1e3) ** 2) / (self.s_base_mva*1e6)
        return pu*zBase

    def pu_to_ampere(self, pu, vn_kv):
        iBase = self.s_base_mva * 1e6 / (math.sqrt(3) * vn_kv * 12.66)
        return pu*iBase

    def pu_to_mho(self, pu, vn_kv):
        yBase = (self.s_base_mva*1e6)/((vn_kv*1e3)**2)
        return pu*yBase
    # endregion

    # region Getters and Setters
    @property
    def buses(self):
        return self._buses

    @buses.setter
    def buses(self, value):
        self._buses = value

    @property
    def generations(self):
        return self._generations

    @generations.setter
    def generations(self, value):
        self._generations = value

    @property
    def loads(self):
        return self._loads

    @loads.setter
    def loads(self, value):
        self._loads = value

    @property
    def shunts(self):
        return self._shunts

    @shunts.setter
    def shunts(self, value):
        self._shunts = value

    @property
    def batteries(self):
        return self._batteries

    @batteries.setter
    def batteries(self, value):
        self._batteries = value

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        self._lines = value

    @property
    def transformers(self):
        return self._transformers

    @transformers.setter
    def transformers(self, value):
        self._transformers = value

    @property
    def soft_open_points(self):
        return self._soft_open_points

    @soft_open_points.setter
    def soft_open_points(self, value):
        self._soft_open_points = value

    @property
    def network_name(self):
        return self._network_name

    @network_name.setter
    def network_name(self, value):
        self._network_name = value
        
    @property
    def s_base_mva(self):
        return self._s_base_mva

    @s_base_mva.setter
    def s_base_mva(self, value):
        self._s_base_mva = value
        
    @property
    def frequency_hz(self):
        return self._frequency_hz

    @frequency_hz.setter
    def frequency_hz(self, value):
        self._frequency_hz = value

    @property
    def full_y_bus(self):
        return self._full_y_bus

    @full_y_bus.setter
    def full_y_bus(self, value):
        self._full_y_bus = value

    @property
    def y_bus_from_to(self):
        return self._y_bus_from_to

    @y_bus_from_to.setter
    def y_bus_from_to(self, value):
        self._y_bus_from_to = value

    @property
    def y_bus_to_from(self):
        return self._y_bus_to_from

    @y_bus_to_from.setter
    def y_bus_to_from(self, value):
        self._y_bus_to_from = value

    @property
    def full_y_bus_shunt(self):
        return self._full_y_bus_shunt

    @full_y_bus_shunt.setter
    def full_y_bus_shunt(self, value):
        self._full_y_bus_shunt = value

    @property
    def y_bus(self):
        return self._y_bus

    @y_bus.setter
    def y_bus(self, value):
        self._y_bus = value

    @property
    def from_buses(self):
        return self._from_buses

    @from_buses.setter
    def from_buses(self, value):
        self._from_buses = value

    @property
    def to_buses(self):
        return self._to_buses

    @to_buses.setter
    def to_buses(self, value):
        self._to_buses = value

    @property
    def pq_buses(self):
        return self._pq_buses

    @pq_buses.setter
    def pq_buses(self, value):
        self._pq_buses = value

    @property
    def pv_buses(self):
        return self._pv_buses

    @pv_buses.setter
    def pv_buses(self, value):
        self._pv_buses = value

    @property
    def slack_buses(self):
        return self._slack_buses

    @slack_buses.setter
    def slack_buses(self, value):
        self._slack_buses = value

    @property
    def vm(self):
        return self._vm

    @vm.setter
    def vm(self, value):
        self._vm = value

    @property
    def va(self):
        return self._va

    @va.setter
    def va(self, value):
        self._va = value

    @property
    def bus_measurements(self):
        return self._bus_measurements

    @bus_measurements.setter
    def bus_measurements(self, value):
        self._bus_measurements = value

    @property
    def branch_measurements(self):
        return self._branch_measurements

    @branch_measurements.setter
    def branch_measurements(self, value):
        self._branch_measurements = value

    @property
    def vm_estimated(self):
        return self._vm_estimated

    @vm_estimated.setter
    def vm_estimated(self, value):
        self._vm_estimated = value

    @property
    def va_estimated(self):
        return self._va_estimated

    @va_estimated.setter
    def va_estimated(self, value):
        self._va_estimated = value
    # endregion
