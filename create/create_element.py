from .elements import *


def create_bus(net,
               bus_idx: int,
               voltage_level_kv: float,
               load_flow_type: str,
               set_voltage_magnitude_kv: float,
               set_voltage_angle_degree: float,
               bus_name: str = 'NA',
               coordinates: tuple[float, float] = (0, 0)) -> None:

    # Buses are nodes that all other elements connect to.
    net.buses[bus_idx] = Bus(bus_idx=bus_idx,
                             voltage_level_kv=voltage_level_kv,
                             load_flow_type=load_flow_type,
                             bus_name=bus_name,
                             coordinates=coordinates,
                             set_voltage_magnitude_kv=set_voltage_magnitude_kv,
                             set_voltage_angle_degree=set_voltage_angle_degree)


def create_load(net,
                load_idx: int,
                bus_idx: int,
                p_mw: float,
                q_mvar: float,
                load_name: str = 'NA') -> None:

    net.loads[load_idx] = Load(idx=load_idx,
                               bus=net.buses[bus_idx],
                               p_mw=p_mw,
                               q_mvar=q_mvar,
                               name=load_name)


def create_generation(net,
                      generation_idx: int,
                      bus_idx: int,
                      p_mw: float,
                      voltage_magnitude_kv: float,
                      generation_name: str = 'NA') -> None:

    net.generations[generation_idx] = Generation(idx=generation_idx,
                                                 bus=net.buses[bus_idx],
                                                 p_mw=p_mw,
                                                 voltage_magnitude_kv=voltage_magnitude_kv,
                                                 name=generation_name)


def create_shunt(net,
                 shunt_idx: int,
                 bus_idx: int,
                 p_mw: float,
                 q_mvar: float,
                 shunt_name: str = 'NA') -> None:

    net.shunts[shunt_idx] = Shunt(idx=shunt_idx,
                                  bus=net.buses[bus_idx],
                                  p_mw=p_mw,
                                  q_mvar=q_mvar,
                                  name=shunt_name)


def create_battery(net,
                   battery_idx: int,
                   bus_idx: int,
                   p_mw: float,
                   p_charge_max_mw: float,
                   p_discharge_max_mw: float,
                   soc: float,
                   capacity_mwh: float,
                   battery_name: str = 'NA') -> None:

    net.batteries[battery_idx] = Battery(idx=battery_idx,
                                         bus=net.buses[bus_idx],
                                         p_mw=p_mw,
                                         p_charge_max_mw=p_charge_max_mw,
                                         p_discharge_max_mw=p_discharge_max_mw,
                                         soc=soc,
                                         capacity_mwh=capacity_mwh,
                                         name=battery_name)


def create_line(net,
                line_idx: int,
                from_bus_idx: int,
                to_bus_idx: int,
                r_ohm: float,
                x_ohm: float,
                b_total_mho: float,
                closed: bool = True) -> None:

    net.lines[line_idx] = Line(idx=line_idx,
                               from_bus=net.buses[from_bus_idx],
                               to_bus=net.buses[to_bus_idx],
                               closed=closed,
                               r_ohm=r_ohm,
                               x_ohm=x_ohm,
                               b_total_mho=b_total_mho)


def create_transformer(net,
                       transformer_idx: int,
                       from_bus_idx: int,
                       to_bus_idx: int,
                       r_pu: float,
                       x_pu: float,
                       z_base: float,
                       tap: float = 1,
                       gm_pu: float = 0,
                       bm_pu: float = 0,
                       phase_shift: float = 0,
                       closed: bool = True) -> None:

    net.transformers[transformer_idx] = Transformer(idx=transformer_idx,
                                                    from_bus=net.buses[from_bus_idx],
                                                    to_bus=net.buses[to_bus_idx],
                                                    closed=closed,
                                                    r_pu=r_pu,
                                                    x_pu=x_pu,
                                                    z_base=z_base,
                                                    gm_pu=gm_pu,
                                                    bm_pu=bm_pu,
                                                    tap=tap,
                                                    phase_shift=phase_shift)


def create_sop(net,
               sop_idx: int,
               from_bus_idx: int,
               to_bus_idx: int,
               rated_s: float,
               closed: bool = True) -> None:

    net.soft_open_points[sop_idx] = SOP(idx=sop_idx,
                                        from_bus=net.buses[from_bus_idx],
                                        to_bus=net.buses[to_bus_idx],
                                        closed=closed,
                                        rated_s=rated_s)


def create_bus_measurement(net,
                           bus_measurement_idx: int,
                           bus_idx: int,
                           std_dev: float,
                           value_pu: float,
                           measurement_type: str) -> None:

    net.bus_measurements[bus_measurement_idx] = Bus_Measurement(measurement_idx=bus_measurement_idx,
                                                                bus=net.buses[bus_idx],
                                                                std_dev=std_dev,
                                                                value_pu=value_pu,
                                                                measurement_type=measurement_type)


def create_branch_measurement(net,
                              branch_measurement_idx: int,
                              from_bus_idx: int,
                              to_bus_idx: int,
                              std_dev: float,
                              value_pu: float,
                              measurement_type: str) -> None:

    net.branch_measurements[branch_measurement_idx] = Branch_Measurement(measurement_idx=branch_measurement_idx,
                                                                         from_bus=net.buses[from_bus_idx],
                                                                         to_bus=net.buses[to_bus_idx],
                                                                         std_dev=std_dev,
                                                                         value_pu=value_pu,
                                                                         measurement_type=measurement_type)
