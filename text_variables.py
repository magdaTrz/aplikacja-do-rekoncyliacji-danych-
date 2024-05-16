from enum import Enum, auto
from typing import overload


class TextEnum(Enum):
    LOAD = auto()
    END = auto()

    KOI = auto()
    UMO = auto()
    KSGPW = auto()
    KSGFIN = auto()
    MATE = auto()

    SAVE_ERROR = auto()
    CREATE_ERROR = auto()
    EXCEL_ERROR = auto()

    def __str__(self):
        return self.name


class TextGenerator:
    @staticmethod
    def report_lable_text(arg1: str) -> str:
        return f"Przechodzę do raportu {arg1}"

    @staticmethod
    def flow_lable_text() -> str:
        return f"Inicjuję klasę"
    @staticmethod
    def mapping_lable_text() -> str:
        return f"Przechodzę do mapowania pól"

    @staticmethod
    def report_lable_text() -> str:
        return f"Tworzę i zapisuję rapot"