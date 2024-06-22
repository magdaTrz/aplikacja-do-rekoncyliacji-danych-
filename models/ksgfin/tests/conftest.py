import pandas
from pytest import fixture
from models.ksgfin.salda_fin import SaldaFin
from text_variables import TextEnum


@fixture
def src_dataframe_before_convert():
    return pandas.DataFrame({
            'rachunek': [123, 456, 789],
            'konto': ['A', 'B', 'C'],
            'subkonto': ['X', 'Y', 'Z'],
            'subkonto_pdst': ['N', 'N', 'T'],
            'spw_r': ['1', '2', '3'],
            'waluta': ['USD', 'EUR', 'GBP'],
            'czy_saldo_wn': ['T', 'N', 'T'],
            'saldo': [100.0, -50.0, 200.0],
            'nr_swiadectwa_Maestro': ['123', '456', None],
            'kod_papieru_Maestro': ['P123', None, 'P789'],
            'czy_konto_pdst_klienta': ['T', 'N', 'T'],
            'rach_13': [123, 456, 789],
            'konto_13': ['A', 'B', 'C'],
            'subkonto_13': ['X', 'Y', 'Z'],
            'strona_13': ['WN', 'MA', 'WN'],
        })

@fixture
def _dataframe():
    return pandas.DataFrame({
            'rachunek': [123, 456, 789],
            'konto': ['A', 'B', 'C'],
            'subkonto': ['X', 'Y', 'Z'],
            'waluta': ['USD', 'EUR', 'GBP'],
            'czy_saldo_wn': ['T', 'F', 'T'],
            'saldo': [100.0, -50.0, 200.0],
            'czy_konto_pdst_klienta': ['T', 'N', 'T'],
            'rach_13': [123, 456, 789],
            'konto_13': ['A', 'B', 'C'],
            'subkonto_13': ['X', 'Y', 'Z'],
            'strona_13': ['WN', 'MA', 'WN'],
        })

@fixture
def ksgfin_load():
    return SaldaFin(
        stage=TextEnum.LOAD
    )
