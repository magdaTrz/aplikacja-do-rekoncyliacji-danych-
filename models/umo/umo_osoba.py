import os

import numpy
import pandas

from pydispatch import dispatcher
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.koi import dict_KOI
from models.report_model import ReportModel
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class UmoOsoba(ReportModel):
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
        print(f'UmoOsoba: _carry_operations(stage={self.stage})')

        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: "rachunek", 1: "numer_klienta", 2: "typ_osoby", 3: "zakres"},
                                             ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: "rachunek", 1: "numer_klienta", 2: "typ_osoby", 3: "zakres"},
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
            tgt_dataframe = self.set_colum_names({0: "rachunek", 1: "numer_klienta", 2: "typ_osoby", 3: "zakres"},
                                                 tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return False
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='numer_klienta')
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    @staticmethod
    def convert_src(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"rachunek": str, 'typ_osoby': str})
        # rachunki klietnów sponsorów nie podlegają rekoncyliacji
        mask_82 = dataframe['rachunek'].str.startswith('82')
        dataframe = dataframe[~mask_82]
        dataframe.loc[:, 'typ_osoby'] = dataframe.loc[:, 'typ_osoby'].str.upper()
        dataframe.loc[:, 'zakres'] = dataframe.loc[:, 'zakres'].str.upper()

        dataframe.loc[dataframe['typ_osoby'] == 'KLIENCI_EXT', 'typ_osoby'] = 'U'
        dataframe.loc[dataframe['zakres'] == 'W', 'typ_osoby'] = 'W'
        dataframe.loc[dataframe['zakres'] == 'E', 'typ_osoby'] = 'P'
        dataframe.loc[:, 'zakres'] = 'P'
        del dataframe['zakres']
        working_directory_dane = os.path.join(os.getcwd(), 'dane')
        umowy_dataframe = pandas.read_csv((os.path.join(working_directory_dane, 'rfs_umowy_src.txt')), sep='|', header=None,
                                   names=['numer_klienta', 'nazwa_tablicy'],
                                   usecols=['numer_klienta', 'nazwa_tablicy'])
        mask = (umowy_dataframe['nazwa_tablicy'] != 'klienci')
        umowy_dataframe = umowy_dataframe[~mask]
        umowy_dataframe = umowy_dataframe[~(umowy_dataframe['numer_klienta'] == 13)]

        new_records_bm = pandas.DataFrame({
            'rachunek': umowy_dataframe['numer_klienta'],
            'numer_klienta': 99000000,
            'typ_osoby': 'P',
        })
        dataframe = pandas.concat([dataframe, new_records_bm], ignore_index=True)
        return dataframe

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        def overwrite_nonmigrated_client(main_dataframe):
            wygr_przegr_dataframe = pandas.read_csv('_logi/_reko_pesel_wygr_przegr.csv', sep=',')
            merged_df = pandas.merge(main_dataframe, wygr_przegr_dataframe, left_on='numer_klienta',
                                     right_on='numer_przegr', how='left')
            del wygr_przegr_dataframe, main_dataframe
            merged_df['numer_klienta'] = merged_df['numer_wygr'].combine_first(merged_df['numer_klienta'])
            return merged_df[['rachunek', 'numer_klienta', 'typ_osoby']]

        dataframe = overwrite_nonmigrated_client(dataframe)
        dataframe = dataframe.astype({"rachunek": str, 'typ_osoby': str})
        return dataframe

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"rachunek": str, 'typ_osoby': str})
        return dataframe[['rachunek', 'numer_klienta', 'typ_osoby']]

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"UmoOsoba(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"UmoOsoba(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["rachunek", "numer_klienta"],
                    compare_cols=["typ_osoby"],
                    text_description="Raport sprawdzający powiązanie rachunku z pełnomocnkiem.")
                check_sum = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts='typ_osoby',
                    text_description="Zliczenie typów osobowości pełnomocnictwa"
                )
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["rachunek", "numer_klienta"],
                    compare_cols=["typ_osoby"],
                    text_description="Raport sprawdzający powiązanie rachunku z pełnomocnkiem.")
                check_sum = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts='typ_osoby',
                    text_description="Zliczenie typów osobowości pełnomocnictwa"
                )
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"UmoOsoba(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"f2f_umo_osoba": f2f, f"checksum_umo_osoba": check_sum}, merge_on=["rachunek", "numer_klienta"])
        except Exception as e:
            print(f"UmoOsoba(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"UmoOsoba(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True
