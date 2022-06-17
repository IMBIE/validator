from dataclasses import dataclass, field
from optparse import Option
from typing import List, Optional, TextIO, Union
import pandas as pd
import numpy as np
from itertools import product
from validator.const.basins import BasinGroup, BasinID, parse_basin
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

    def first(self) -> Optional[Series]:
        if self.series:
            return self.series[0]
        return None

    def get_stats(self) -> Statistics:
        first_start = min([series.data["date"].min() for series in self.series])
        last_end = max([series.data["date"].max() for series in self.series])

        start = decimal_year_to_datetime(first_start)
        end = decimal_year_to_datetime(last_end)

        duration = end - start

        mean_epochs = np.mean([series.data["date"].size for series in self.series])
        mean_interval = duration / mean_epochs

        return Statistics(start, end, duration, mean_interval)

    @classmethod
    def from_file(cls, source: Union[str, TextIO], schema: Schema) -> "Contribution":
        """
        read a contribution from a data file
        """
        username_column = schema.get_column("Username")
        experiment_group_column = schema.get_column("ExperimentGroup")

        column_headers = [column.name for column in schema.columns]

        data: pd.DataFrame = pd.read_csv(
            source, names=column_headers, comment="#", skipinitialspace=True
        )
        header_skip_idx = 0

        if data[username_column.name].unique().size > 1:
            if data[username_column.name][1:].unique().size == 1:
                header_skip_idx = 1
            else:
                raise FormatError("file contains multiple definitions for username")
        username = data[username_column.name][header_skip_idx]

        if data[experiment_group_column.name][header_skip_idx:].unique().size > 1:
            raise FormatError("file contains multiple definitions for experiment group")
        experiment_group = data[experiment_group_column.name][header_skip_idx]

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

            if not row_filter.any():
                continue

            attrs = {}
            for col, value in zip(prop_columns, combination):
                if col.type == "ExperimentGroup":
                    value = ExperimentGroup.parse(value)
                attrs[col.name] = value

            basin_id_name = schema.get_column("BasinID").name
            basin_group_name = schema.get_column("BasinGroup").name
            attrs[basin_group_name], attrs[basin_id_name] = parse_basin(
                attrs[basin_group_name], attrs[basin_id_name]
            )

            series.append(Series(series_data, data_format=schema.name, **attrs))

        return cls(username, experiment_group, series=series)
