"""
Plotly chart builders for the Charts page, styled to match the AOS
Command Center theme: flat colors from the real brand palette, no
gradients, no bright/neon colors.
"""

import plotly.graph_objects as go

ACCENT = "#1a2c4d"
ACCENT_MUTED = "#3d5480"
SIGNAL = "#7c6231"
MUTED = "#5c6068"
BORDER = "#d3d5da"
PAPER = "#faf9f6"

PALETTE = [ACCENT, ACCENT_MUTED, SIGNAL, "#7a8699", "#a3ada0", "#54606e"]


def _base_layout(fig: go.Figure, title: str):
    fig.update_layout(
        title=title,
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(color="#14161b", family="Inter, system-ui, sans-serif"),
        title_font=dict(color=ACCENT, size=16),
        margin=dict(l=40, r=20, t=50, b=40),
        showlegend=True,
    )
    fig.update_xaxes(showgrid=True, gridcolor=BORDER, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, zeroline=False)
    return fig


def bar_chart(labels: list, values: list, title: str, y_title: str = ""):
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=ACCENT)])
    fig.update_yaxes(title=y_title)
    return _base_layout(fig, title)


def pie_chart(labels: list, values: list, title: str):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=PALETTE), hole=0.35)])
    return _base_layout(fig, title)


def line_chart(x_values: list, y_values: list, title: str, y_title: str = ""):
    fig = go.Figure(data=[go.Scatter(x=x_values, y=y_values, mode="lines+markers", line=dict(color=ACCENT, width=2))])
    fig.update_yaxes(title=y_title)
    return _base_layout(fig, title)


def network_chart(edges: list, title: str):
    """A simple, dependency-free bipartite network view (no graphviz/
    networkx — just two columns of Plotly scatter markers plus a line
    trace per edge) — companies on the left, people on the right, one
    edge per person -> their company. `edges` is a list of
    {"person", "company"} dicts. Not a claim of a full graph-layout
    tool, just an honest, readable relationship map."""
    companies = sorted({e["company"] for e in edges if e.get("company")})
    people = sorted({e["person"] for e in edges if e.get("person")})

    company_y = {name: i for i, name in enumerate(companies)}
    person_y = {name: i for i, name in enumerate(people)}
    company_scale = (len(people) - 1) / max(len(companies) - 1, 1) if companies else 1

    fig = go.Figure()
    for e in edges:
        if not e.get("company") or not e.get("person"):
            continue
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[company_y[e["company"]] * company_scale, person_y[e["person"]]],
            mode="lines", line=dict(color=BORDER, width=1), showlegend=False, hoverinfo="none",
        ))
    fig.add_trace(go.Scatter(
        x=[0] * len(companies), y=[company_y[c] * company_scale for c in companies],
        mode="markers+text", text=companies, textposition="middle left",
        marker=dict(size=14, color=ACCENT), name="Company",
    ))
    fig.add_trace(go.Scatter(
        x=[1] * len(people), y=[person_y[p] for p in people],
        mode="markers+text", text=people, textposition="middle right",
        marker=dict(size=10, color=SIGNAL), name="Person",
    ))
    fig.update_xaxes(visible=False, range=[-0.5, 1.5])
    fig.update_yaxes(visible=False)
    fig.update_layout(showlegend=True)
    return _base_layout(fig, title)


def empty_chart(message: str, title: str):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(color=MUTED, size=14))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _base_layout(fig, title)
