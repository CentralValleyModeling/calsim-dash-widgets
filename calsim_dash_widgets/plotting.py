import dash
import pandas as pd
import plotly.express as px


def create_sparkline(df: pd.DataFrame, **layout_kwargs) -> dash.dcc.Graph:
    fig = px.line(x=df.index, y=df.iloc[:, 0])
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