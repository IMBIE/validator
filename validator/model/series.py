import pandas as pd
from dataclasses import dataclass
import datetime as dt
import numpy as np

from validator.const.basins import BasinGroup, BasinID
from validator.const.experiment_groups import ExperimentGroup
from validator.helpers.decimal_year_to_datetime import decimal_year_to_datetime
from validator.helpers.timedelta_to_decimal_year import timedelta_to_decimal_year
from validator.proc.dm_to_dmdt.dm_to_dmdt import dm_to_dmdt


@dataclass(frozen=True)
class SeriesStatistics:
    start_date: dt.datetime
    stop_date: dt.datetime
    interval: dt.timedelta
    total_dm: float
    mean_dmdt: float
    computed: bool = False


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
    computed: bool = False

    @property
    def identifier(self) -> str:
        return (
            f"{self.experiment_group.value}/{self.contributor}: {self.basin_id.value}"
        )

    def to_dmdt(self) -> "Series":
        assert self.data_format == "dm", "series already contains dmdt data"

        dmdt_data = self.data.copy()
        dmdt_data["date"], dmdt_data["dmdt"], dmdt_data["dmdt_sd"] = dm_to_dmdt(
            self.data["date"].values,
            self.data["dm"].values,
            self.data["dm_sd"].values,
            3.0,
        )
        dmdt_data.drop("dm", axis=1)
        dmdt_data.drop("dm_sd", axis=1)

        return Series(
            dmdt_data,
            "dmdt",
            self.contributor,
            self.experiment_group,
            self.basin_id,
            self.basin_group,
            computed=True,
        )

    def to_dm(self) -> "Series":
        assert self.data_format != "dm", "series already contains dm data"

        dm_data = self.data.copy()
        diffs = np.concatenate([1], np.diff(self.data["date"].values))
        dm_data["dmdt"] = np.cumsum(self.data["dm"].values) / diffs
        dm_data["dmdt_sd"] = np.cumsum(self.data["dm_sd"].values) / diffs

        dm_data.drop("dmdt")
        dm_data.drop("dmdt_sd")

        return Series(
            dm_data,
            "dm",
            self.contributor,
            self.experiment_group,
            self.basin_id,
            self.basin_group,
            computed=True,
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
        values = self.data[value_column].values

        if self.data_format == "dmdt":
            mean_dmdt = np.nanmean(values)
            total_dm = mean_dmdt * timedelta_to_decimal_year(duration)
        else:
            total_dm = values[-1]
            mean_dmdt = total_dm / timedelta_to_decimal_year(duration)

        return SeriesStatistics(
            start, stop, interval, total_dm, mean_dmdt, self.computed
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.identifier}'>"
