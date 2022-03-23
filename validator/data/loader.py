from typing import Any, Dict
import yaml

from validator.model.schema import ColumnRule, Schema, parse_interval


class Loader(yaml.SafeLoader):
    """
    custom loader class for schema files
    """


def construct_schema(loader: Loader, node: yaml.Node) -> Schema:
    """
    build schema object from YAML node
    """
    elems = loader.construct_mapping(node, deep=True)

    return Schema(
        name=elems["name"],
        columns=[construct_column_rule(el) for el in elems["columns"]],
        description=elems.get("description"),
    )


def construct_column_rule(node: Dict[str, Any]) -> ColumnRule:
    """
    create a column rule from YAML mapping
    """
    return ColumnRule(
        node["name"],
        node["type"],
        node.get("description"),
        node.get("unique", False),
        node.get("property", False),
        parse_interval(node.get("interval")),
    )


Loader.add_constructor("!schema", construct_schema)
