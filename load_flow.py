from numpy import ones, zeros, longdouble, deg2rad, exp, conj, concatenate
from scipy.sparse import vstack, hstack, csr_matrix as sparse
from scipy.sparse.linalg import spsolve
from .ds_dx import calculate_dsbus_dx
import json


def flat_start(net, load_flow_data):
    vm = ones(len(net.buses))
    va = zeros(len(net.buses))
    for generation in load_flow_data['generation'].values():
        vm[generation['bus_idx']] = generation['vm_pu']
    for bus_idx, slack_bus in load_flow_data['slack_bus'].items():
        vm[int(bus_idx)] = slack_bus['vm_pu']
        va[int(bus_idx)] = deg2rad(slack_bus['va_degree'])
    return vm, va


def get_bus_load_flow_types(load_flow_data):
    pq_buses = set()
    pv_buses = set()
    slack_buses = set()
    for bus, bus_type in load_flow_data['load_flow_type'].items():
        if bus_type == 'PQ':
            pq_buses.add(int(bus))
        elif bus_type == 'PV':
            pv_buses.add(int(bus))
        else:
            slack_buses.add(int(bus))
    return pq_buses, pv_buses, slack_buses


def set_scheduled_powers(net, load_flow_data):
    net.p_scheduled_pu = zeros((len(net.buses), 1), dtype=longdouble)
    net.q_scheduled_pu = zeros((len(net.buses), 1), dtype=longdouble)
    for generation in load_flow_data['generation'].values():
        net.p_scheduled_pu[generation['bus_idx']] += net.mw_to_pu(generation['p_mw'])
    for load in load_flow_data['load'].values():
        net.p_scheduled_pu[load['bus_idx']] -= net.mw_to_pu(load['p_mw'])
        net.q_scheduled_pu[load['bus_idx']] -= net.mw_to_pu(load['q_mvar'])
    for static_generation in load_flow_data['static_generation'].values():
        net.p_scheduled_pu[static_generation['bus_idx']] += net.mw_to_pu(static_generation['p_mw'])
        net.q_scheduled_pu[static_generation['bus_idx']] += net.mw_to_pu(static_generation['q_mvar'])


def calculate_injection_powers(net, v):
    S = v * conj(net.y_bus * v)
    return S.reshape((len(net.buses), 1))


def calculate_jacobian_matrix(net, v, pvpq_list, pq_list):
    ds_dvm, ds_dva = calculate_dsbus_dx(sparse(net.y_bus), v)

    j11 = ds_dva[pvpq_list, :][:, pvpq_list].real
    j12 = ds_dvm[pvpq_list, :][:, pq_list].real
    J21 = ds_dva[pq_list, :][:, pvpq_list].imag
    J22 = ds_dvm[pq_list, :][:, pq_list].imag

    return vstack([hstack([j11, j12]), hstack([J21, J22])])


def load_flow_step(net, v, pvpq_list, pq_list):
    S = calculate_injection_powers(net, v)

    J  = calculate_jacobian_matrix(net, v, pvpq_list, pq_list)
    delta_p = S.real[pvpq_list] - net.p_scheduled_pu[pvpq_list]
    delta_q = S.imag[pq_list] - net.q_scheduled_pu[pq_list]

    F = concatenate([delta_p, delta_q])
    return -spsolve(J, F), F


def load_flow(net,
              load_flow_case,
              max_iteration: int = 100,
              tolerance: float = 1e-8):

    f = open(load_flow_case, 'r')
    load_flow_data = json.load(f)
    del f
    net.pq_buses, net.pv_buses, net.slack_buses = get_bus_load_flow_types(load_flow_data)
    vm, va = flat_start(net, load_flow_data)
    pvpq_list = sorted(list(net.pq_buses) + list(net.pv_buses))
    pq_list = sorted(list(net.pq_buses))

    net.y_bus = net.full_y_bus.copy()  # TODO: This should be updated from a database of switch data
    set_scheduled_powers(net, load_flow_data)

    iteration = 0

    while iteration < max_iteration:
        iteration += 1
        v = vm*exp(1j*va)
        delta_x, F = load_flow_step(net, v, pvpq_list, pq_list)
        delta_va = delta_x[0:len(pvpq_list)]
        delta_vm = delta_x[len(pvpq_list):len(pvpq_list) + len(pq_list)]

        va[pvpq_list] += delta_va
        vm[pq_list] += delta_vm

        eps = max(abs(F))
        if eps < tolerance:
            print(f'Newton-Raphson Load FLow Converged at Iteration {iteration}')
            net.vm = vm
            net.va = va
            break

        if iteration == max_iteration:
            print(f'Did not converge!')




