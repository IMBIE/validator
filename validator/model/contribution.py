from dataclasses import dataclass, field
from typing import List, TextIO, Union
import pandas as pd
import numpy as np
from itertools import product
from validator.const.basins import parse_basin

from validator.model.schema import Schema
from .series import Series

from ..const.experiment_groups import ExperimentGroup


@dataclass(frozen=True)
class Contribution:
    username: str
    experiment_group: ExperimentGroup
    series: List[Series] = field(default_factory=list)

    @classmethod
    def from_file(cls, source: Union[str, TextIO], schema: Schema) -> "Contribution":
        """
        read a contribution from a data file
        """
        column_headers = [column.name for column in schema.columns]

        data: pd.DataFrame = pd.read_csv(source, names=column_headers, comment="#")

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
                attrs[basin_group_name].strip(), attrs[basin_id_name].strip()
            )

            series.append(Series(series_data, **attrs))

        username_column = schema.get_column("Username")
        experiment_group_column = schema.get_column("ExperimentGroup")

        return cls(
            attrs[username_column.name], attrs[experiment_group_column.name], series
        )
