from dataclasses import dataclass
from typing import Dict

from ..const.severity import Severity


@dataclass(frozen=True)
class Message:
    severity: Severity
    title: str
    description: str = None

    def to_json(self) -> Dict[str, str]:
        _dict = {"severity": self.severity.value, "title": self.title}
        if self.description is not None:
            _dict["description"] = self.description

        return _dict
