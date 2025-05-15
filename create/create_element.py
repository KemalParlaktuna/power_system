from .elements import *


def create_bus(net,
               bus_idx: int,
               voltage_level_kv: float,
               bus_name: str = 'NA',
               coordinates: tuple[float, float] = (0, 0)) -> None:

    # Buses are nodes that all other elements connect to.
    net.buses[bus_idx] = Bus(bus_idx=bus_idx,
                             voltage_level_kv=voltage_level_kv,
                             bus_name=bus_name,
                             coordinates=coordinates
                             )


def create_load(net,
                load_idx: int,
                bus_idx: int,
                s_rated_mva: float,
                load_name: str = 'NA') -> None:

    net.loads[load_idx] = Load(idx=load_idx,
                               bus=net.buses[bus_idx],
                               s_rated_mva=s_rated_mva,
                               name=load_name)


def create_generator(net,
                     generation_idx: int,
                     bus_idx: int,
                     min_p_mw: float,
                     max_p_mw: float,
                     min_q_mvar: float,
                     max_q_mvar: float,
                     generator_name: str = 'NA') -> None:

    net.generators[generation_idx] = Generator(idx=generation_idx,
                                               bus=net.buses[bus_idx],
                                               min_p_mw=min_p_mw,
                                               max_p_mw=max_p_mw,
                                               min_q_mvar=min_q_mvar,
                                               max_q_mvar=max_q_mvar,
                                               name=generator_name)


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
                   p_charge_mw: float,
                   p_discharge_mw: float,
                   soc: float,
                   capacity_mwh: float,
                   battery_name: str = 'NA') -> None:

    net.batteries[battery_idx] = Battery(idx=battery_idx,
                                         bus=net.buses[bus_idx],
                                         p_charge_mw=p_charge_mw,
                                         p_discharge_mw=p_discharge_mw,
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
                       v_rated_high_kv: float,
                       v_rated_low_kv: float,
                       rated_s_mva: float,
                       r_pu: float,
                       x_pu: float,
                       gm_pu: float = 0,
                       bm_pu: float = 0,
                       closed: bool = True) -> None:

    net.transformers[transformer_idx] = Transformer(idx=transformer_idx,
                                                    from_bus=net.buses[from_bus_idx],
                                                    to_bus=net.buses[to_bus_idx],
                                                    v_rated_high_kv=v_rated_high_kv,
                                                    v_rated_low_kv=v_rated_low_kv,
                                                    rated_s_mva=rated_s_mva,
                                                    closed=closed,
                                                    r_pu=r_pu,
                                                    x_pu=x_pu,
                                                    gm_pu=gm_pu,
                                                    bm_pu=bm_pu
                                                    )


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
