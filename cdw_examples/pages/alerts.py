import dash
import dash_bootstrap_components as dbc
from dash import html

import calsim_dash_widgets as cdw

dash.register_page(__name__, path="/alerts")
app = dash.get_app()


def make_small_alert_grid(obs_run: str, exp_run: str):
    grid = list()
    vars = {
        "shasta_storage": "Shasta Storage",
        "oroville_storage": "Oroville Storage",
        "banks_exports": "Banks Exports",
        "jones_exports": "Jones Exports",
    }
    small_to_make = {
        "Mean": cdw.alerts.TinyMeanAlert,
        "Max": cdw.alerts.TinyMaxAlert,
        "Min": cdw.alerts.TinyMinAlert,
    }
    for v, n in vars.items():
        row = []
        for kind, factory in small_to_make.items():
            row.append(
                factory(
                    observed=app.datasets[obs_run][v],
                    expected=app.datasets[exp_run][v],
                    children=f"{kind} {n}",
                )
            )
        grid.append(dbc.Row(dbc.Col(row, width="auto")))

    return dbc.Col(grid, width="auto")


def make_multiple_small_alert_grids():
    small_alerts = list()
    grids = {
        "Adjsuted Historical Hydrology": ("adj", "hist"),
        "Climate Change Level of Concern 95%": ("cc95", "hist"),
    }
    for title, (o, e) in grids.items():
        grid = make_small_alert_grid(o, e)
        small_alerts.append(html.H6(title, className="pt-3 pb-1"))
        small_alerts.append(dbc.Row(grid))

    return small_alerts


def make_storage_alerts():
    grids = {
        "Adjusted Historical Hydrology": ("adj", "hist"),
        "Climate Change Level of Concern 95%": ("cc95", "hist"),
    }
    storage_vars = {
        "Shasta Storage": "shasta_storage",
        "Oroville Storage": "oroville_storage",
    }
    alerts = list()
    for run_name, (o_key, e_key) in grids.items():
        row = list()
        alerts.append(html.H6(run_name, className="pt-3 pb-1"))
        for ts_name, ts_key in storage_vars.items():
            o = app.timeseries[o_key][ts_key]
            e = app.timeseries[e_key][ts_key]
            row.append(
                dbc.Col(
                    cdw.alerts.MeanStorageAlert(o, e, name=f"Mean {ts_name}"),
                    width="auto",
                )
            )
        alerts.append(dbc.Row(row))

    return alerts


def layout(**kwargs):
    small_alerts = make_multiple_small_alert_grids()
    storage_alerts = make_storage_alerts()
    alerts = {
        "Small Alerts": dbc.Col(small_alerts),
        "Storage Alerts": storage_alerts,
    }
    details = {
        "Small Alerts": "These alerts just show whether or not a certain "
        + "variable has a value we expect. You'll need to look at what's happening "
        + "yourself.",
        "Storage Alerts": "These alerts are designed to look at the values we care "
        + "about when looking at Storage values.",
    }
    sections = list()
    for name, section in alerts.items():
        sections.append(
            html.Div(
                [
                    html.H2(name),
                    html.P(details[name]),
                    dbc.Container(
                        children=section,
                        # fluid=True,
                    ),
                ],
                className="pt-3 pb-3",
            )
        )
    return html.Div(
        [
            html.H1("Alert Examples"),
            html.P(
                "Alerts can be used to compare values against expectations. These are "
                + "the fastest way to show results from a model."
            ),
            dbc.Stack(sections, gap=12),
        ]
    )
