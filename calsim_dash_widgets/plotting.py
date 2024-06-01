import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def sparkline(s: pd.Series, **layout_kwargs) -> dash.dcc.Graph:
    fig = px.line(x=s.index, y=s.values)
    # hide and lock down axes
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(
        visible=True,
        fixedrange=True,
        showticklabels=False,
        rangemode="tozero",
    )
    # remove facet/subplot labels
    fig.update_layout(annotations=[], overwrite=True)
    # strip down the rest of the plot
    layout_kwargs = (
        dict(
            showlegend=False,
            plot_bgcolor="white",
            margin=dict(t=0, l=0, b=0, r=0),
            autosize=False,
            width=300,
            height=33.6 + 8,  # Manually determined to match the H3 size in bootstrap
        )
        | layout_kwargs
    )
    fig.update_layout(**layout_kwargs)

    return dash.dcc.Graph(
        figure=fig,
        config=dict(displayModeBar=False),
        style=dict(overflow="hidden"),
    )


def comparative_sparkline(
    series: dict[str, pd.Series],
    **layout_kwargs,
) -> dash.dcc.Graph:
    fig = go.Figure()
    for name, s in series.items():
        fig.add_trace(go.Scatter(x=s.index, y=s, mode="lines", name=name))
    # hide and lock down axes
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(
        visible=True,
        fixedrange=True,
        showticklabels=False,
        rangemode="tozero",
    )
    # remove facet/subplot labels
    fig.update_layout(annotations=[], overwrite=True)
    # strip down the rest of the plot
    layout_kwargs = (
        dict(
            showlegend=True,
            plot_bgcolor="white",
            margin=dict(t=0, l=0, b=0, r=0),
            autosize=False,
            width=300,
            height=150,
            legend=dict(
                yanchor="top",
                y=0,
                xanchor="left",
                x=0,
            ),
        )
        | layout_kwargs
    )
    fig.update_layout(**layout_kwargs)

    return dash.dcc.Graph(
        figure=fig,
        config=dict(displayModeBar=False),
        # style=dict(overflow="hidden"),
    )


def exceedance(s: pd.Series, **layout_kwargs) -> dash.dcc.Graph:
    s = s.sort_values(ascending=False)
    e = np.arange(1.0, s.size + 1) / s.size
    fig = px.line(x=s, y=e)
    layout_kwargs = (
        dict(
            showlegend=False,
            autosize=False,
            width=750,
            height=400,
            xaxis_title="Value",
            yaxis_title="Exceedance Probability",
            font=dict(size=11),
            yaxis=dict(
                tickformat=".0%",
                autorange="reversed",
            ),
        )
        | layout_kwargs
    )
    fig.update_layout(**layout_kwargs)
    return dash.dcc.Graph(figure=fig)


def comparative_exceedance(
    series: dict[str, pd.Series],
    **layout_kwargs,
) -> dash.dcc.Graph:
    series = {k: s.sort_values(ascending=False) for k, s in series.items()}
    exceed = {k: np.arange(1.0, s.size + 1) / s.size for k, s in series.items()}
    # plot lines
    fig = go.Figure()
    for name, s in series.items():
        fig.add_trace(go.Scatter(x=s, y=exceed[name], mode="lines", name=name))
    layout_kwargs = (
        dict(
            showlegend=True,
            autosize=False,
            width=750,
            height=400,
            xaxis_title="Value",
            yaxis_title="Exceedance Probability",
            font=dict(size=11),
            yaxis=dict(
                tickformat=".0%",
                autorange="reversed",
            ),
            legend=dict(
                yanchor="top",
                y=-0.15,
                xanchor="left",
                x=0,
            ),
        )
        | layout_kwargs
    )
    fig.update_layout(**layout_kwargs)
    return dash.dcc.Graph(figure=fig)


def timeseries(s: pd.Series, **layout_kwargs) -> dash.dcc.Graph:
    fig = px.line(x=s.index, y=s.values)
    layout_kwargs = (
        dict(
            showlegend=False,
            autosize=False,
            width=750,
            height=400,
            xaxis_title="Date",
            yaxis_title="Value",
            font=dict(size=11),
        )
        | layout_kwargs
    )
    fig.update_layout(**layout_kwargs)
    return dash.dcc.Graph(figure=fig)
