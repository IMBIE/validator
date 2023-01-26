from enum import Enum


class ExperimentGroup(Enum):
    RA = "RA"
    GMB = "GMB"
    IOM = "IOM"
    SMB = "SMB"
    GIA = "GIA"

    @property
    def full_name(self) -> str:
        return FULL_NAMES[self]

    @classmethod
    def parse(cls, string: str) -> "ExperimentGroup":
        string = string.strip().upper()
        string_whitespace = string.replace("-", " ").replace("_", " ")

        for value, name in FULL_NAMES.items():
            if string_whitespace in name.upper():
                return value

        return cls(string)


FULL_NAMES = {
    ExperimentGroup.RA: "Radar Altimetry",
    ExperimentGroup.GMB: "Gravimetry",
    ExperimentGroup.IOM: "Mass Budget",
    ExperimentGroup.GIA: "Glacial Isostatic Adjustment",
    ExperimentGroup.SMB: "Surface Mass Balance",
}
