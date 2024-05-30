from typing import Literal

import csrs
import dash
import dash_bootstrap_components as dbc

from . import aggregation, plotting

StorageAggArguments = Literal["eos_mean", "eos_max", "eos_min", "mean", "max", "min"]


class TimeseriesCard(dbc.Card):
    value: float
    timeseries: csrs.Timeseries
    header: str

    def _init_card(self, **kwargs):
        # Initialize the sub-card elements
        display_subheader = dash.html.P(
            kwargs.pop("subheader", "summary value"),
            className="small em m-0 p-0",
        )
        display_value = dash.html.H3(
            f"{self.value:,.0f} {self.timeseries.units}",
            className="card-title",
        )
        # Assemble the body
        body = [display_subheader, display_value]
        # footer
        footer = [
            dash.html.P(
                f"{self.timeseries.scenario} (v{self.timeseries.version})",
                className="small",
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


class StorageCard(TimeseriesCard):
    def __init__(
        self,
        timeseries: csrs.Timeseries,
        header: str = None,
        kind: StorageAggArguments = "eos_mean",
        **kwargs,
    ):
        agg_subheader = {
            "eos_mean": "Average End of Sept Storage",
            "eos_max": "Max End of Sept Storage",
            "eos_min": "Min End of Sept Storage",
            "mean": "Average Storage",
            "max": "Maximum Storage",
            "min": "Minimum Storage",
        }
        self.timeseries = timeseries
        self.header = header or timeseries.path.split("/")[2]
        agg_func = getattr(aggregation, kind)
        self.value = agg_func(timeseries)
        self._init_card(subheader=agg_subheader.get(kind, kind), **kwargs)


class AverageAnnualFlowCard(TimeseriesCard):
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
        self._init_card(**kwargs)


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
        return plotting.sparkline(self.timeseries.to_frame().iloc[:, 0])

    def _init_card(self, **kwargs):
        sparkline = self._get_sparkline()
        display_body_details = dash.html.P(
            f"{self.timeseries.scenario}",
            className="card-text",
        )
        # Assemble the body
        body = list()
        body.extend([sparkline, display_body_details])
        # Assemble the whole card
        _children = list()
        _children.extend(
            [
                dbc.CardHeader(self.header),
                dbc.CardBody(body),
                dbc.CardFooter(f"Run Version: {self.timeseries.version}"),
            ]
        )
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
        return plotting.sparkline(df.iloc[:, 0])


class ComparativeTimeseriesCard(dbc.Card):
    base: float
    alt: float
    base_timeseries: csrs.Timeseries
    alt_timeseries: csrs.Timeseries
    header: str

    def _init_card(self, **kwargs):
        # Initialize the sub-card elements
        diff = self.alt - self.base
        display_value = f"{diff:,.0f} {self.base_timeseries.units}"

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
            display_body_details = dash.html.P(
                f"{self.base_timeseries.scenario} (version {va} vs {vb})",
                className="card-text",
            )
        else:
            a = f"{self.alt_timeseries.scenario}"
            b = f"{self.base_timeseries.scenario}"
            display_body_details = dash.html.P(
                f"{a} vs {b}",
                className="card-text",
            )
        # Assemble the body
        body = list()
        body.extend([display_value, display_body_details])
        # Assemble the whole card
        _children = list()
        _children.extend(
            [
                dbc.CardHeader(self.header),
                dbc.CardBody(body),
            ]
        )
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


class CompareStorageCard(ComparativeTimeseriesCard):
    def __init__(
        self,
        base_timeseries: csrs.Timeseries,
        alt_timeseries: csrs.Timeseries,
        header: str = None,
        kind: StorageAggArguments = "eos_mean",
        **kwargs,
    ):
        self.base_timeseries = base_timeseries
        self.alt_timeseries = alt_timeseries
        if base_timeseries.units != alt_timeseries.units:
            ua = alt_timeseries.units
            ub = base_timeseries.units
            raise ValueError(f"Cannot compare with diff units: alt={ua}, base={ub}")
        self.header = header or f"Compare {alt_timeseries.path.split('/')[2]}"
        agg_func = getattr(aggregation, kind)
        self.base = agg_func(base_timeseries)
        self.alt = agg_func(alt_timeseries)
        self._init_card(**kwargs)
