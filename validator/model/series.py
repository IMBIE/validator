from os import truncate
import pandas as pd
from dataclasses import dataclass
import datetime as dt
import numpy as np

from validator.const.basins import BasinGroup, BasinID
from validator.const.experiment_groups import ExperimentGroup
from validator.helpers.decimal_year_to_datetime import decimal_year_to_datetime
from validator.helpers.timedelta_to_decimal_year import timedelta_to_decimal_year
from validator.proc.dm_to_dmdt.dm_to_dmdt import LSQMethod, dm_to_dmdt


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

        # set dmdt configuration
        dmdt_settings = dict(
            wsize=3.0,
            lsq_method=LSQMethod.weighted,
            truncate=False,
            tapering=True,
        )

        dmdt_data = self.data.copy()
        dmdt_data["date"], dmdt_data["dmdt"], dmdt_data["dmdt_sd"] = dm_to_dmdt(
            self.data["date"].values,
            self.data["dm"].values,
            self.data["dm_sd"].values,
            **dmdt_settings,
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

        # dm_data = self.data.copy()

        if "date_0" in self.data.columns:
            dates = np.hstack([self.data.date_0.values[0], self.data.date_1.values])
            diffs = np.diff(dates)
            dm = np.hstack([0, np.cumsum(self.data.dmdt.values) * diffs])

            dm_sd = np.sqrt(
                np.cumsum(
                    np.hstack([self.data.dmdt_sd.values[0], self.data.dmdt_sd.values])
                )
            ) * np.sqrt(np.hstack([1, diffs]))
        else:
            dates = self.data.date.values
            diffs = np.diff(dates)
            dm = np.cumsum(self.data.dmdt.values) * np.hstack([0, diffs])
            dm_sd = np.sqrt(np.cumsum(self.data.dmdt_sd.values)) * np.sqrt(
                np.hstack([1, diffs])
            )

        dm_data = pd.DataFrame(
            {
                "date": dates,
                "dm": dm,
                "dm_sd": dm_sd,
            }
        )

        # diffs = np.hstack([1.0, np.diff(self.data.date.values)])
        # dm_data["dm"] = np.cumsum(self.data.dmdt.values) / diffs
        # dm_data["dm_sd"] = np.cumsum(self.data.dmdt_sd.values) / diffs

        # dm_data.drop("dmdt", axis=1)
        # dm_data.drop("dmdt_sd", axis=1)

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
        if "date_0" in self.data.columns:
            series_start = self.data.date_0.min()
            series_stop = self.data.date_1.max()

        else:
            series_start = self.data.date.min()
            series_stop = self.data.date.max()

        num_records = self.data.index.size

        start = decimal_year_to_datetime(series_start)
        stop = decimal_year_to_datetime(series_stop)
        duration = stop - start
        interval = duration / num_records

        value_column = "dmdt" if self.data_format == "dmdt" else "dm"
        # error_column = f"{value_column}_sd"
        values = self.data[value_column].values

        if self.data_format == "dmdt":
            mean_dmdt = np.nanmean(values)
            total_dm = mean_dmdt * timedelta_to_decimal_year(duration)
        else:
            total_dm = values[-1] - values[0]
            mean_dmdt = total_dm / timedelta_to_decimal_year(duration)

        return SeriesStatistics(
            start, stop, interval, total_dm, mean_dmdt, self.computed
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.identifier}'>"
