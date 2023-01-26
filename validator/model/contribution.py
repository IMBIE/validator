from dataclasses import dataclass, field
from optparse import Option
from typing import Iterator, List, Optional, TextIO, Union
import pandas as pd
import numpy as np
from itertools import product

from validator.const.basins import (
    BasinGroup,
    BasinID,
    IceSheet,
    parse_basin,
    REGIONS_ZWALLY,
    REGIONS_RIGNOT,
)
from validator.helpers.decimal_year_to_datetime import decimal_year_to_datetime

from validator.model.schema import Schema
from .series import Series
import datetime as dt

from ..const.experiment_groups import ExperimentGroup


class FormatError(Exception):
    """
    raised when a data file does not match the IMBIE data format
    """


@dataclass(frozen=True)
class Statistics:
    start: dt.datetime
    end: dt.datetime
    duration: dt.timedelta
    interval: dt.timedelta


@dataclass(frozen=True)
class Contribution:
    username: str
    experiment_group: ExperimentGroup
    # name: str = None
    # institute: str = None
    series: List[Series] = field(default_factory=list)

    def join(self, *others: "Contribution") -> "Contribution":
        """
        return new contribution which combines data
        of all
        """
        series = self.series
        for contrib in others:
            series += contrib.series

        return Contribution(self.username, self.experiment_group, series)

    def filter(
        self,
        *,
        format: str = None,
        basin_id: BasinID = None,
        basin_group: BasinGroup = None,
    ) -> "Contribution":
        series = self.series.copy()

        if format is not None:
            series = [s for s in series if s.data_format == format]
        if basin_group is not None:
            series = [s for s in series if s.basin_group == basin_group]
        if basin_id is not None:
            series = [s for s in series if s.basin_id == basin_id]

        return Contribution(self.username, self.experiment_group, series)

    def get(
        self,
        *,
        format: str = None,
        basin_id: BasinID = None,
        basin_group: BasinGroup = None,
    ) -> Optional[Series]:
        return self.filter(
            basin_id=basin_id, basin_group=basin_group, format=format
        ).first()

    def __iter__(self) -> Iterator[Series]:
        yield from self.series

    def first(self) -> Optional[Series]:
        if self.series:
            return self.series[0]
        return None

    def get_stats(self) -> Statistics:
        first_start = None
        last_end = None

        num_epochs = []

        for series in self.series:
            if "date" in series.data.columns:
                series_start = series.data.date.min()
                series_end = series.data.date.max()
            else:
                series_start = series.data.date_0.min()
                series_end = series.data.date_1.max()

            if first_start is None or first_start > series_start:
                first_start = series_start
            if last_end is None or last_end < series_end:
                last_end = series_end

            num_epochs.append(series.data.index.size)

        # first_start = min([series.data["date"].min() for series in self.series])
        # last_end = max([series.data["date"].max() for series in self.series])

        start = decimal_year_to_datetime(first_start)
        end = decimal_year_to_datetime(last_end)

        duration = end - start

        # mean_epochs = np.mean([series.data["date"].size for series in self.series])
        mean_epochs = np.mean(num_epochs)
        mean_interval = duration / mean_epochs

        return Statistics(start, end, duration, mean_interval)

    def sum_regions(self) -> None:
        """
        create series for all missing regions for which basin data
        are available
        """
        formats = {s.data_format for s in self}
        # groups = {s.basin_group for s in self if s != BasinGroup.GENERIC}
        groups = [BasinGroup.RIGNOT, BasinGroup.ZWALLY]
        sheets = [IceSheet.APIS, IceSheet.EAIS, IceSheet.WAIS, IceSheet.GRIS]

        for region, group, fmt in product(sheets, groups, formats):
            if self.get(format=fmt, basin_id=region) is None:

                new_series = self.sum_region(region, group, fmt)
                if new_series is not None:
                    self.series.append(new_series)

    def sum_region(
        self, region: IceSheet, basin_type: BasinGroup, data_format: str
    ) -> Series | None:
        """
        create series for region from summed basin if possible
        """
        basin_set = {
            BasinGroup.ZWALLY: REGIONS_ZWALLY,
            BasinGroup.RIGNOT: REGIONS_RIGNOT,
        }[basin_type][region]

        basins: list[Series] = []

        for basin in basin_set:
            series = self.get(format=data_format, basin_id=basin)

            if not series:
                return None

            basins.append(series)

        head, *tail = basins
        sum_data = head.data.copy()

        columns = head.data.columns

        t_column = "date_0" if "date_0" in columns else "date"
        data_columns = [colname for colname in columns if "date" not in colname]

        t = head.data[t_column].values

        for other in tail:
            t_other = other.data[t_column].values
            for colname in data_columns:
                sum_data[colname] += np.interp(t, t_other, other.data[colname].values)

        return Series(
            sum_data,
            data_format,
            head.contributor,
            head.experiment_group,
            region,
            BasinGroup.GENERIC,
            computed=True,
        )

    @classmethod
    def from_file(cls, source: Union[str, TextIO], schema: Schema) -> "Contribution":
        """
        read a contribution from a data file
        """
        username_column = schema.get_column("Username")
        experiment_group_column = schema.get_column("ExperimentGroup")

        column_headers = [column.name for column in schema.columns]

        data: pd.DataFrame = pd.read_csv(
            source,
            names=column_headers,
            comment="#",
            skipinitialspace=True,
            index_col=False,
        )
        # if "date_0" in column_headers:
        #     data["date"] = (data.date_0 + data.date_1) / 2
        header_skip_idx = 0

        unique_usernames = data[username_column.name].unique()

        if unique_usernames.size > 1:
            if data[username_column.name][1:].unique().size == 1:
                header_skip_idx = 1
            else:
                raise FormatError(
                    f"file contains multiple definitions for username: {list(unique_usernames)}"
                )
        username = data[username_column.name][header_skip_idx]

        unique_groups = data[experiment_group_column.name][header_skip_idx:].unique()
        if unique_groups.size > 1:
            raise FormatError(
                f"file contains multiple definitions for experiment group: {list(unique_groups)}"
            )
        experiment_group = ExperimentGroup.parse(
            data[experiment_group_column.name][header_skip_idx]
        )

        prop_columns = schema.get_property_columns()
        series = []

        property_combinations = product(
            *[data[col.name].unique() for col in prop_columns]
        )

        for combination in property_combinations:
            names = [col.name for col in prop_columns]

            row_filter = np.ones_like(data.index, dtype=np.bool8)

            for name, value in zip(names, combination):
                row_filter = np.logical_and(row_filter, data[name] == value)

            series_data: pd.DataFrame = data[row_filter].drop(columns=names)

            # if "date_0" in column_headers:
            #     rows, _ = series_data.shape
            #     series_data["date"] = series_data.date_0

            # if rows == 1:
            #     copy = series_data.copy()
            #     series_data["date"] = series_data.date_1
            #     series_data = pd.concat([series_data, copy], ignore_index=True)

            if not row_filter.any():
                continue

            attrs = {}
            for col, value in zip(prop_columns, combination):
                if col.type == "ExperimentGroup":
                    value = ExperimentGroup.parse(value)
                else:
                    attrs[col.name] = str(value)
                attrs[col.name] = value

            basin_id_name = schema.get_column("BasinID").name
            basin_group_name = schema.get_column("BasinGroup").name
            attrs[basin_group_name], attrs[basin_id_name] = parse_basin(
                attrs[basin_group_name], attrs[basin_id_name]
            )

            series.append(Series(series_data, data_format=schema.name, **attrs))

        return cls(username, experiment_group, series=series)
