from scipy.sparse import lil_matrix
from numpy import cdouble, deg2rad, conjugate, exp


def create_y_bus(net):
    net.full_y_bus = lil_matrix((len(net.buses), len(net.buses)), dtype=cdouble)
    net.y_bus_from_to = lil_matrix((len(net.lines) + len(net.transformers), len(net.buses)), dtype=cdouble)
    net.y_bus_to_from = lil_matrix((len(net.lines) + len(net.transformers), len(net.buses)), dtype=cdouble)

    for shunt in net.shunts.values():
        i = shunt.bus.bus_idx
        net.full_y_bus[i, i] += (shunt.p_mw - 1j*shunt.q_mvar)/net.s_base_mva

    for line in net.lines.values():
        i = line.from_bus.bus_idx
        j = line.to_bus.bus_idx
        r_pu = net.ohm_to_pu(line.r_ohm, line.from_bus.voltage_level_kv)
        x_pu = net.ohm_to_pu(line.x_ohm, line.from_bus.voltage_level_kv)
        b_total_pu = net.mho_to_pu(line.b_total_mho, line.from_bus.voltage_level_kv)
        y_series = 1 / complex(r_pu, x_pu)
        net.full_y_bus[i, i] += y_series + 1j * b_total_pu / 2
        net.full_y_bus[i, j] -= y_series
        net.full_y_bus[j, i] -= y_series
        net.full_y_bus[j, j] += y_series + 1j * b_total_pu/2

        net.y_bus_from_to[line.idx, i] -= -y_series - 1j * b_total_pu/2
        net.y_bus_from_to[line.idx, j] += -y_series

        net.y_bus_to_from[line.idx, i] += -y_series
        net.y_bus_to_from[line.idx, j] -= -y_series - 1j * b_total_pu / 2
        net.from_buses.append(i)
        net.to_buses.append(j)

    for transformer in net.transformers.values():
        i = transformer.from_bus.bus_idx
        j = transformer.to_bus.bus_idx
        z_base = transformer.v_rated_low_kv**2/transformer.rated_s_mva
        r_pu = net.ohm_to_pu(transformer.r_pu*z_base, transformer.v_rated_low_kv)
        x_pu = net.ohm_to_pu(transformer.x_pu*z_base, transformer.v_rated_low_kv)

        gm_pu = net.mho_to_pu(transformer.gm_pu/z_base, transformer.to_bus.voltage_level_kv)
        bm_pu = net.mho_to_pu(transformer.bm_pu/z_base, transformer.to_bus.voltage_level_kv)
        y_shunt = complex(gm_pu, bm_pu)
        y_series = 1/complex(r_pu, x_pu)
        tap = transformer.tap
        phase_shift = transformer.phase_shift

        if tap == 0 or tap == None:
            tap = 1
        a = tap*exp(1j*deg2rad(phase_shift))

        net.full_y_bus[i, i] += y_series/(tap**2) + y_shunt/2
        net.full_y_bus[i, j] -= y_series/conjugate(a)
        net.full_y_bus[j, i] -= y_series/a
        net.full_y_bus[j, j] += y_series + y_shunt/2

        net.y_bus_from_to[transformer.idx, i] -= -y_series - y_shunt/2
        net.y_bus_from_to[transformer.idx, j] += -y_series

        net.y_bus_to_from[transformer.idx, i] += -y_series
        net.y_bus_to_from[transformer.idx, j] -= -y_series - y_shunt/2

        net.from_buses.append(i)
        net.to_buses.append(j)


def update_y_bus(net):
    pass
    # Submodule Update Test
