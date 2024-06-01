import sys
from pathlib import Path

import csrs
import dash
import dash_bootstrap_components as dbc
from dash import html

sys.path.append("..")
import calsim_dash_widgets as cdw

from . import data


class CustomDash(dash.Dash):
    @property
    def timeseries(self) -> dict[str, dict[str, csrs.Timeseries]]:
        return data.timeseries

    @property
    def runs(self) -> dict[str, csrs.Run]:
        return data.runs

    @property
    def datasets(self) -> dict[str, dict[str, cdw.timeseries.TimeseriesDataset]]:
        return data.datasets


def main_old():

    exports_exceedance_plot = plots.ExceedancePlot(ts_exports)
    storage_exceedance_plot = plots.StorageExceedancePlot(
        ts_storage,
        header="Shasta Storage",
    )
    exports_ts_plot = plots.TimeseriesPlot(ts_exports)
    storage_ts_plot = plots.TimeseriesPlot(
        ts_storage,
        header="Shasta Storage",
    )
    exports_comp_exceedance_plot = plots.CompareExceedancePlot(
        ts_exports_hist,
        ts_exports,
    )
    storage_comp_exceedance_plot = plots.CompareStorageExceedancePlot(
        ts_storage_hist,
        ts_storage,
        header="Shasta Storage",
    )


def main():
    app = CustomDash(
        __name__,
        title="CS3 Widgets",
        use_pages=True,
        suppress_callback_exceptions=True,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            dbc.icons.BOOTSTRAP,
        ],
    )
    links_to_make = {
        "Cards": "/cards",
        "Alerts": "/alerts",
    }
    links = dbc.Row(
        [
            dbc.Col(dbc.NavItem(dbc.NavLink(name, href=link)))
            for name, link in links_to_make.items()
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )
    navbar = dbc.NavbarSimple(
        brand=cdw.branding.CalSim3NavbarBrand(label="CalSim3 Widgets"),
        children=links,
        dark=True,
        color="dark",
        expand=True,
    )
    body = dbc.Container(dash.page_container)
    app.layout = html.Div([navbar, body])
    app.run(debug=True)


if __name__ == "__main__":
    main()
