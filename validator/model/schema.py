from dataclasses import dataclass
import io
import yaml
from typing import Any, Dict, List, Union


def parse_interval(value: Union[str, float] = None) -> float:
    if isinstance(value, str):
        return {"monthly": 1 / 12, "yearly": 1.0}[value]
    return value


@dataclass(frozen=True)
class ColumnRule:
    name: str
    type: str
    description: str = None
    unique: bool = False
    property: bool = False
    interval: float = None


@dataclass(frozen=True)
class Schema:
    name: str
    columns: List[ColumnRule]
    description: str = None

    def get_property_columns(self) -> List[ColumnRule]:
        return [col for col in self.columns if col.property]

    def get_data_columns(self) -> List[ColumnRule]:
        return [col for col in self.columns if not col.property]

    def get_column(self, _type: str) -> ColumnRule:
        for col in self.columns:
            if col.type == _type:
                return col
        raise ValueError(f"no column found with type '{_type}'")

    @staticmethod
    def parse_props(**props: Any) -> Dict[str, Any]:
        return {
            key: value if key != "interval" else parse_interval(value)
            for key, value in props.items()
        }

    @classmethod
    def from_file(cls, file: io.StringIO, format_name: str) -> "Schema":
        """
        load a schema from a yml file
        """
        from validator.data.loader import Loader

        data = yaml.load(file, Loader)
        for entry in data:
            if entry.name == format_name:
                return entry

        raise KeyError(f"no such format defined in schema: '{format_name}'")
