from io import FileIO
from typing import Iterator
import numpy as np

from validator.const.severity import Severity
from validator.model.contribution import Contribution
from validator.model.message import Message
from validator.model.schema import Schema

INTERVAL_TOLERANCE = 1e-4


def validate_file(data_file: FileIO, schema: Schema) -> Iterator[Message]:
    """
    run validation checks on a file
    """
    try:
        contribution = Contribution.from_file(data_file, schema)
    except Exception as e:
        yield Message(Severity.error, "Could not read contribution", repr(e))
        return

    for series in contribution.series:
        for column in schema.get_data_columns():
            values = series.data[column.name].values

            if column.interval is not None:
                intervals = values[1:] - values[:-1]

                errors = np.abs(intervals - column.interval)
                if np.any(errors > INTERVAL_TOLERANCE):
                    yield Message(
                        Severity.error,
                        "Invalid data interval",
                        f'{series}: Column "{column.name}" does not match expected interval: {column.interval}',
                    )
            if column.unique and np.unique(values).size > 1:
                yield Message(
                    Severity.error,
                    "Multiple values in unique column",
                    f'{series}: Column "{column.name}" expects a single value per series',
                )
