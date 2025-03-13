from scipy.sparse import csr_matrix as sparse
from numpy import conj, arange


def calculate_dsbus_dx(y_bus: sparse, v: list):
    i_bus = y_bus * v
    n = range(len(v))
    diag_v = sparse((v, (n, n)))
    diag_i_bus = sparse((i_bus, (n, n)))
    diag_v_norm = sparse((v / abs(v), (n, n)))
    dsbus_dvm = diag_v * conj(y_bus * diag_v_norm) + conj(diag_i_bus) * diag_v_norm
    dsbus_dva = 1j * diag_v * conj(diag_i_bus - y_bus * diag_v)
    return dsbus_dvm, dsbus_dva


def calculate_dsbranch_dx(y_bus_from_to: sparse, from_buses, v: list):
    i_branch = y_bus_from_to * v  # Current
    n_branch, n_bus = y_bus_from_to.shape  # number of branches, number of buses
    v_norm  = v / abs(v)
    m = arange(n_branch)
    n = arange(n_bus)

    diag_v_from = sparse((v[from_buses], (m, m)))
    diag_i_branch = sparse((i_branch, (m, m)))
    diag_v = sparse((v, (n, n)))
    diag_v_norm = sparse((v_norm, (n, n)))

    dsbranch_dva = 1j * (conj(diag_i_branch) *
                    sparse((v[from_buses], (m, from_buses)), (n_branch, n_bus)) - diag_v_from * conj(y_bus_from_to * diag_v))

    dsbranch_dvm = diag_v_from * conj(y_bus_from_to * diag_v_norm) + conj(diag_i_branch) * \
              sparse((v_norm[from_buses], (m, from_buses)), (n_branch, n_bus))

    return dsbranch_dvm, dsbranch_dva
