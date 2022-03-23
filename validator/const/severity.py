from enum import Enum, IntEnum


class Severity(Enum):
    error = "error"
    warning = "warning"
    info = "info"


class ExitCode(IntEnum):
    ok = 0
    validation_failed = 10
