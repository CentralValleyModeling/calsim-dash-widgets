from typing import Callable, Literal

import csrs
import pandas as pd
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


def annual_sum(
    timeseries: csrs.Timeseries | pandss.RegularTimeseries,
    month: int = 1,
    cfs_to_taf: bool = True,
) -> pd.DataFrame:
    df = timeseries.to_frame()
    if cfs_to_taf and (timeseries.units.lower() == "cfs"):
        if isinstance(df.index, pd.PeriodIndex):
            delta = df.index.to_timestamp(how="end") - df.index.to_timestamp()
        elif isinstance(df.index, pd.DatetimeIndex):
            delta = df.index.to_series().diff()
            # Assume diffs are cyclical on a 48 instance period, works for
            # months, days, hours. Not weeks
            delta.iloc[0] = delta.iloc[47]
            delta = pd.TimedeltaIndex(delta)
        else:
            raise ValueError(
                f"Cannot determine duration without date-like index: {type(df.index)=}"
            )
        seconds = delta.total_seconds()
        df = (df.mul(seconds, axis=0)) / 43_560_000  # cfs to TAF
        cols = df.columns.to_frame()
        cols["UNITS"] = ["TAF"]
        df.columns = pd.MultiIndex.from_frame(cols)
    return df.resample(pd.offsets.YearEnd(month=month)).sum()


def annual_eos(timeseries: csrs.Timeseries | pandss.RegularTimeseries) -> pd.DataFrame:
    df = timeseries.to_frame()
    if not hasattr(df.index, "month"):
        raise ValueError(
            f"Cannot filter by months without date-like index: {type(df.index)=}"
        )
    mask = df.index.month == 9
    return df.loc[mask].copy()
