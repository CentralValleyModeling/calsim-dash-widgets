import csrs
import dash
import dash_bootstrap_components as dbc

from . import aggregation, plotting


class ExceedancePlot(dash.html.Div):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = "",
        **kwargs,
    ):
        self.timeseries = timeseries
        self.header = header or self.timeseries.path.split("/")[2]
        super().__init__(**kwargs)
        self.children = [
            dbc.Stack(
                [
                    dash.html.H6(self.header),
                    plotting.exceedance(
                        self.timeseries.to_frame().iloc[:, 0],
                        xaxis_title=f"{self.header} ({self.timeseries.units})",
                    ),
                ],
                direction="vertical",
            )
        ]


class StorageExceedancePlot(dash.html.Div):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = "",
        **kwargs,
    ):
        self.timeseries = timeseries
        self.header = header or self.timeseries.path.split("/")[2]
        super().__init__(**kwargs)
        df = aggregation.annual_eos(self.timeseries)
        self.children = [
            dbc.Stack(
                [
                    dash.html.H6(self.header),
                    plotting.exceedance(
                        df.iloc[:, 0],
                        xaxis_title=f"{self.header} ({self.timeseries.units})",
                    ),
                ],
                direction="vertical",
            )
        ]


class TimeseriesPlot(dash.html.Div):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = "",
        **kwargs,
    ):
        self.timeseries = timeseries
        self.header = header or self.timeseries.path.split("/")[2]
        super().__init__(**kwargs)
        df = self.timeseries.to_frame()
        self.children = [
            dbc.Stack(
                [
                    dash.html.H6(self.header),
                    plotting.timeseries(
                        df.iloc[:, 0],
                        yaxis_title=f"{self.header} ({self.timeseries.units})",
                    ),
                ],
                direction="vertical",
            )
        ]
