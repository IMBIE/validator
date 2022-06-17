import pandas as pd
from dataclasses import dataclass
import datetime as dt
import numpy as np

from validator.const.basins import BasinGroup, BasinID
from validator.const.experiment_groups import ExperimentGroup
from validator.helpers.decimal_year_to_datetime import decimal_year_to_datetime
from validator.helpers.timedelta_to_decimal_year import timedelta_to_decimal_year


@dataclass(frozen=True)
class SeriesStatistics:
    start_date: dt.datetime
    stop_date: dt.datetime
    interval: dt.timedelta
    total_dm: float
    mean_dmdt: float


@dataclass(frozen=True)
class Series:
    """
    one data series from CSV data file
    """

    data: pd.DataFrame
    data_format: str
    contributor: str
    experiment_group: ExperimentGroup
    basin_id: BasinID
    basin_group: BasinGroup

    @property
    def identifier(self) -> str:
        return (
            f"{self.experiment_group.value}/{self.contributor}: {self.basin_id.value}"
        )

    def get_statistics(self) -> SeriesStatistics:
        epochs: np.ndarray = self.data["date"][:]

        first_epoch = epochs.min()
        last_epoch = epochs.max()

        start = decimal_year_to_datetime(first_epoch)
        stop = decimal_year_to_datetime(last_epoch)
        duration = stop - start
        interval = duration / epochs.size

        value_column = "dmdt" if self.data_format == "dmdt" else "dm"
        # error_column = f"{value_column}_sd"
        values = self.data[value_column][:]

        if self.data_format == "dmdt":
            mean_dmdt = np.mean(values)
            total_dm = mean_dmdt * timedelta_to_decimal_year(duration)
        else:
            total_dm = values.max() - values.min()
            mean_dmdt = total_dm / timedelta_to_decimal_year(duration)

        return SeriesStatistics(start, stop, interval, total_dm, mean_dmdt)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.identifier}'>"
