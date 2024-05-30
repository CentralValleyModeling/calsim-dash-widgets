from typing import Callable, Literal

import csrs
import pandss


def agg(
    timeseries: csrs.Timeseries | pandss.RegularTimeseries,
    func: Callable | str | list | dict | None = None,
    axis: Literal[0, "index"] = 0,
    *args,
    **kwargs,
) -> float:
    return timeseries.to_frame().iloc[:, 0].agg(func, axis, *args, **kwargs)


def mean(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> float:
    return agg(timeseries, "mean")


def min(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> float:
    return agg(timeseries, "min")


def max(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> float:
    return agg(timeseries, "max")


def eos_agg(
    timeseries: csrs.Timeseries | pandss.RegularTimeseries,
    func: Callable | str | list | dict | None = None,
    axis: Literal[0, "index"] = 0,
    *args,
    **kwargs,
) -> float:
    df = timeseries.to_frame()
    if not hasattr(df.index, "month"):
        raise ValueError(
            f"Cannot filter by months without date-like index: {type(df.index)=}"
        )
    mask = df.index.month == 9
    df = df.loc[mask]
    return df.iloc[:, 0].agg(func, axis, *args, **kwargs)


def eos_mean(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> float:
    return eos_agg(timeseries, "mean")


def eos_min(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> float:
    return eos_agg(timeseries, "min")


def eos_max(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> float:
    return eos_agg(timeseries, "max")
