import pandas as pd
from dataclasses import dataclass

from validator.const.experiment_groups import ExperimentGroup


@dataclass(frozen=True)
class Series:
    """
    one data series from CSV data file
    """

    data: pd.DataFrame
    contributor: str
    experiment_group: ExperimentGroup
    basin_id: str
    basin_group: str
