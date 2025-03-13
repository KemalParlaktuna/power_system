from numpy import ones, zeros, longdouble, deg2rad, exp, conj, concatenate
from scipy.sparse import vstack, hstack, csr_matrix as sparse
from scipy.sparse.linalg import spsolve
from .ds_dx import calculate_dsbus_dx


def flat_start(net):
    vm = ones(len(net.buses))
    va = zeros(len(net.buses))
    for bus in net.buses.values():
        vm[bus.bus_idx] = bus.set_voltage_magnitude_kv/bus.voltage_level_kv
        va[bus.bus_idx] = deg2rad(bus.set_voltage_angle_degree)  # TODO: Subsystem angles should be set to the slack bus angle of the subsystem.
    return vm, va


def get_bus_load_flow_types(net):
    net.pq_buses = set()
    net.pv_buses = set()
    net.slack_buses = set()
    for bus in net.buses.values():
        if bus.load_flow_type == 'PQ':
            net.pq_buses.add(bus.bus_idx)
        elif bus.load_flow_type == 'PV':
            net.pv_buses.add(bus.bus_idx)
        else:
            net.slack_buses.add(bus.bus_idx)


def set_scheduled_powers(net):
    net.p_scheduled_pu = zeros((len(net.buses), 1), dtype=longdouble)
    net.q_scheduled_pu = zeros((len(net.buses), 1), dtype=longdouble)
    for generation in net.generations.values():
        net.p_scheduled_pu[generation.bus.bus_idx] += net.mw_to_pu(generation.p_mw)
    for load in net.loads.values():
        net.p_scheduled_pu[load.bus.bus_idx] -= net.mw_to_pu(load.p_mw)
        net.q_scheduled_pu[load.bus.bus_idx] -= net.mw_to_pu(load.q_mvar)


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
              max_iteration: int = 100,
              tolerance: float = 1e-8):

    vm, va = flat_start(net)
    get_bus_load_flow_types(net)

    pvpq_list = sorted(list(net.pq_buses) + list(net.pv_buses))
    pq_list = sorted(list(net.pq_buses))

    net.y_bus = net.full_y_bus.copy()  # TODO: This should be updated from a database of switch data
    set_scheduled_powers(net)

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




