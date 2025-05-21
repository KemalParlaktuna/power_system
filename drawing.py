import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"


def draw_network(net, color=False):
    edge_trace, edge_labels_trace = create_edge_trace(net)
    if color == True:
        node_trace = create_node_trace_colored(net)
    else:
        node_trace = create_node_trace(net)

    network_name = net.network_name
    s_base_mva = net.s_base_mva
    frequency_hz = net.frequency_hz

    fig = create_figure(edge_labels_trace, node_trace, edge_trace, network_name, s_base_mva, frequency_hz)

    fig.show()


def draw_network_based_on_voltage_levels(net):
    edge_trace, edge_labels_trace = create_edge_trace(net)

    node_trace = create_node_trace(net, 'voltage_level_kv')

    network_name = net.network_name + ' Voltage Level'
    s_base_mva = net.s_base_mva
    frequency_hz = net.frequency_hz

    fig = create_figure(edge_labels_trace, node_trace, edge_trace, network_name, s_base_mva, frequency_hz)

    fig.show()


def create_figure(edge_labels_trace, node_trace, edge_trace, network_name, s_base_mva, frequency_hz):
    fig = go.Figure(data=[edge_labels_trace, edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(
                            text=f'{network_name} Graph <br>'
                                 f'Power Base: {s_base_mva} MVA <br>'
                                 f'Frequency: {frequency_hz} Hz <br>',
                            font=dict(
                                size=16
                            )
                        ),
                        showlegend=False,
                        hovermode='closest',
                        plot_bgcolor='white',
                        margin=dict(b=20, l=5, r=5, t=100),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    return fig


def create_edge_trace(net):
    edge_labels = []
    edge_color = []
    line_x, line_y, line_label_x, line_label_y = create_edge_info(net.lines)
    for line in net.lines.values():
        edge_labels.append(f'Line {line.idx}<br>'                           
                           f'From Bus Name: {line.from_bus.bus_name}<br>'
                           f'To Bus Name: {line.to_bus.bus_name}<br>'
                           f'R:{line.r_ohm} ohm<br>'
                           f'X:{line.x_ohm} ohm<br>'
                           f'B:{line.b_total_mho} mho<br>')

    transformer_x, transformer_y, transformer_label_x, transformer_label_y = create_edge_info(net.transformers)
    for transformer in net.transformers.values():
        edge_labels.append(f'Transfomer {transformer.idx}<br>'
                           f'From Bus Name: {transformer.from_bus.bus_name}<br>'
                           f'From Bus Voltage Level: {transformer.from_bus.voltage_level_kv} kV<br>'
                           f'To Bus Name: {transformer.to_bus.bus_name}<br>'
                           f'To Bus Voltage Level: {transformer.to_bus.voltage_level_kv} kV<br>'
                           f'R: {transformer.r_pu} pu<br>'
                           f'X: {transformer.x_pu} pu<br>'
                           f'Tap: {transformer.tap}<br>'
                           f'Phase Shift: {transformer.phase_shift} degrees<br>')

    sop_x, sop_y, sop_label_x, sop_label_y = create_edge_info(net.soft_open_points)
    for sop in net.soft_open_points.values():
        edge_labels.append(f'SOP {sop.idx}<br>'
                           f'From Bus Name: {sop.from_bus.bus_name}<br>'
                           f'To Bus Name: {sop.to_bus.bus_name}<br>'
                           f'P: {sop.p_mw} MW<br>'
                           f'Q_from_to: {sop.q_mvar_from_to} MVAr<br>'
                           f'Q_to_from: {sop.q_mvar_to_from} MVAr<br>'
                           f'Tap: {sop.efficiency}<br>'
                           f'Phase Shift: {sop.phase_shift} degrees<br>')


    edge_trace = go.Scatter(x=line_x + transformer_x + sop_x,
                            y=line_y + transformer_y + sop_y,
                            line=dict(width=1, color='black'),
                            hoverinfo='none',
                            mode='lines',
                            )

    edge_labels_trace = go.Scatter(x=line_label_x + transformer_label_x + sop_label_x,
                                   y=line_label_y + transformer_label_y + sop_label_y,
                                   mode='none',
                                   hovertext=edge_labels,
                                   hoverinfo='text',
                                   textposition='top center')

    return edge_trace, edge_labels_trace


def create_edge_info(edge_dict):
    edge_x = []
    edge_y = []
    label_x = []
    label_y = []
    for edge in edge_dict.values():
        x0, y0 = edge.from_bus.coordinates
        x1, y1 = edge.to_bus.coordinates
        label_x.append((x0 + x1) / 2)
        label_y.append((y0 + y1) / 2)
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    return edge_x, edge_y, label_x, label_y


def create_node_trace(net, color_rule=None):
    node_x = []
    node_y = []
    node_labels = []
    node_color = []
    for bus in net.buses.values():
        x, y = bus.coordinates
        node_x.append(x)
        node_y.append(y)
        node_labels.append(f'Bus ID: {bus.bus_idx} <br>'
                           f'{bus.bus_name} <br>'
                           f'Voltage Level: {bus.voltage_level_kv} kV <br>')
        if color_rule == 'voltage_level_kv':
            node_color.append(bus.voltage_level_kv)


    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hovertext=node_labels,
        hoverinfo='text',
        marker=dict(
            showscale=False,
            colorscale='Jet',
            reversescale=True,
            color=node_color,
            size=12,
            line_width=2))

    return node_trace


def create_node_trace_colored(net):
    node_x = []
    node_y = []
    node_color = []
    node_symbol = ['circle']*len(net.buses)
    node_text = []

    for bus in net.buses.values():
        # Position
        x, y = bus.coordinates
        node_x.append(x)
        node_y.append(y)

        # Hover text
        text = f"Bus: {bus.bus_name}<br>Voltage: {bus.voltage_level_kv} kV"
        node_text.append(text)

        # Color by energized status
        if bus.energized:
            node_color.append('green')
        else:
            node_color.append('lightgray')

    for generator in net.generators.values():
        node_symbol[generator.bus.bus_idx] = 'star'

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(
            size=12,
            color=node_color,
            symbol=node_symbol,
            line=dict(width=1, color='black')
        ),
        hovertext=node_text,
        hoverinfo='text'
    )

    return node_trace

