import os

import numpy
import pandas

from pydispatch import dispatcher
import paths
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class OiConsents(ReportModel):
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
        print(f'OiConsents: _carry_operations(stage={self.stage})')
        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'consent_type', 2: 'consent_start_time',
                                              3: 'consent'}, ext_dataframe)

        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'consent_type', 2: 'consent_start_time',
                                                  3: 'consent'}, src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe)
                self.dataframe_ext = self.convert_ext(ext_dataframe)

                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'consent_type', 2: 'consent_start_time',
                                                  3: 'consent'}, tgt_dataframe)

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
        dataframe = dataframe[dataframe['consent'] != 'B']
        dataframe = dataframe[dataframe['consent'] != '0']
        dataframe.loc[:, 'consent_type'] = dataframe['consent_type'].map(
            {
                "SUDE": "SU",
                "EPODPIS": "EP",
                "PB_BM": "PB",
                "TELE": "TL",
                "GROUP": "GR",
            }
        ).fillna(dataframe['consent_type'])
        dataframe.loc[:, 'consent'] = dataframe['consent'].map(
            {
                "T": "Y",
                "P": "N",
                "E": "Y",
                "K": "N",
            }
        ).fillna(dataframe['consent'])

        dataframe['consent_start_time'] = pandas.to_datetime(dataframe['consent_start_time'].fillna("23-09-1677"),
                                                             format="%d-%m-%Y", errors='coerce')
        dataframe['consent_start_time'] = dataframe['consent_start_time'].dt.strftime("%Y-%m-%d")
        dataframe.loc[dataframe['consent_start_time'] == '1677-09-23', 'consent_start_time'] = numpy.nan
        return dataframe[['numer_klienta', 'consent_type', 'consent_start_time', 'consent']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        return dataframe[['numer_klienta', 'consent_type', 'consent_start_time', 'consent']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        return dataframe[['numer_klienta', 'consent_type', 'consent_start_time', 'consent']]

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"OiConsents(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"OiConsents(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["numer_klienta", "consent_type"],
                    compare_cols=["consent_start_time", "consent"],
                    text_description="Rejestr zgód, oświadczeń klienta")
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["numer_klienta", "consent_type"],
                    compare_cols=["consent_start_time", "consent"],
                    text_description="Rejestr zgód, oświadczeń klienta")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"OiConsents(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"f2f_oi_consents": f2f}, merge_on=["numer_klienta", "consent_type"])
        except Exception as e:
            print(f"OiConsents(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"OiConsents(): add_password_to_excel  Error daodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True
