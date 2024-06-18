import os

import numpy
import pandas

from pydispatch import dispatcher

from models.dict_update import DictUpdate
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.koi import dict_KOI
from models.report_model import ReportModel
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class SaldaPw(ReportModel):
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
        print(f'SaldaPw: _carry_operations(stage={self.stage})')
        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names(
            {0: 'rachunek', 1: 'kod_papieru', 2: 'id_depozyt', 3: 'gielda', 4: 'status_aktyw',
             5: 'klasa_konta', 6: 'id_konta', 7: 'saldo'}, ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: 'rachunek', 1: 'kod_papieru', 2: 'gielda', 3: 'id_depozyt', 4: 'nr_konta',
                            5: 'kod_produktu', 6: 'id_konta', 7: 'saldo'}, src_dataframe)

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
                {0: 'rachunek', 1: 'kod_papieru', 2: 'id_depozyt', 3: 'gielda', 4: 'status_aktyw',
                 5: 'klasa_konta', 6: 'id_konta', 7: 'saldo'}, tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return False
            else:
                self.dataframe_ext = self.convert_ext(ext_dataframe, is_eod=True)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    @staticmethod
    def convert_src(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        def cols_mapping(row, column_to_map, col1_to_fill, col2_to_fill, col3_to_fill, mapping_dict):
            key = row[column_to_map]
            if key in mapping_dict:
                values = mapping_dict[key]
                try:
                    row[col1_to_fill] = values[0]
                    row[col2_to_fill] = values[1]
                    row[col3_to_fill] = values[2]
                except IndexError:
                    row[col1_to_fill] = values[0]
                    row[col2_to_fill] = values[1]
            elif key is None:
                pass
            else:
                row[col1_to_fill] = '-'
                row[col2_to_fill] = '-'
                if col3_to_fill is not None:
                    row[col3_to_fill] = '-'
            return row

        def map_values_to_columns(dataframe, column_to_map, col1_to_fill, col2_to_fill, map_dict, col3_to_fill=None):
            return dataframe.apply(cols_mapping, args=(column_to_map, col1_to_fill, col2_to_fill, col3_to_fill), axis=1,
                                   mapping_dict=map_dict)

        dataframe = dataframe.astype({'rachunek': str, 'nr_konta': str})

        dict_update = DictUpdate()

        dataframe.loc[:, 'kod_produktu'] = dataframe.loc[:, 'kod_produktu'].str.lower()
        dataframe.loc[:, 'nr_konta'] = dataframe.loc[:, 'nr_konta'].str.lower()
        dataframe['key_two'] = None
        dataframe['key_three'] = None

        dataframe = map_values_to_columns(dataframe, 'id_depozyt', 'gielda', 'id_depozyt',
                                          dict_update.get_dict_gielda_depozyt())

        dict_rachunki_str = [str(rachunek) for rachunek in dict_update.get_dict_rachunki()]
        condition = dataframe['rachunek'].isin(dict_rachunki_str)
        print(f"   Rachunki zamieniane na '13': {dict_rachunki_str}")

        dataframe.loc[condition, 'key_three'] = dataframe['rachunek'].astype(str) + dataframe['nr_konta'].astype(str) \
                                                + dataframe['kod_produktu'].astype(str)
        dataframe.loc[~condition, 'key_two'] = dataframe['nr_konta'].astype(str) + dataframe['kod_produktu'].astype(str)

        dataframe['klasa_konta'] = None
        dataframe['status_aktyw'] = None

        dataframe = map_values_to_columns(dataframe, 'key_two', 'klasa_konta', 'status_aktyw',
                                          dict_update.get_dict_klasa_konta_status_aktyw())
        dataframe = map_values_to_columns(dataframe, 'key_three', 'rachunek', 'klasa_konta',
                                          dict_update.get_dict_rachunek_klasa_konta_status_aktyw(),
                                          'status_aktyw')
        del dataframe['key_three']
        del dataframe['key_two']
        dataframe['rachunek_maestro'] = dataframe['rachunek']
        dataframe.loc[dataframe['rachunek'].str.len() < 8, 'rachunek'] = '13'
        dataframe['key_two'] = None
        dataframe.loc[dataframe['klasa_konta'] == 'nan', 'key_two'] = dataframe['nr_konta'].astype(str) \
                                                                      + dataframe['kod_produktu'].astype(str)
        dataframe = map_values_to_columns(dataframe, 'key_two', 'klasa_konta', 'status_aktyw',
                                          dict_update.get_dict_klasa_konta_status_aktyw())
        dataframe['rachunek'] = dataframe['rachunek'].astype(str)
        del dataframe['key_two']
        dataframe = dataframe.rename(columns={'kod_produktu': 'kod_produktu_maestro', 'nr_konta': 'nr_konta_maestro'})
        return dataframe[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta', 'id_konta',
                          'rachunek_maestro', 'nr_konta_maestro', 'kod_produktu_maestro', 'saldo']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame, is_eod=False) -> pandas.DataFrame:
        if is_eod:
            dataframe.loc[:, 'status_aktyw'] = dataframe['status_aktyw'].str.upper()
        return dataframe[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta', 'saldo']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'status_aktyw'] = dataframe['status_aktyw'].str.upper()
        return dataframe[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta', 'saldo']]

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"SaldaPw(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"SaldaFin(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                converted_src_df_pl = self.dataframe_src[self.dataframe_src['gielda'] == 'WWA']
                converted_src_df = self.dataframe_src[self.dataframe_src['gielda'] != 'WWA']

                converted_ext_df_pl = self.dataframe_ext[self.dataframe_ext['gielda'] == 'WWA']
                converted_ext_df = self.dataframe_ext[self.dataframe_ext['gielda'] != 'WWA']

                dataframe_ext_saldo_pl = converted_ext_df_pl.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False)['saldo'].sum()
                dataframe_ext_saldo_zagr = converted_ext_df.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False)['saldo'].sum()
                dataframe_src_saldo_pl = converted_src_df_pl.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False).agg({
                    'saldo': 'sum',
                    # 'rachunek_maestro': 'first',
                    # 'kod_produktu_maestro': 'first',
                    # 'nr_konta_maestro': 'first'
                })
                dataframe_src_saldo_zagr = converted_src_df.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False).agg({
                    'saldo': 'sum',
                    # 'rachunek_maestro': 'first',
                    # 'kod_produktu_maestro': 'first',
                    # 'nr_konta_maestro': 'first'
                })
                report_saldo_pl = excel_workbook.create_f2f_report(
                    dataframe_1=dataframe_src_saldo_pl[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                                        'status_aktyw', 'klasa_konta', 'saldo']],
                    dataframe_2=dataframe_ext_saldo_pl[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                                        'status_aktyw', 'klasa_konta', 'saldo']],
                    # sheet_name="saldo_RachPapier_PL",
                    merge_on_cols=['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    compare_cols=['saldo'],
                    text_description="Stany papierów na rachunkach klientowskich oraz wewnętrznych, zagregowanych "
                                     "wg pól: giełda, id_depozyt, status_aktyw, klasa_konta Papiery notowane na GPW")

                del dataframe_src_saldo_pl, dataframe_ext_saldo_pl
                report_saldo_zagr = excel_workbook.create_f2f_report(
                    dataframe_1=dataframe_src_saldo_zagr[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                                          'status_aktyw', 'klasa_konta', 'saldo']],
                    dataframe_2=dataframe_ext_saldo_zagr[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                                          'status_aktyw', 'klasa_konta', 'saldo']],
                    # sheet_name="saldo_RachPapier_ZAGR",
                    merge_on_cols=['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    compare_cols=['saldo'],
                    text_description="Stany papierów na rachunkach klientowskich oraz wewnętrznych, zagregowanych wg "
                                     "pól: giełda, id_depozyt, status_aktyw, klasa_konta Papiery notowane poza GPW "
                                     "(zagranica)")
            elif self.stage == TextEnum.END:
                ext_dataframe_pl = self.dataframe_ext[self.dataframe_ext['gielda'] == 'WWA']
                ext_dataframe_zagr = self.dataframe_ext[self.dataframe_ext['gielda'] != 'WWA']

                tgt_dataframe_pl = self.dataframe_tgt[self.dataframe_tgt['gielda'] == 'WWA']
                tgt_dataframe_zagr = self.dataframe_tgt[self.dataframe_tgt['gielda'] != 'WWA']

                dataframe_ext_saldo_pl = ext_dataframe_pl.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False)['saldo'].sum()
                dataframe_ext_saldo_zagr = ext_dataframe_zagr.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False)['saldo'].sum()
                del ext_dataframe_pl, ext_dataframe_zagr
                dataframe_tgt_saldo_pl = tgt_dataframe_pl.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False)['saldo'].sum()
                dataframe_tgt_saldo_zagr = tgt_dataframe_zagr.groupby(
                    ['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta'],
                    as_index=False)['saldo'].sum()
                del tgt_dataframe_pl, tgt_dataframe_zagr

                report_saldo_pl = excel_workbook.create_f2f_report(
                    dataframe_1=dataframe_ext_saldo_pl,
                    dataframe_2=dataframe_tgt_saldo_pl,
                    # sheet_name="saldo_RachPapier_PL",
                    merge_on_cols=['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                   'status_aktyw', 'klasa_konta'],
                    text_description="Stany papierów na rachunkach klientowskich oraz wewnętrznych, zagregowanych "
                                     "wg pól: giełda, id_depozyt, status_aktyw, klasa_konta Papiery notowane na GPW")
                del dataframe_ext_saldo_pl, dataframe_tgt_saldo_pl
                report_saldo_zagr = excel_workbook.create_f2f_report(
                    dataframe_1=dataframe_ext_saldo_zagr,
                    dataframe_2=dataframe_tgt_saldo_zagr,
                    # sheet_name="saldo_RachPapier_ZAGR",
                    merge_on_cols=['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                   'status_aktyw', 'klasa_konta'],
                    text_description="Stany papierów na rachunkach klientowskich oraz wewnętrznych, zagregowanych wg pól: "
                                     "giełda, id_depozyt, status_aktyw, klasa_konta Papiery notowane poza GPW (zagranica)")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"SaldaPw(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"saldo_RachPapier_PL": report_saldo_pl,
                                          f"saldo_RachPapier_ZAGR": report_saldo_zagr},
                                         merge_on=['rachunek', 'kod_papieru', 'gielda', 'id_depozyt',
                                   'status_aktyw', 'klasa_konta'])
        except Exception as e:
            print(f"SaldaPw(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"SaldaPw(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True
