from enum import Enum
from typing import Tuple


class BasinGroup(Enum):
    GENERIC = "GENERIC"
    ZWALLY = "ZWALLY"
    RIGNOT = "RIGNOT"

    @classmethod
    def parse(cls, string: str) -> "BasinGroup":
        return cls(string.strip().upper())

    def basins_type(self) -> "BasinID":
        types = {BasinGroup.ZWALLY: ZwallyBasin, BasinGroup.RIGNOT: RignotBasin}
        if self in types:
            return types[self]
        return IceSheet


class BasinID(Enum):
    @classmethod
    def parse(cls, string: str) -> "BasinID":
        return cls(string.strip().upper())


class ZwallyBasin(BasinID):
    Z1 = "1"
    Z2 = "2"
    Z3 = "3"
    Z4 = "4"
    Z5 = "5"
    Z6 = "6"
    Z7 = "7"
    Z8 = "8"
    Z9 = "9"
    Z10 = "10"
    Z11 = "11"
    Z12 = "12"
    Z13 = "13"
    Z14 = "14"
    Z15 = "15"
    Z16 = "16"
    Z17 = "17"
    Z18 = "18"
    Z19 = "19"
    Z20 = "20"
    Z21 = "21"
    Z22 = "22"
    Z23 = "23"
    Z24 = "24"
    Z25 = "25"
    Z26 = "26"
    Z27 = "27"
    Z1_1 = "1.1"
    Z1_2 = "1.2"
    Z1_3 = "1.3"
    Z1_4 = "1.4"
    Z2_1 = "2.1"
    Z2_2 = "2.2"
    Z3_1 = "3.1"
    Z3_2 = "3.2"
    Z3_3 = "3.3"
    Z4_0 = "4.0"  # basin 4.0: may need to remove this
    Z4_1 = "4.1"
    Z4_2 = "4.2"
    Z4_3 = "4.3"
    Z5_0 = "5.0"
    Z6_0 = "6.0"  # basin 6.0: may need to remove this
    Z6_1 = "6.1"
    Z6_2 = "6.2"
    Z7_0 = "7.0"  # basin 7.0: may need to remove this
    Z7_1 = "7.1"
    Z7_2 = "7.2"
    Z8_0 = "8.0"  # basin 8.0: may need to remove this
    Z8_1 = "8.1"
    Z8_2 = "8.2"


class RignotBasin(BasinID):
    I_IPP = "I-IPP"
    IPP_J = "IPP-J"
    HP_I = "HP-I"
    H_HP = "H-HP"
    G_H = "G-H"
    J_JPP = "J-JPP"
    EP_F = "EP-F"
    F_G = "F-G"
    K_A = "K-A"
    A_AP = "A-AP"
    AP_B = "AP-B"
    JPP_K = "JPP-K"
    B_C = "B-C"
    E_EP = "E-EP"
    CP_D = "CP-D"
    C_CP = "C-CP"
    DP_E = "DP-E"
    D_DP = "D-DP"
    NO = "NO"
    NE = "NE"
    SE = "SE"
    SW = "SW"
    CW = "CW"
    NW = "NW"


class IceSheet(BasinID):
    APIS = "APIS"
    WAIS = "WAIS"
    EAIS = "EAIS"
    GRIS = "GRIS"
    AIS = "AIS"
    ALL = "ALL"

    @classmethod
    def parse(cls, value: str) -> "IceSheet":
        value = value.strip().upper()

        if value == "GIS":
            return cls.GRIS
        for sheet in cls:
            if sheet.value.startswith(value):
                return sheet

        raise ValueError(f"unknown ice sheet: '{value}'")


def parse_basin(group: str, basin: str) -> Tuple[BasinGroup, BasinID]:
    from validator.model.contribution import FormatError

    basin = str(basin)

    try:
        basin_enum: BasinID = IceSheet.parse(basin)
    except ValueError:
        group: BasinGroup = BasinGroup.parse(group)
        _type = group.basins_type()

        try:
            return group, _type.parse(basin)
        except ValueError:
            raise FormatError(f"unknown {group} basin: '{basin}'")
    else:
        return BasinGroup.GENERIC, basin_enum


REGIONS_ZWALLY: dict[IceSheet, list[ZwallyBasin]] = {
    IceSheet.APIS: [
        ZwallyBasin.Z24,
        ZwallyBasin.Z25,
        ZwallyBasin.Z26,
        ZwallyBasin.Z27,
    ],
    IceSheet.EAIS: [
        ZwallyBasin.Z2,
        ZwallyBasin.Z3,
        ZwallyBasin.Z4,
        ZwallyBasin.Z5,
        ZwallyBasin.Z6,
        ZwallyBasin.Z7,
        ZwallyBasin.Z8,
        ZwallyBasin.Z9,
        ZwallyBasin.Z10,
        ZwallyBasin.Z11,
        ZwallyBasin.Z12,
        ZwallyBasin.Z13,
        ZwallyBasin.Z14,
        ZwallyBasin.Z15,
        ZwallyBasin.Z16,
        ZwallyBasin.Z17,
    ],
    IceSheet.WAIS: [
        ZwallyBasin.Z1,
        ZwallyBasin.Z18,
        ZwallyBasin.Z19,
        ZwallyBasin.Z20,
        ZwallyBasin.Z21,
        ZwallyBasin.Z22,
        ZwallyBasin.Z23,
    ],
    IceSheet.GRIS: [
        ZwallyBasin.Z1_1,
        ZwallyBasin.Z1_2,
        ZwallyBasin.Z1_3,
        ZwallyBasin.Z1_4,
        ZwallyBasin.Z2_1,
        ZwallyBasin.Z2_2,
        ZwallyBasin.Z3_1,
        ZwallyBasin.Z3_2,
        ZwallyBasin.Z3_3,
        ZwallyBasin.Z4_1,
        ZwallyBasin.Z4_2,
        ZwallyBasin.Z4_3,
        ZwallyBasin.Z5_0,
        ZwallyBasin.Z6_1,
        ZwallyBasin.Z6_2,
        ZwallyBasin.Z7_1,
        ZwallyBasin.Z7_2,
        ZwallyBasin.Z8_1,
        ZwallyBasin.Z8_2,
    ],
}
REGIONS_RIGNOT: dict[IceSheet, list[RignotBasin]] = {
    IceSheet.APIS: [RignotBasin.I_IPP, RignotBasin.IPP_J, RignotBasin.HP_I],
    IceSheet.EAIS: [
        RignotBasin.JPP_K,
        RignotBasin.K_A,
        RignotBasin.A_AP,
        RignotBasin.AP_B,
        RignotBasin.B_C,
        RignotBasin.C_CP,
        RignotBasin.CP_D,
        RignotBasin.D_DP,
        RignotBasin.DP_E,
        RignotBasin.E_EP,
    ],
    IceSheet.WAIS: [
        RignotBasin.J_JPP,
        RignotBasin.EP_F,
        RignotBasin.G_H,
        RignotBasin.F_G,
        RignotBasin.H_HP,
    ],
    IceSheet.GRIS: [
        RignotBasin.NO,
        RignotBasin.NE,
        RignotBasin.SE,
        RignotBasin.SW,
        RignotBasin.CW,
        RignotBasin.NW,
    ],
}
