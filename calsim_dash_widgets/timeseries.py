import csrs
import pandas as pd


class TimeseriesDataset:
    def __init__(self, timeseries: csrs.Timeseries):
        self.timeseries = timeseries

    def set_timeseries(self, new: csrs.Timeseries):
        self.timeseries = new

    def filter_to_value(self, action, **kwargs) -> float:
        v = action(self.timeseries, **kwargs)
        if not isinstance(v, float):
            raise ValueError(f"{action} returned {type(v)}, expected float")
        return v

    def filter_to_series(self, action, **kwargs) -> pd.Series:
        v = action(self.timeseries, **kwargs)
        if not isinstance(v, pd.Series):
            raise ValueError(f"{action} returned {type(v)}, expected pandas.Series")
        return v


class MultipleTimeseriesDataset:
    def __init__(self, timeseries: tuple[csrs.Timeseries]):
        self.timeseries = timeseries

    def set_timeseries(self, new: tuple[csrs.Timeseries]):
        self.timeseries = new

    def filter_to_value(self, action, **kwargs) -> tuple[float]:
        v = action(self.timeseries, **kwargs)
        if not isinstance(v, tuple[float]):
            raise ValueError(f"{action} returned {type(v)}, expected tuple[float]")
        return v

    def filter_to_series(self, action, **kwargs) -> pd.DataFrame:
        v = action(self.timeseries, **kwargs)
        if not isinstance(v, pd.DataFrame):
            raise ValueError(f"{action} returned {type(v)}, expected pandas.DataFrame")
        return v
