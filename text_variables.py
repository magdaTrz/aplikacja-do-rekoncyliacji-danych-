from enum import Enum, auto
from typing import overload
from pydispatch import dispatcher

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
    def flow_lable_text() -> str:
        return f"Inicjalizacja klas do przetwarzania danych"
    @staticmethod
    def mapping_lable_text() -> str:
        return f"Przechodzę do mapowania pól danych"