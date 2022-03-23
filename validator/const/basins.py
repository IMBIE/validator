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
    Z4_1 = "4.1"
    Z4_2 = "4.2"
    Z4_3 = "4.3"
    Z5_0 = "5.0"
    Z6_1 = "6.1"
    Z6_2 = "6.2"
    Z7_1 = "7.1"
    Z7_2 = "7.2"
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
    CS = "CW"
    NW = "NW"


class IceSheet(BasinID):
    APIS = "APIS"
    WAIS = "WAIS"
    EAIS = "EAIS"
    GRIS = "GRIS"
    AIS = "AIS"
    ALL = "ALL"


def parse_basin(group: str, basin: str) -> Tuple[BasinGroup, BasinID]:
    try:
        basin: BasinID = IceSheet.parse(basin)
    except ValueError:
        group: BasinGroup = BasinGroup.parse(group)
        _type = group.basins_type()

        return group, _type.parse(basin)
    else:
        return BasinGroup.GENERIC, basin
