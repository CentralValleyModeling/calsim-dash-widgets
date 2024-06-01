import dash_bootstrap_components as dbc
from dash import html

from . import assets


class CalSim3NavbarBrand(dbc.NavbarBrand):
    def __init__(self, label: str, img: html.Img = None, **kwargs):
        if img is None:
            img = html.Img(
                src=str(assets.ICON_PNG),
                height="30px",
            )
        label = dbc.NavbarBrand(label, className="m-0")
        children = dbc.Row(
            [
                dbc.Col(img),
                dbc.Col(label),
            ],
            align="center",
            className="g-2",
        )
        # Update kwargs
        kwargs = {
            "href": "/",
            "children": children,
            "style": {
                "textDecoration": "none",
                "margin": "0",
            },
        } | kwargs
        super().__init__(**kwargs)
