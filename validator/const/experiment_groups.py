from enum import Enum


class ExperimentGroup(Enum):
    ra = "RA"
    gmb = "GMB"
    iom = "IOM"
    smb = "SMB"
    gia = "GIA"

    @property
    def full_name(self) -> str:
        return FULL_NAMES[self]

    @classmethod
    def parse(cls, string: str) -> "ExperimentGroup":
        string = string.upper()

        for value, name in FULL_NAMES.items():
            string_whitespace = string.replace("-", " ").replace("_", " ")
            if string_whitespace in name.upper():
                return value

        return cls(string)


FULL_NAMES = {
    ExperimentGroup.ra: "Radar Altimetry",
    ExperimentGroup.gmb: "Gravimetry",
    ExperimentGroup.iom: "Mass Budget",
    ExperimentGroup.gia: "Glacial Isostatic Adjustment",
    ExperimentGroup.smb: "Surface Mass Balance",
}
