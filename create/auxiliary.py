from itertools import count

from .create_element import *
import json
from numpy import exp, conj, zeros, clongdouble, random as rnd
# from tkinter import filedialog as fd


def create_bus_from_dict(net, data) -> None:
    count = 0
    for bus in data['bus_data'].values():
        create_bus(net,
                   bus_idx=bus['bus_idx'],
                   voltage_level_kv=bus['voltage_level_kv'],
                   coordinates=bus['coordinates'])
        net.bus_map[bus['bus_idx']] = count
        count += 1


def create_load_from_dict(net, data) -> None:
    for load in data['load_data'].values():
        create_load(net,
                    load_idx=load['load_idx'],
                    bus_idx=load['bus_idx'],
                    s_rated_mva=load['s_rated_mva']
                    )


def create_generation_from_dict(net, data: dict) -> None:
    for generation in data['generator_data'].values():
        create_generator(net,
                         generation_idx=generation['generator_idx'],
                         bus_idx=generation['bus_idx'],
                         min_p_mw=generation['min_p_mw'],
                         max_p_mw=generation['max_p_mw'],
                         min_q_mvar=generation['min_q_mvar'],
                         max_q_mvar=generation['max_q_mvar']
                         )


def create_shunt_from_dict(net, data: dict) -> None:
    for shunt in data['shunt_data'].values():
        create_shunt(net,
                     shunt_idx=shunt['shunt_idx'],
                     bus_idx=shunt['bus_idx'],
                     p_mw=shunt['p_mw'],
                     q_mvar=shunt['q_mvar'])


def create_battery_from_dict(net, data: dict) -> None:
    for battery in data['battery_data'].values():
        create_battery(net,
                       battery_idx=battery['battery_idx'],
                       bus_idx=battery['bus_idx'],
                       p_charge_mw=battery['p_charge_mw'],
                       p_discharge_mw=battery['p_discharge_mw'],
                       soc=battery['soc'],
                       capacity_mwh=battery['capacity_mwh']
                       )


def create_line_from_dict(net, data: dict) -> None:
    count = 0
    for line in data['line_data'].values():
        create_line(net,
                    line_idx=line['line_idx'],
                    from_bus_idx=line['from_bus_idx'],
                    to_bus_idx=line['to_bus_idx'],
                    closed=line['closed'],
                    r_ohm=line['r_ohm'],
                    x_ohm=line['x_ohm'],
                    b_total_mho=line['b_total_mho']
                    )
        net.line_map[line['line_idx']] = count
        count += 1


def create_transformer_from_dict(net, data: dict) -> None:
    count = 0
    for transformer in data['transformer_data'].values():
        create_transformer(net,
                           transformer_idx=transformer['transformer_idx'],
                           from_bus_idx=transformer['from_bus_idx'],
                           to_bus_idx=transformer['to_bus_idx'],
                           v_rated_high_kv=transformer['v_rated_high_kv'],
                           v_rated_low_kv=transformer['v_rated_low_kv'],
                           rated_s_mva=transformer['rated_s_mva'],
                           r_pu=transformer['r_pu'],
                           x_pu=transformer['x_pu'],
                           gm_pu=transformer['gm_pu'],
                           bm_pu=transformer['bm_pu'],
                           tap=transformer['tap'],
                           phase_shift=transformer['phase_shift']
                           )
        net.transformer_map[transformer['transformer_idx']] = count
        count += 1


def create_sop_from_dict(net, data: dict) -> None:
    for sop in data['sop_data'].values():  # todo: maybe move this into a separate wrapper function !!
        create_sop(net,
                   sop_idx=sop['sop_idx'],
                   from_bus_idx=sop['from_bus_idx'],
                   to_bus_idx=sop['to_bus_idx'],
                   rated_s=sop['rated_s'],
                   closed=sop['closed'])


def create_network_from_json(net, filename) -> None:
    # filename: str = fd.askopenfilename()
    f = open(filename, 'r')
    data = json.load(f)
    del f
    net.network_name = data['system_data']['network_name']
    net.s_base_mva = data['system_data']['s_base_mva']
    net.frequency_hz = data['system_data']['frequency_hz']
    create_bus_from_dict(net, data)
    create_load_from_dict(net, data)
    create_generation_from_dict(net, data)
    create_shunt_from_dict(net, data)
    create_battery_from_dict(net, data)
    create_line_from_dict(net, data)
    create_transformer_from_dict(net, data)
    create_sop_from_dict(net, data)


def create_batteries_from_json(net, filename) -> None:
    f = open(filename, 'r')
    data = json.load(f)
    del f
    create_battery_from_dict(net, data)


def create_measurements_from_load_flow_solution(net) -> None:
    v = net.vm*exp(1j*net.va)
    S = v * conj(net.y_bus * v)

    bus_measurement_idx = 0
    for bus_idx in range(len(S)):
        create_bus_measurement(net,
                               bus_measurement_idx=bus_measurement_idx,
                               bus_idx=bus_idx,
                               std_dev=0.1,
                               value_pu=S[bus_idx].real,
                               measurement_type='p_injection')
        bus_measurement_idx += 1

        create_bus_measurement(net,
                               bus_measurement_idx=bus_measurement_idx,
                               bus_idx=bus_idx,
                               std_dev=0.1,
                               value_pu=S[bus_idx].imag,
                               measurement_type='q_injection')
        bus_measurement_idx += 1

        create_bus_measurement(net,
                               bus_measurement_idx=bus_measurement_idx,
                               bus_idx=bus_idx,
                               std_dev=0.1,
                               value_pu=net.vm[bus_idx],
                               measurement_type='v_magnitude')
        bus_measurement_idx += 1

    branch_measurement_idx = 0
    i_branch = net.y_bus_from_to * v
    S_flow = v[net.from_buses] * conj(i_branch)
    branch_idx = 0
    for line in net.lines.values():
        i = line.from_bus.bus_idx
        j = line.to_bus.bus_idx

        create_branch_measurement(net,
                                  branch_measurement_idx=branch_measurement_idx,
                                  from_bus_idx=i,
                                  to_bus_idx=j,
                                  std_dev=0.1,
                                  value_pu=S_flow[branch_idx].real,
                                  measurement_type='p_flow')
        branch_measurement_idx += 1

        create_branch_measurement(net,
                                  branch_measurement_idx=branch_measurement_idx,
                                  from_bus_idx=i,
                                  to_bus_idx=j,
                                  std_dev=0.1,
                                  value_pu=S_flow[branch_idx].imag,
                                  measurement_type='q_flow')
        branch_measurement_idx += 1
        branch_idx += 1

        # create_branch_measurement(net,
        #                           branch_measurement_idx=branch_measurement_idx,
        #                           from_bus_idx=i,
        #                           to_bus_idx=j,
        #                           std_dev=0.1,
        #                           value_pu=abs(i_branch),
        #                           measurement_type='i_magnitude')
        # branch_measurement_idx += 1


    for transformer in net.transformers.values():
        i = transformer.from_bus.bus_idx
        j = transformer.to_bus.bus_idx

        create_branch_measurement(net,
                                  branch_measurement_idx=branch_measurement_idx,
                                  from_bus_idx=i,
                                  to_bus_idx=j,
                                  std_dev=0.1,
                                  value_pu=S_flow[branch_idx].real,
                                  measurement_type='p_flow')
        branch_measurement_idx += 1

        create_branch_measurement(net,
                                  branch_measurement_idx=branch_measurement_idx,
                                  from_bus_idx=i,
                                  to_bus_idx=j,
                                  std_dev=0.1,
                                  value_pu=S_flow[branch_idx].imag,
                                  measurement_type='q_flow')
        branch_measurement_idx += 1

        branch_idx += 1

        # create_branch_measurement(net,
        #                           branch_measurement_idx=branch_measurement_idx,
        #                           from_bus_idx=i,
        #                           to_bus_idx=j,
        #                           std_dev=0.1,
        #                           value_pu=abs(i_branch),
        #                           measurement_type='i_magnitude')
        # branch_measurement_idx += 1
