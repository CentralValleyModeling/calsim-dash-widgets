import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path="/")


def layout(**kwargs):
    page_descriptions = {
        "/alerts": html.P(
            "The most basic form of data display. They don't even show any "
            + "numbers, just a single color"
        ),
        "/cards": html.P("Multiple quick glances at the data of one or two runs."),
    }
    toasts = list()
    for page in dash.page_registry.values():
        path: str = page["path"]
        name: str = page["name"]
        if path not in page_descriptions:
            continue
        desc = page_descriptions[path]
        link = html.A(
            "See Examples",
            href=page["path"],
            className="link-info",
        )
        content = dbc.Col(
            [
                dbc.Row(desc),
                dbc.Row(link),
            ]
        )
        toast = dbc.Toast(
            header=html.H3(name),
            children=content,
            class_name="m-1 pb-2",
        )
        toasts.append(toast)

    return dbc.Col(
        [
            dbc.Row(html.H1("Widget Types")),
            dbc.Row(toasts),
        ]
    )
