from enum import Enum


class ExperimentGroup(Enum):
    ra = "RA"
    gmb = "GMB"
    iom = "IOM"

    @property
    def full_name(self) -> str:
        return FULL_NAMES[self]

    @classmethod
    def parse(cls, string: str) -> "ExperimentGroup":
        string = string.strip().upper()

        for value, name in FULL_NAMES.items():
            if string in name.upper():
                return value

        return cls(string)


FULL_NAMES = {
    ExperimentGroup.ra: "Radar Altimetry",
    ExperimentGroup.gmb: "Gravimetry",
    ExperimentGroup.iom: "Mass Balance",
}
