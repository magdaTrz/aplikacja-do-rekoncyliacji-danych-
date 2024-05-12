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
    def report_lable_text(arg1: str, arg2:str | None = None) -> str:
        return f"Wygenerowano {arg1} raport {arg2}" if arg2 else f"Stworzono {arg1}"