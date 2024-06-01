from typing import Any, Literal

import csrs
import dash_bootstrap_components as dbc
from dash import html

from . import aggregation, timeseries

StorageAggArguments = Literal["eos_mean", "eos_max", "eos_min", "mean", "max", "min"]
AGG_MEANING = {
    "eos_mean": "Average End of Sept Storage",
    "eos_max": "End of Sept Storage Maximum",
    "eos_min": "End of Sept Storage Minimum",
    "mean": "Average Monthly Storage",
    "max": "Maximum Single Month Storage",
    "min": "Minimum Single Month Storage",
}


class TimeseriesAlert(dbc.Card):
    def __init__(
        self,
        observed: csrs.Timeseries,
        expected: csrs.Timeseries,
        allowable_diff_perc: float = 0.05,
        name: str = "",
        **kwargs,
    ):
        self._observed = observed
        self._expected = expected
        self.allowable_diff_perc = allowable_diff_perc

        o = self.get_observed()
        e = self.get_expected()
        diff = o - e
        diff_perc = diff / e

        bad_comp = self.get_bad_comparability()
        name = name or self._observed.path.split("/")[2]
        units = self._observed.units

        if bad_comp:
            i = "bi bi-exclamation-triangle-fill"
            color = "warning"
        elif abs(diff_perc) >= self.allowable_diff_perc:
            i = "bi bi-x-octagon-fill"
            color = "danger"
        else:
            i = "bi bi-check-circle-fill"
            color = "success"
        # Assemble
        li_bootstrap = (
            "list-group-item d-flex justify-content-between "
            + f"align-items-center list-group-item-{color} p-1"
        )

        observed = html.Li(
            html.P(f"{o:,.0f} {units}", className="small m-0"),
            className=li_bootstrap,
        )
        difference = html.Li(
            [
                html.P(f"{diff:+,.0f} {units}", className="small m-0"),
                dbc.Badge(
                    f"{diff_perc:+,.0%}",
                    color="light",
                    text_color=color,
                    class_name="border me-1",
                ),
            ],
            className=li_bootstrap,
        )
        icon = html.I(
            className=f"{i} p-2 text-{color}",
            style={"font-size": "x-large"},
        )
        #
        body = dbc.CardBody(
            [
                html.H6(name, className="card-title"),
                html.Ul(
                    [observed, difference],
                    className="list-group",
                ),
            ],
            class_name="card-body p-2",
        )
        # Assemble children
        kwargs = {
            "color": color,
            "outline": True,
            "class_name": "m-1",
        } | kwargs
        super().__init__(
            children=[
                dbc.Row(
                    className="g-1 align-items-center",
                    children=[
                        dbc.Col(icon, class_name="col-md-2 align-items-center"),
                        dbc.Col(body, class_name="col-md-10"),
                    ],
                )
            ],
            **kwargs,
        )

    def get_observed(self) -> float:
        return self._observed.to_frame().iloc[:, 0].mean()

    def get_expected(self) -> float:
        return self._expected.to_frame().iloc[:, 0].mean()

    def get_bad_comparability(self) -> dict[str, tuple[Any, Any]]:
        not_comparable = dict()
        for attr, val in self._observed.model_dump(
            exclude=("scenario", "version")
        ).items():
            other = getattr(self._expected, attr)
            if hasattr(val, "__len__"):
                # Array, just check sizes
                if len(val) != len(other):
                    not_comparable[attr] = (len(val), len(other))
            else:
                if val != other:
                    not_comparable[attr] = (val, other)
        return not_comparable


class MeanStorageAlert(TimeseriesAlert):
    def get_observed(self) -> float:
        return aggregation.annual_eos(self._observed).iloc[:, 0].mean()

    def get_expected(self) -> float:
        return aggregation.annual_eos(self._expected).iloc[:, 0].mean()


class StudyHealthBoard(html.Div):
    def __init__(
        self,
        observed: csrs.Run,
        expected: csrs.Run,
        client: csrs.clients.Client | None = None,
    ):
        self._observed = observed
        self._expected = expected

        self.client = client or csrs.RemoteClient(
            "https://calsim-scenario-results-server.azurewebsites.net/"
        )  # Default to CSRS server
        alerts = {
            "Storage": [
                (MeanStorageAlert, "shasta_storage", "Shasta Storage"),
                (MeanStorageAlert, "folsom_storage", "Folsom Storage"),
                (MeanStorageAlert, "oroville_storage", "Oroville Storage"),
            ],
            "Exports": [
                (TimeseriesAlert, "banks_exports", "Banks Exports"),
                (TimeseriesAlert, "jones_exports", "Jones Exports"),
            ],
        }
        children = list()
        for section, paths in alerts.items():
            alert_objs = list()
            paths: list[tuple[TimeseriesAlert.__class__, str, str]]
            for alert_factory, path, name in paths:
                obj = alert_factory(
                    self.get_o_timeseries(path),
                    self.get_e_timeseries(path),
                    name=name,
                )
                alert_objs.append(obj)
            children.append(
                dbc.Stack(
                    [
                        html.H5(section),
                        dbc.Stack(alert_objs, direction="horizontal", gap=3),
                    ]
                )
            )
        super().__init__(children=children)

    def get_o_timeseries(self, path: str) -> csrs.Timeseries:
        obj = self._observed
        return self.client.get_timeseries(
            scenario=obj.scenario,
            version=obj.version,
            path=path,
        )

    def get_e_timeseries(self, path: str) -> csrs.Timeseries:
        obj = self._expected
        return self.client.get_timeseries(
            scenario=obj.scenario,
            version=obj.version,
            path=path,
        )


class TinyAlert(dbc.Badge):
    def __init__(
        self,
        observed: timeseries.TimeseriesDataset,
        expected: timeseries.TimeseriesDataset,
        filter,
        allowable_diff_perc: float = 0.05,
        filter_kwargs: dict = None,
        **kwargs,
    ):
        self.observed = observed
        self.expected = expected
        self.filter = filter
        self.allowable_diff_perc = allowable_diff_perc
        self.filter_kwargs = filter_kwargs or dict()
        self.kwargs = kwargs
        # Decide which badge to be
        try:
            ov = self.observed.filter_to_value(filter, **self.filter_kwargs)
            ev = self.expected.filter_to_value(filter, **self.filter_kwargs)
            diff = ov - ev
            if ev == 0:
                ev = 1.0  # Avoid ZeroDivisionError
            diff_perc = diff / ev
        except Exception:
            self.kwargs["color"] = "warning"
        else:
            if abs(diff_perc) > self.allowable_diff_perc:
                self.kwargs["color"] = "danger"
            else:
                self.kwargs["color"] = "success"
        name = self.observed.timeseries.path.split("/")[2]
        kwargs = {
            "className": "me-1",
            "pill": True,
            "children": name,
        } | self.kwargs
        super().__init__(**kwargs)


class TinyMeanAlert(TinyAlert):
    def __init__(
        self,
        observed: timeseries.TimeseriesDataset,
        expected: timeseries.TimeseriesDataset,
        allowable_diff_perc: float = 0.05,
        **kwargs,
    ):
        super().__init__(
            observed=observed,
            expected=expected,
            allowable_diff_perc=allowable_diff_perc,
            filter=aggregation.mean,
            **kwargs,
        )


class TinyMaxAlert(TinyAlert):
    def __init__(
        self,
        observed: timeseries.TimeseriesDataset,
        expected: timeseries.TimeseriesDataset,
        allowable_diff_perc: float = 0.05,
        **kwargs,
    ):
        super().__init__(
            observed=observed,
            expected=expected,
            allowable_diff_perc=allowable_diff_perc,
            filter=aggregation.max,
            **kwargs,
        )


class TinyMinAlert(TinyAlert):
    def __init__(
        self,
        observed: timeseries.TimeseriesDataset,
        expected: timeseries.TimeseriesDataset,
        allowable_diff_perc: float = 0.05,
        **kwargs,
    ):
        super().__init__(
            observed=observed,
            expected=expected,
            allowable_diff_perc=allowable_diff_perc,
            filter=aggregation.min,
            **kwargs,
        )
