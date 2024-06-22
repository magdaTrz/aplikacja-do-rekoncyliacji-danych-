from unittest.mock import MagicMock

import pandas
import pandas as pd
import pytest

from models.ksgfin.salda_fin import SaldaFin
from text_variables import TextEnum


class TestSaldaFin:

    @pytest.fixture(autouse=True)
    def setup_salda_fin(self):
        self.salda_fin = SaldaFin(stage=TextEnum.LOAD,
                                  path_src='test_salda_fin_src.txt',
                                  path_ext='test_out_salda_fin_ext.csv',
                                  path_tgt='test_salda_fin_tgt.csv',
                                  data_folder_report_path='data/',
                                  save_folder_report_path='output/',
                                  path_excel_file='test_report.xlsx',
                                  password='test_password')

    def test_convert_src(self, src_dataframe_before_convert: pandas.DataFrame):
        src_dataframe = src_dataframe_before_convert
        self.salda_fin.make_dataframe_from_file = MagicMock(return_value=src_dataframe)
        self.salda_fin.set_colum_names = MagicMock(return_value=src_dataframe)

        result = self.salda_fin.convert_src(src_dataframe)
        expected_columns = [
            'rachunek', 'konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro',
            'subkonto_pdst_Maestro', 'spw_r_Maestro', 'nr_swiadectwa_Maestro', 'kod_papieru_Maestro',
            'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo', 'rach_13', 'konto_13', 'subkonto_13', 'strona_13'
        ]

        assert list(result.columns) == expected_columns
        assert len(result) == len(src_dataframe)

    def test_convert_ext(self, _dataframe: pandas.DataFrame):
        ext_dataframe = _dataframe

        result = self.salda_fin.convert_ext(ext_dataframe)
        expected_columns = [
            'rachunek', 'konto', 'subkonto', 'waluta', 'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo',
            'rach_13', 'konto_13', 'subkonto_13', 'strona_13'
        ]

        assert list(result.columns) == expected_columns
        assert len(result) == len(ext_dataframe)

    def test_convert_tgt(self, _dataframe: pandas.DataFrame):
        tgt_dataframe = _dataframe

        result = self.salda_fin.convert_tgt(tgt_dataframe)
        expected_columns = [
            'rachunek', 'konto', 'subkonto', 'waluta', 'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo',
            'rach_13', 'konto_13', 'subkonto_13', 'strona_13'
        ]

        assert list(result.columns) == expected_columns
        assert len(result) == len(tgt_dataframe)

    def test_prepare_dataframe_waluta_saldo_load_stage(self, _dataframe: pandas.DataFrame):
        self.salda_fin.dataframe_src = _dataframe
        self.salda_fin.dataframe_ext = _dataframe
        result = self.salda_fin.prepare_dataframe_waluta_saldo(self.salda_fin.dataframe_src,
                                                               self.salda_fin.dataframe_ext)

        assert len(result) == 2
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], pd.DataFrame)

    def test_prepare_dataframe_detail_end_stage(self, _dataframe: pandas.DataFrame):
        self.salda_fin.dataframe_ext = _dataframe
        self.salda_fin.dataframe_tgt = _dataframe
        result = self.salda_fin.prepare_dataframe_detail(self.salda_fin.dataframe_ext,
                                                         self.salda_fin.dataframe_tgt, is_eod=True)

        assert len(result) == 2
        assert isinstance(result[0], pd.DataFrame)
        assert isinstance(result[1], pd.DataFrame)
