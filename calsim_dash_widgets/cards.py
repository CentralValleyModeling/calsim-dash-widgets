from typing import Literal

import csrs
import dash
import dash_bootstrap_components as dbc
import pandas as pd

from . import aggregation, plotting

StorageAggArguments = Literal["eos_mean", "eos_max", "eos_min", "mean", "max", "min"]
AGG_MEANING = {
    "eos_mean": "Average End of Sept Storage",
    "eos_max": "End of Sept Storage Maximum",
    "eos_min": "End of Sept Storage Minimum",
    "mean": "Average Monthly Storage",
    "max": "Maximum Single Month Storage",
    "min": "Minimum Single Month Storage",
}


class _TimeseriesCard(dbc.Card):
    value: float
    timeseries: csrs.Timeseries
    header: str
    display_units: str

    def _init_card(self, **kwargs):
        # Initialize the sub-card elements
        display_subheader = dash.html.P(
            kwargs.pop("subheader", "summary value"),
            className="small em m-0 p-0",
        )
        display_value = dash.html.H3(
            f"{self.value:,.0f} {self.display_units}",
            className="card-title",
        )
        # Assemble the body
        body = [display_subheader, display_value]
        # footer
        footer = [
            dash.html.P(
                f"{self.timeseries.scenario} (v{self.timeseries.version})",
                className="small mb-0",
            ),
        ]

        # Assemble the whole card
        _children = [
            dbc.CardHeader(self.header),
            dbc.CardBody(body, class_name="card-body pt-2 pb-1"),
            dbc.CardFooter(footer),
        ]

        # Resolve passed kwargs
        custom_kwargs = dict(
            color="secondary",
            outline=True,
        )
        custom_kwargs = custom_kwargs | kwargs
        super().__init__(
            _children,
            **custom_kwargs,
        )


class StorageCard(_TimeseriesCard):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = None,
        kind: StorageAggArguments = "eos_mean",
        **kwargs,
    ):

        self.timeseries = timeseries
        self.header = header or timeseries.path.split("/")[2]
        agg_func = getattr(aggregation, kind)
        self.value = agg_func(timeseries)
        self.display_units = self.timeseries.units
        self._init_card(subheader=AGG_MEANING.get(kind, kind), **kwargs)


class AverageAnnualFlowCard(_TimeseriesCard):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = None,
        **kwargs,
    ):
        self.timeseries = timeseries
        self.header = header or timeseries.path.split("/")[2]
        self.value = aggregation.annual_sum(timeseries).iloc[:, 0].mean()
        if self.timeseries.units.lower() == "cfs":
            self.display_units = "TAF"  # The above step converts
        else:
            self.display_units = self.timeseries.units
        self._init_card(subheader="Average Annual Flow", **kwargs)


class SparklineCard(dbc.Card):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = None,
        **kwargs,
    ):
        self.timeseries = timeseries
        self.header = header or timeseries.path.split("/")[2]
        self._init_card(**kwargs)

    def _get_sparkline(self):
        return plotting.sparkline(
            self.timeseries.to_frame().iloc[:, 0],
            yaxis=dict(title=self.timeseries.units),
        )

    def _init_card(self, **kwargs):
        sparkline = self._get_sparkline()

        # Assemble the body
        body = list()
        body.extend([sparkline])
        # footer
        footer = [
            dash.html.P(
                f"{self.timeseries.scenario} (v{self.timeseries.version})",
                className="small mb-0",
            ),
        ]
        # Assemble the whole card
        _children = list()
        _children.extend(
            [
                dbc.CardHeader(self.header),
                dbc.CardBody(body),
                dbc.CardFooter(footer),
            ]
        )
        # Resolve passed kwargs
        custom_kwargs = (
            dict(
                color="secondary",
                outline=True,
            )
            | kwargs
        )
        super().__init__(
            _children,
            **custom_kwargs,
        )


class SparklineMonthlyAverageCard(SparklineCard):
    def _get_sparkline(self):
        df = self.timeseries.to_frame()
        df = df.groupby(df.index.month).mean()
        df.index = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        return plotting.sparkline(
            df.iloc[:, 0],
            yaxis=dict(title=self.timeseries.units),
        )


class _ComparativeTimeseriesCard(dbc.Card):
    base: float
    alt: float
    base_timeseries: csrs.Timeseries
    alt_timeseries: csrs.Timeseries
    header: str
    subheader: str

    def _init_card(self, **kwargs):
        # Initialize the sub-card elements
        diff = self.alt - self.base
        display_value = f"{diff:,.0f} {self.base_timeseries.units}"
        display_subheader = dash.html.P(
            self.subheader,
            className="small em m-0 p-0",
        )
        if diff > 0:
            display_value = dash.html.H3(
                [dash.html.I(className="bi bi-arrow-up me-3"), display_value],
                className="card-title",
            )
        elif diff < 0:
            display_value = dash.html.H3(
                [
                    dash.html.I(
                        className="bi bi-arrow-down me-3",
                    ),
                    display_value,
                ],
                className="card-title",
            )
        else:
            display_value = dash.html.H3("No difference")

        if self.base_timeseries.scenario == self.alt_timeseries.scenario:
            va = self.alt_timeseries.version
            vb = self.base_timeseries.version
            display_details = dash.html.P(
                f"{self.base_timeseries.scenario} (version {va} vs {vb})",
                className="card-text p-1",
            )
        else:
            a = f"{self.alt_timeseries.scenario}"
            b = f"{self.base_timeseries.scenario}"
            display_details = dash.html.P(
                f"{a} vs {b}",
                className="small mb-0",
            )
        # Assemble the body
        body = [
            display_subheader,
            display_value,
        ]
        # footer
        footer = [display_details]
        # Assemble the whole card
        _children = [
            dbc.CardHeader(self.header),
            dbc.CardBody(body, class_name="card-body pt-2 pb-1"),
            dbc.CardFooter(footer),
        ]

        # Resolve passed kwargs
        custom_kwargs = dict(
            color="secondary",
            outline=True,
        )
        custom_kwargs = custom_kwargs | kwargs
        super().__init__(
            _children,
            **custom_kwargs,
        )


class CompareStorageCard(_ComparativeTimeseriesCard):
    def __init__(
        self,
        base_timeseries: csrs.Timeseries,
        alt_timeseries: csrs.Timeseries,
        header: str = "",
        subheader: str = "",
        kind: StorageAggArguments = "eos_mean",
        **kwargs,
    ):
        self.base_timeseries = base_timeseries
        self.alt_timeseries = alt_timeseries
        if base_timeseries.units != alt_timeseries.units:
            ua = alt_timeseries.units
            ub = base_timeseries.units
            raise ValueError(f"Cannot compare with diff units: alt={ua}, base={ub}")
        self.header = header or f"{alt_timeseries.path.split('/')[2]}"
        self.subheader = "Compare " + AGG_MEANING.get(kind, kind)
        agg_func = getattr(aggregation, kind)
        self.base = agg_func(base_timeseries)
        self.alt = agg_func(alt_timeseries)
        self._init_card(**kwargs)


class ComparativeSparklineCard(dbc.Card):
    def __init__(
        self,
        base: csrs.Timeseries,
        alt: csrs.Timeseries,
        header: str = None,
        **kwargs,
    ):
        self.base = base
        self.alt = alt
        if self.base.units != self.alt.units:
            raise ValueError("Cannot plot timeseries with different units")
        self.header = header or self.base.path.split("/")[2]
        self._init_card(**kwargs)

    def _get_sparkline(self):
        return plotting.comparative_sparkline(
            {
                self.base.scenario: self.base.to_frame().iloc[:, 0],
                self.alt.scenario: self.alt.to_frame().iloc[:, 0],
            },
            yaxis=dict(title=self.base.units),
        )

    def _init_card(self, **kwargs):
        sparkline = self._get_sparkline()

        # Assemble the body
        body = list()
        body.extend([sparkline])
        # footer
        footer = [
            dash.html.Div(
                [
                    dash.html.P(
                        f"{self.base.scenario} version {self.base.version}",
                        className="small mb-0",
                    ),
                    dash.html.P(
                        f"{self.alt.scenario} version {self.alt.version}",
                        className="small mb-0",
                    ),
                ]
            )
        ]
        # Assemble the whole card
        _children = list()
        _children.extend(
            [
                dbc.CardHeader(self.header),
                dbc.CardBody(body),
                dbc.CardFooter(footer),
            ]
        )
        # Resolve passed kwargs
        custom_kwargs = (
            dict(
                color="secondary",
                outline=True,
            )
            | kwargs
        )
        super().__init__(
            _children,
            **custom_kwargs,
        )


class ComparativeSparklineMonthlyAverageCard(ComparativeSparklineCard):
    def _get_sparkline(self):
        def _reshape(ts: csrs.Timeseries) -> pd.DataFrame:
            df = ts.to_frame()
            df = df.groupby(df.index.month).mean()
            df.index = [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ]
            return df

        df_base = _reshape(self.base)
        df_alt = _reshape(self.alt)
        return plotting.comparative_sparkline(
            {
                self.base.scenario: df_base.iloc[:, 0],
                self.alt.scenario: df_alt.iloc[:, 0],
            },
            yaxis=dict(title=self.base.units),
        )
