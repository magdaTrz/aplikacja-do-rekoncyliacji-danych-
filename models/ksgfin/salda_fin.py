import os

import numpy
import pandas

from pydispatch import dispatcher

from models.dict_update import DictUpdate
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class SaldaFin(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path='',
                 save_folder_report_path='', path_excel_file='report.xlsx', password=None):
        super().__init__()
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.data_folder_report_path: str = data_folder_report_path
        self.save_folder_report_path: str = save_folder_report_path
        self.path_excel: str = path_excel_file
        self.dataframe_src: pandas.DataFrame | None = None
        self.dataframe_ext: pandas.DataFrame | None = None
        self.dataframe_tgt: pandas.DataFrame | None = None
        self.summary_dataframe: pandas.DataFrame | None = None
        self.merge_statistics_dataframe: pandas.DataFrame | None = None
        self.percent_reconciliation_dataframe: pandas.DataFrame | None = None
        self.sample_dataframe: pandas.DataFrame | None = None
        self.password: None | str = password

    def _carry_operations(self) -> bool:
        print(f'SaldaFin: _carry_operations(stage={self.stage})')

        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names(
            {0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto', 4: 'waluta', 5: 'czy_saldo_wn',
             6: 'saldo', 7: 'rach_13', 8: 'konto_13', 9: 'subkonto_13', 10: 'strona_13'},
            ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto',
                                                  4: 'subkonto_pdst', 5: 'spw_r', 6: 'waluta', 7: 'czy_saldo_wn',
                                                  8: 'saldo', 9: 'rach_13', 10: 'konto_13', 11: 'subkonto_13',
                                                  12: 'strona_13', 13: 'nr_swiadectwa_Maestro',
                                                  14: 'kod_papieru_Maestro'},
                                                 src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe)
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names(
                {0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto', 4: 'waluta', 5: 'czy_saldo_wn',
                 6: 'saldo', 7: 'rach_13', 8: 'konto_13', 9: 'subkonto_13', 10: 'strona_13'},
                tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return False
            else:
                self.dataframe_ext = self.convert_ext(ext_dataframe, is_eod=True)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    @staticmethod
    def convert_src(dataframe: pandas.DataFrame) -> pandas.DataFrame:

        def cols_mapping(row, column_to_map, col1_fill, col2_fill, mapping_dict):
            key = row[column_to_map]
            if key in mapping_dict:
                values = mapping_dict[key]
                row[col1_fill] = values[0]
                row[col2_fill] = values[1]
            elif key is None:
                pass
            else:
                row[col1_fill] = row[col1_fill]
                row[col2_fill] = row[col2_fill]
            return row

        def map_values_to_columns(dataframe, column_to_map, col1_fill, col2_fill, map_dict) -> pandas.DataFrame:
            return dataframe.apply(cols_mapping, args=(column_to_map, col1_fill, col2_fill), axis=1,
                                   mapping_dict=map_dict)

        dict_update = DictUpdate()

        dataframe['key_three'] = None
        dataframe['key_four'] = None

        try:
            dataframe['czy_sponsor'] = dataframe.apply(
                lambda row: 'T' if str(row['nr_swiadectwa_Maestro']).lstrip('0') != str(row['rachunek']) else 'F',
                axis=1)
            dataframe.loc[dataframe['czy_sponsor'] == 'F', ['nr_swiadectwa_Maestro', 'kod_papieru_Maestro']] = None
        except Exception as e:
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Błąd kolumn pomocniczych: ['nr_swiadectwa_Maestro',kod_papieru_Maestro'] {e}",
                            head='error')
        dict_konto_fin = [konto for konto in dict_update.get_dict_konto_fin()]
        dataframe['konto_Maestro'] = dataframe['konto']
        dataframe['subkonto_Maestro'] = dataframe['subkonto']
        dataframe['subkonto_pdst_Maestro'] = dataframe['subkonto_pdst']
        dataframe['spw_r_Maestro'] = dataframe['spw_r']

        condition = dataframe['konto'].isin(dict_konto_fin)
        dataframe.loc[:, 'subkonto'] = dataframe.loc[:, 'subkonto'].astype(str).str.lstrip('0')
        dataframe.loc[:, 'subkonto_pdst'] = dataframe.loc[:, 'subkonto_pdst'].astype(str).str.lstrip('0')

        dataframe.loc[condition, 'key_four'] = dataframe['konto'].astype(str) + dataframe['subkonto'].astype(str) + dataframe['subkonto_pdst'].astype(str) + dataframe['spw_r'].astype(str)
        dataframe.loc[~condition, 'key_three'] = dataframe['konto'].astype(str) + dataframe['subkonto'].astype(str) \
                                                 + dataframe['subkonto_pdst'].astype(str)
        condition_2 = (dataframe['konto'] == 139)
        condition_3 = (dataframe['subkonto'].isin(['23', '24', '25', '26', '27', '22']))
        dataframe.loc[(condition_2 & condition_3), 'key_three'] = \
            dataframe['konto'].astype(str) + dataframe['subkonto'].astype(str) + dataframe['subkonto_pdst'].astype(str)

        dataframe = map_values_to_columns(dataframe, 'key_three', 'konto', 'subkonto',
                                          dict_update.get_dict_konto_subkonto())
        dataframe = map_values_to_columns(dataframe, 'key_four', 'konto', 'subkonto',
                                          dict_update.get_dict_spwr_konto_subkonto())

        del dataframe['key_three']
        del dataframe['key_four']
        return dataframe[
            ['rachunek', 'konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro',
             'spw_r_Maestro', 'nr_swiadectwa_Maestro', 'kod_papieru_Maestro', 'czy_saldo_wn', 'czy_konto_pdst_klienta',
             'saldo', 'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame, is_eod=False) -> pandas.DataFrame:
        dataframe.loc[:, 'konto'] = dataframe.loc[:, 'konto'].astype(str)
        dataframe.loc[:, 'subkonto'] = dataframe.loc[:, 'subkonto'].astype(str).str.lstrip('0')
        if is_eod:
            con_1 = (dataframe['subkonto'] == '80100')
            con_2 = (dataframe['saldo'] < 0)
            dataframe.loc[(con_1 & con_2), 'subkonto'] = '80200'
        return dataframe[['rachunek', 'konto', 'subkonto', 'waluta', 'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo',
                          'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'konto'] = dataframe.loc[:, 'konto'].astype(str)
        dataframe.loc[:, 'subkonto'] = dataframe.loc[:, 'subkonto'].astype(str)
        dataframe.loc[:, 'konto'] = dataframe['konto'].apply(lambda x: x.replace('.0', ''))
        dataframe.loc[:, 'subkonto'] = dataframe['subkonto'].apply(lambda x: x.replace('.0', ''))
        dataframe.loc[:, 'subkonto'] = dataframe.loc[:, 'subkonto'].str.lstrip('0')
        return dataframe[['rachunek', 'konto', 'subkonto', 'waluta', 'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo',
                          'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]

    @staticmethod
    def prepare_dataframe_waluta_saldo(dataframe_1: pandas.DataFrame,
                                       dataframe_2: pandas.DataFrame,
                                       is_eod=False) -> pandas.DataFrame:
        if is_eod:
            balance_accounts = ['24504', '24505', '24506', '24507', '24508']
            '''Raport waluta|konto|saldo'''
            waluta_df_ext = dataframe_1[['waluta', 'konto', 'saldo']].copy()
            waluta_df_tgt = dataframe_2[['waluta', 'konto', 'saldo']].copy()
            waluta_df_tgt = waluta_df_tgt[~waluta_df_tgt['konto'].isin(balance_accounts)]
            waluta_df_ext = waluta_df_ext.groupby(['waluta'], as_index=False)['saldo'].sum()
            waluta_df_tgt = waluta_df_tgt.groupby(['waluta'], as_index=False)['saldo'].sum()
            return [waluta_df_ext, waluta_df_tgt]
        else:
            '''Raport waluta|saldo'''
            converted_src = dataframe_1[['rachunek', 'konto', 'subkonto', 'waluta', 'czy_konto_pdst_klienta', 'saldo',
                                         'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]
            converted_ext = dataframe_2
            waluta_df_src = converted_src[['waluta', 'saldo']].copy()
            waluta_df_ext = converted_ext[['waluta', 'saldo']].copy()
            waluta_df_src = waluta_df_src.groupby(['waluta'], as_index=False)['saldo'].sum()
            waluta_df_ext = waluta_df_ext.groupby(['waluta'], as_index=False)['saldo'].sum()
            return [waluta_df_src, waluta_df_ext]

    @staticmethod
    def prepare_dataframe_detail(dataframe_1: pandas.DataFrame,
                                 dataframe_2: pandas.DataFrame,
                                 is_eod=False) -> pandas.DataFrame:
        if is_eod:
            balance_accounts = ['24504', '24505', '24506', '24507', '24508']
            saldo_df_ext = dataframe_1.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'],
                as_index=False)['saldo'].sum()
            saldo_df_tgt = dataframe_2.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'],
                as_index=False)['saldo'].sum()
            pandas.set_option('display.float_format', '{:.2f}'.format)
            saldo_df_ext = saldo_df_ext.astype({'konto': str, 'subkonto': str})
            saldo_df_tgt = saldo_df_tgt.astype({'konto': str, 'subkonto': str})
            saldo_df_tgt = saldo_df_tgt[~saldo_df_tgt['konto'].isin(balance_accounts)]
            return [saldo_df_ext, saldo_df_tgt]
        else:
            '''Raport oznaczeniaMaestro'''
            saldo_df_src = dataframe_1.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'], as_index=False).agg({
                'saldo': 'sum',
                'konto_Maestro': 'first',
                'subkonto_Maestro': 'first',
                'subkonto_pdst_Maestro': 'first',
                'spw_r_Maestro': 'first',
                'nr_swiadectwa_Maestro': 'first',
                'kod_papieru_Maestro': 'first'
            })
            saldo_df_ext = dataframe_2.groupby(['rachunek', 'konto', 'subkonto', 'waluta'],
                                               as_index=False)['saldo'].sum()

            pandas.set_option('display.float_format', '{:.2f}'.format)
            saldo_df_src = saldo_df_src.astype({'konto': str, 'subkonto': str})
            saldo_df_ext = saldo_df_ext.astype({'konto': str, 'subkonto': str})
            return [saldo_df_src, saldo_df_ext]

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"SaldaFin(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"SaldaFin(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                dataframes_waluta = self.prepare_dataframe_waluta_saldo(self.dataframe_src, self.dataframe_ext)
                raport_waluta = excel_workbook.create_f2f_report(
                    dataframe_1=dataframes_waluta[0],
                    dataframe_2=dataframes_waluta[1],
                    merge_on_cols=["waluta"],
                    compare_cols=["saldo"],
                    text_description="Raport sprawdzający sumę sald pogrupowaną według waluty.")
                dataframes_detail = self.prepare_dataframe_detail(self.dataframe_src, self.dataframe_ext)
                raport_detail = excel_workbook.create_f2f_report(
                    dataframe_1=dataframes_detail[0],
                    dataframe_2=dataframes_detail[1],
                    merge_on_cols=['rachunek', 'konto', 'subkonto', 'waluta'],
                    compare_cols=["saldo"],
                    text_description="Zestawienie zawartości kartoteki kont finansowych."
                )
            elif self.stage == TextEnum.END:
                dataframes_waluta = self.prepare_dataframe_waluta_saldo(self.dataframe_ext, self.dataframe_tgt,
                                                                        is_eod=True)
                raport_waluta = excel_workbook.create_f2f_report(
                    dataframe_1=dataframes_waluta[0],
                    dataframe_2=dataframes_waluta[1],
                    merge_on_cols=["waluta"],
                    compare_cols=["saldo"],
                    text_description="Raport sprawdzający sumę sald pogrupowaną według waluty.")
                dataframes_detail = self.prepare_dataframe_detail(self.dataframe_ext, self.dataframe_tgt, is_eod=True)
                raport_detail = excel_workbook.create_f2f_report(
                    dataframe_1=dataframes_detail[0],
                    dataframe_2=dataframes_detail[1],
                    merge_on_cols=['rachunek', 'konto', 'subkonto', 'waluta'],
                    compare_cols=["saldo"],
                    text_description="Zestawienie zawartości kartoteki kont finansowych."
                )
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"SaldaFin(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"sum_waluta_salda": raport_waluta, f"sum_rach_klient_sald": raport_detail},
                                         merge_on=['rachunek', 'konto', 'subkonto', 'waluta'])
        except Exception as e:
            print(f"SaldaFin(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"SaldaFin(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True
