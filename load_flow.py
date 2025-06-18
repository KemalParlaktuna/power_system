from numpy import ones, zeros, longdouble, deg2rad, exp, conj, concatenate
from scipy.sparse import vstack, hstack, csr_matrix as sparse
from scipy.sparse.linalg import spsolve
from .ds_dx import calculate_dsbus_dx
import json
from .network_matrices import remove_line_from_y_bus, remove_transformer_from_y_bus
import networkx as nx
from itertools import combinations


def flat_start(net, load_flow_data):
    vm = ones(len(net.buses))
    va = zeros(len(net.buses))
    for generation in load_flow_data['generation'].values():
        bus = net.bus_map[generation['bus_idx']]
        vm[bus] = generation['vm_pu']
    for bus_idx, slack_bus in load_flow_data['slack_bus'].items():
        bus = net.bus_map[int(bus_idx)]
        vm[bus] = slack_bus['vm_pu']
        va[bus] = deg2rad(slack_bus['va_degree'])
    return vm, va


def get_bus_load_flow_types(net, load_flow_data) -> None:
    net.pq_buses = set()
    net.pv_buses = set()
    net.slack_buses = set()
    for bus, bus_type in load_flow_data['load_flow_type'].items():
        i = net.bus_map[int(bus)]
        if bus_type == 'PQ':
            net.pq_buses.add(i)
        elif bus_type == 'PV':
            net.pv_buses.add(i)
        else:
            net.slack_buses.add(i)


def check_multiple_slacks(net) -> None:
    G = nx.Graph()

    # Add lines as edges
    for line in net.lines.values():
        if line.closed:
            i = net.bus_map[line.from_bus.bus_idx]
            j = net.bus_map[line.to_bus.bus_idx]
            G.add_edge(i, j)

    # Add transformers as edges
    for transformer in net.transformers.values():
        if transformer.closed:
            i = net.bus_map[transformer.from_bus.bus_idx]
            j = net.bus_map[transformer.to_bus.bus_idx]
            G.add_edge(i, j)

    # Add all buses as nodes (redundant if all are already in edges, but safe)
    for bus in net.buses.values():
        i = net.bus_map[bus.bus_idx]
        G.add_node(i)

    # Check if any two slack buses are connected
    for u, v in combinations(net.slack_buses, 2):
        if nx.has_path(G, u, v):
            raise ValueError(f"Slack buses {u} and {v} are electrically connected.")


def set_scheduled_powers(net, load_flow_data):
    p_scheduled_pu = zeros((len(net.buses), 1), dtype=longdouble)
    q_scheduled_pu = zeros((len(net.buses), 1), dtype=longdouble)
    for generation in load_flow_data['generation'].values():
        bus = net.bus_map[generation['bus_idx']]
        p_scheduled_pu[bus] += net.mw_to_pu(generation['p_mw'])
    for load in load_flow_data['load'].values():
        bus = net.bus_map[load['bus_idx']]
        p_scheduled_pu[bus] -= net.mw_to_pu(load['p_mw'])
        q_scheduled_pu[bus] -= net.mw_to_pu(load['q_mvar'])
    for static_generation in load_flow_data['static_generation'].values():
        bus = net.bus_map[static_generation['bus_idx']]
        p_scheduled_pu[bus] += net.mw_to_pu(static_generation['p_mw'])
        q_scheduled_pu[bus] += net.mw_to_pu(static_generation['q_mvar'])

    return p_scheduled_pu, q_scheduled_pu


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


def load_flow_step(net, v, pvpq_list, pq_list, p_scheduled_pu, q_scheduled_pu):
    S = calculate_injection_powers(net, v)

    J  = calculate_jacobian_matrix(net, v, pvpq_list, pq_list)
    delta_p = S.real[pvpq_list] - p_scheduled_pu[pvpq_list]
    delta_q = S.imag[pq_list] - q_scheduled_pu[pq_list]

    F = concatenate([delta_p, delta_q])
    return -spsolve(J, F), F


def read_load_flow_data(load_flow_case):
    f = open(load_flow_case, 'r')
    load_flow_data = json.load(f)
    del f
    return load_flow_data


def run_load_flow_from_case_file(net, load_flow_case) -> None:
    """
    Wrapper function for load flow to run with case file
    """
    load_flow_data = read_load_flow_data(load_flow_case)
    p_scheduled_pu, q_scheduled_pu = set_scheduled_powers(net, load_flow_data)
    vm, va = flat_start(net, load_flow_data)
    get_bus_load_flow_types(net, load_flow_data)
    net.y_bus = net.full_y_bus.copy()
    update_y_bus(net, load_flow_data)
    check_multiple_slacks(net)
    load_flow(net, p_scheduled_pu, q_scheduled_pu, vm, va)


def update_y_bus(net, load_flow_data):
    for line_idx in load_flow_data['open_line'].values():
        net.lines[line_idx].closed = False
        remove_line_from_y_bus(net, net.lines[line_idx])

    for transformer_idx in load_flow_data['open_transformer'].values():
        net.transformers[transformer_idx].closed = False
        remove_transformer_from_y_bus(net, net.transformers[transformer_idx])


def load_flow(net,
              p_scheduled_pu,
              q_scheduled_pu,
              vm,
              va,
              max_iteration: int = 100,
              tolerance: float = 1e-8) -> None:

    pvpq_list = sorted(list(net.pq_buses) + list(net.pv_buses))
    pq_list = sorted(list(net.pq_buses))

    iteration = 0

    while iteration < max_iteration:
        iteration += 1
        v = vm*exp(1j*va)
        delta_x, F = load_flow_step(net, v, pvpq_list, pq_list, p_scheduled_pu, q_scheduled_pu)
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
