import dash
import dash_bootstrap_components as dbc
from dash import html

import calsim_dash_widgets as cdw

dash.register_page(__name__, path="/cards")
app = dash.get_app()


def layout(**kwargs):
    cards = {
        "Single Data Point": [
            cdw.cards.StorageCard(app.timeseries["hist"]["shasta_storage"]),
            cdw.cards.StorageCard(
                app.timeseries["adj"]["shasta_storage"],
                header="Shasta",
            ),
            cdw.cards.AverageAnnualFlowCard(
                app.timeseries["cc50"]["banks_exports"],
                header="Banks Exports",
            ),
        ],
        "Sparklines": [
            cdw.cards.SparklineCard(app.timeseries["hist"]["banks_exports"]),
            cdw.cards.SparklineMonthlyAverageCard(
                app.timeseries["adj"]["jones_exports"],
                header="Jones Exports",
            ),
        ],
        "Comparative Single Data Point": [
            cdw.cards.CompareStorageCard(
                app.timeseries["hist"]["shasta_storage"],
                app.timeseries["cc95"]["shasta_storage"],
            ),
            cdw.cards.CompareStorageCard(
                app.timeseries["hist"]["oroville_storage"],
                app.timeseries["adj"]["oroville_storage"],
                header="Oroville",
                kind="eos_max",
            ),
        ],
        "Comparative Sparklines": [
            cdw.cards.ComparativeSparklineCard(
                app.timeseries["hist"]["jones_exports"],
                app.timeseries["cc95"]["jones_exports"],
            ),
            cdw.cards.ComparativeSparklineMonthlyAverageCard(
                app.timeseries["hist"]["banks_exports"],
                app.timeseries["cc95"]["banks_exports"],
                header="Banks Exports (Monthly Average)",
            ),
        ],
    }
    details = {
        "Single Data Point": "Show a summary of a timeseries",
        "Sparklines": "Show the temporal pattern on a timeseries",
        "Comparative Single Data Point": "Compare two similar timeseries",
        "Comparative Sparklines": "Compare the temporal patterns of two timeseries",
    }
    sections = list()
    for name, section in cards.items():
        sections.append(
            html.Div(
                [
                    html.H2(name),
                    html.P(details[name]),
                    dbc.Stack(
                        children=[*section],
                        direction="horizontal",
                        gap=3,
                    ),
                ],
                className="pt-3 pb-3",
            )
        )
    return html.Div(
        [
            html.H1("Card Examples"),
            html.P(
                "Cards can be used to quickly convey the content, and "
                + "comparative content of a timeseries."
            ),
            dbc.Stack(sections, gap=12),
        ]
    )
