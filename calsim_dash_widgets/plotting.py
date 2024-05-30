import dash
import numpy as np
import pandas as pd
import plotly.express as px


def sparkline(s: pd.Series, **layout_kwargs) -> dash.dcc.Graph:
    fig = px.line(x=s.index, y=s.values)
    # hide and lock down axes
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
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
