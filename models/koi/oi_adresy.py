import os

import numpy
import pandas

from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.koi import dict_KOI
from models.report_model import ReportModel
from text_variables import TextEnum


class OiAdresy(ReportModel):
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
        print(f'OiAdresy: _carry_operations(stage={self.stage})')

        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: "numer_klienta", 1: "typ", 2: "ulica", 3: "miejscowosc",
                                                  4: "kod", 5: "kraj"}, ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: "numer_klienta", 1: "typ", 2: "ulica", 3: "miejscowosc",
                                                  4: "kod", 5: "kraj"}, src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe)
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt)
            tgt_dataframe = self.set_colum_names({0: "numer_klienta", 1: "typ", 2: "ulica", 3: "miejscowosc",
                                                  4: "kod", 5: "kraj"}, tgt_dataframe)

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
        dataframe = dataframe.astype({"typ": str, "ulica": str, "miejscowosc": str, "kod": str, "kraj": str})
        dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kraj'] = dataframe.loc[:, 'kraj'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'typ'] = dataframe.loc[:, 'typ'].astype(str).str.upper()

        dataframe.loc[:, 'typ'] = dataframe.loc[:, 'typ'].str.upper()
        dataframe = dataframe.loc[dataframe['typ'].isin(['KLIENCI', 'KL_ADRESY'])]
        dataframe.loc[dataframe['typ'] == 'KLIENCI', 'typ'] = 'Z'
        dataframe.loc[dataframe['typ'] == 'KL_ADRESY', 'typ'] = 'K'
        return dataframe

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"typ": str, "ulica": str, "miejscowosc": str, "kod": str, "kraj": str})
        dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kraj'] = dataframe.loc[:, 'kraj'].astype(str).str.lstrip().str.rstrip()
        return dataframe

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"typ": str, "ulica": str, "miejscowosc": str, "kod": str, "kraj": str})
        dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kraj'] = dataframe.loc[:, 'kraj'].astype(str).str.lstrip().str.rstrip()
        return dataframe

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"OiAdresy(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"OiAdresy(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["numer_klienta", "typ"],
                    compare_cols=["ulica", "miejscowosc", "kod", "kraj"],
                    text_description="Adresy podmiotów zarejestrowanych w systemie")
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["numer_klienta", "typ"],
                    compare_cols=["ulica", "miejscowosc", "kod", "kraj"],
                    text_description="Adresy podmiotów zarejestrowanych w systemie")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"OiAdresy(): create_report  Error tworzenia raportu : {e}")
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"f2f_oi_adresy": f2f}, merge_on=["numer_klienta", "typ"])
        except Exception as e:
            print(f"OiAdresy(): create_report  Error zapisywania raportu : {e}")
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"OiAdresy(): add_password_to_excel  Error daodawania hasła do raportu : {e}")
        return True
