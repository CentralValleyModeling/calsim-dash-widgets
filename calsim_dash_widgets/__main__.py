import ssl
from pathlib import Path

import csrs
import dash
import dash_bootstrap_components as dbc

from . import cards, plots

STATIC = Path(__file__).parent / "static"
ASSETS = Path(__file__).parent / "assets"


def verify_dwr_cert(cert):
    allowed_cert_fingerprint = "SHA256_FINGERPRINT_OF_ALLOWED_CERT"

    # Extract the fingerprint of the provided cert
    cert_fingerprint = cert["fingerprint_sha256"]

    if cert_fingerprint == allowed_cert_fingerprint:
        return True
    print(cert_fingerprint)
    return False


def create_custom_ssl_context():
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED

    # Load system CA certificates
    context.load_default_certs()

    def custom_verify_cb(conn, cert, errnum, depth, ok):
        if not ok:
            if verify_dwr_cert(cert):
                return True
        return ok

    context.verify_flags |= ssl.VERIFY_X509_TRUSTED_FIRST
    context.verify_cb = custom_verify_cb
    return context


def main():
    # Load data
    context = create_custom_ssl_context()
    client = csrs.RemoteClient(
        "https://calsim-scenario-results-server.azurewebsites.net/",
        verify=context,
    )
    ts_storage = client.get_timeseries(
        scenario="Adjusted Historical (Danube)",
        version="1.2",
        path="shasta_storage",
    )
    ts_storage_hist = client.get_timeseries(
        scenario="Historical (Danube)",
        version="1.1",
        path="shasta_storage",
    )
    ts_exports = client.get_timeseries(
        scenario="Adjusted Historical (Danube)",
        version="1.2",
        path="banks_exports",
    )

    # Create app
    app = dash.Dash(
        __name__,
        title="CS3 Widgets",
        external_stylesheets=[ASSETS, dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    )

    # Create widgets
    navbar = dbc.NavbarSimple(
        brand="CalSim Dash Widgets Example",
        color="dark",
        dark=True,
        className="mb-2",
    )

    storage_long_term = cards.StorageCard(ts_storage)
    storage_end_of_sept_max = cards.StorageCard(
        ts_storage,
        header="Shasta Storage (Maximum Sept)",
        kind="eos_max",
    )
    storage_plot = cards.SparklineCard(
        ts_storage,
        header="Shasta Storage",
    )
    storage_plot_monthly = cards.SparklineMonthlyAverageCard(
        ts_storage,
        header="Average Monthly Shasta Storage",
    )
    comp_storage_long_term = cards.CompareStorageCard(
        base_timeseries=ts_storage_hist,
        alt_timeseries=ts_storage,
    )
    comp_storage_max = cards.CompareStorageCard(
        base_timeseries=ts_storage_hist,
        alt_timeseries=ts_storage,
        header="Adjusted vs Historical (End of Sept Max Shasta Storage)",
        kind="eos_max",
    )

    exports_exceedance_plot = plots.ExceedancePlot(ts_exports)
    storage_exceedance_plot = plots.StorageExceedancePlot(
        ts_storage,
        header="Shasta Storage",
    )
    exports_ts_plot = plots.TimeseriesPlot(ts_exports)
    storage_ts_plot = plots.TimeseriesPlot(ts_storage, header="Shasta Storage")

    card_div = dash.html.Div(
        className="ml-3 mr-3 p-3",
        children=[
            dash.html.H2("Cards"),
            dbc.Stack(
                [
                    dbc.Stack(
                        [
                            storage_long_term,
                            storage_end_of_sept_max,
                            storage_plot,
                            storage_plot_monthly,
                        ],
                        direction="horizontal",
                        gap=3,
                    ),
                    dbc.Stack(
                        [
                            comp_storage_long_term,
                            comp_storage_max,
                        ],
                        direction="horizontal",
                        gap=3,
                    ),
                ],
                direction="vertical",
                gap=3,
            ),
        ],
    )
    plot_div = dash.html.Div(
        className="ml-3 mr-3 p-3",
        children=[
            dash.html.H2("Plots"),
            dbc.Stack(
                [
                    dash.html.H4("Exceedance"),
                    dbc.Stack(
                        [
                            exports_exceedance_plot,
                            storage_exceedance_plot,
                        ],
                        direction="horizontal",
                    ),
                    dash.html.H4("Timeseries"),
                    dbc.Stack(
                        [
                            exports_ts_plot,
                            storage_ts_plot,
                        ],
                        direction="horizontal",
                    ),
                ],
                direction="vertical",
            ),
        ],
    )
    app.layout = dash.html.Div(
        [
            dash.dcc.Location(id="url", refresh=False),
            navbar,
            card_div,
            plot_div,
        ]
    )
    app.run(debug=True)


if __name__ == "__main__":
    main()
