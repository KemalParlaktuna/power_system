from numpy import ones, exp, conj, zeros, eye, c_, r_, array, diagflat, concatenate
from scipy.sparse import csr_matrix, vstack, hstack, eye as sparse_eye
from scipy.sparse.linalg import spsolve
from scipy.optimize import linprog as lp
from .ds_dx import calculate_dsbus_dx, calculate_dsbranch_dx


def create_measurement_vector(net):
    v_magnitude = []
    p_injection = []
    q_injection = []
    p_flow = []
    q_flow = []
    r_cov = []
    for idx, measurement in net.bus_measurements.items():
        if measurement.measurement_type == 'v_magnitude':
            v_magnitude.append(measurement.value_pu)
            r_cov.append(measurement.std_dev**2)
        elif measurement.measurement_type == 'p_injection':
            p_injection.append(measurement.value_pu)
            r_cov.append(measurement.std_dev**2)
        else:
            q_injection.append(measurement.value_pu)
            r_cov.append(measurement.std_dev**2)

    for idx, measurement in net.branch_measurements.items():
        if measurement.measurement_type == 'p_flow':
            p_flow.append(measurement.value_pu)
            r_cov.append(measurement.std_dev**2)
        elif measurement.measurement_type == 'q_flow':
            q_flow.append(measurement.value_pu)
            r_cov.append(measurement.std_dev**2)

    return array(v_magnitude + p_injection + q_injection + p_flow + q_flow), csr_matrix(diagflat(1 / array(r_cov) ** 2))


def create_jacobian_matrix(net, v):
    dsbus_dvm, dsbus_dva = calculate_dsbus_dx(net.y_bus, v)
    dsbranch_dvm, dsbranch_dva = calculate_dsbranch_dx(net.y_bus_from_to,
                                                           net.from_buses,
                                                           v)
    v_jac_va, v_jac_vm = zeros((v.shape[0], v.shape[0])), eye(v.shape[0], v.shape[0])
    s_jac_va = vstack((dsbus_dva.real,
                       dsbus_dva.imag,
                       dsbranch_dva.real,
                       dsbranch_dva.imag))

    s_jac_vm = vstack((dsbus_dvm.real,
                      dsbus_dvm.imag,
                      dsbranch_dvm.real,
                      dsbranch_dvm.imag))

    s_jac = hstack((s_jac_va, s_jac_vm)).toarray()

    vm_jac = c_[v_jac_va, v_jac_vm]
    H = r_[vm_jac, s_jac]

    return csr_matrix(H[:, 1:])  # todo: this should read slack buses. for now assume it is bus 0.


def create_hx(net, v):
    s_flow = v[net.from_buses] * conj(net.y_bus_from_to * v)
    s_bus = v * conj(net.y_bus * v)
    hx = r_[abs(v),
            s_bus.real,
            s_bus.imag,
            s_flow.real,
            s_flow.imag]

    return hx


def flat_start(net):
    vm = ones(len(net.buses))
    va = zeros(len(net.buses))
    return vm, va


def estimate(net,
             max_iteration=100,
             tolerance=1e-8,
             algorithm='WLS'):

    vm, va = flat_start(net)

    iteration = 0
    while iteration < max_iteration:
        iteration += 1
        v = vm * exp(1j * va)
        z, r_inv = create_measurement_vector(net)
        H = create_jacobian_matrix(net, v)
        hx = create_hx(net, v)
        r = z - hx
        if algorithm =='WLS':
            G_m = H.T * (r_inv * H)

            dx = spsolve(G_m, H.T * (r_inv * r))

        elif algorithm == 'LAV':
            m, n = H.shape

            C = concatenate((zeros((1, n)), zeros((1, n)), ones((1, m)), ones((1, m))), axis=1)
            A = hstack((H, -H, sparse_eye(m, format='csc'), -sparse_eye(m, format='csc')))

            res = lp(c=C, A_eq=A, b_eq=r, method="highs-ds")
            sol = res.x

            delXu = sol[0:n]
            delXv = sol[n:n + n]

            dx = delXu - delXv
        else:
            raise NotImplementedError

        va[1:] += dx[:len(net.buses)-1]  # todo: this should read slack buses. for now assume it is bus 0.
        vm += dx[len(net.buses)-1:]  # todo: this should read slack buses. for now assume it is bus 0.

        eps = max(abs(dx))
        if eps < tolerance:
            print(f'{algorithm} State Estimation Converged at Iteration {iteration}')
            net.vm_estimated = vm
            break
        if iteration == max_iteration:
            net.va_estimated = va
            print(f'{algorithm} State Estimation Did Not Converge')

