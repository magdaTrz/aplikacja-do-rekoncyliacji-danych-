import os

import pandas
from pydispatch import dispatcher
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class OiTelecom(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path='',
                 save_folder_report_path='', path_excel_file='report.xlsx', password=None):
        super().__init__()
        print('OiTelecom: __init__')
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
        print(f'OiTelecom: _carry_operations(stage={self.stage})')

        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path, dtype='str')
            src_dataframe = self.set_colum_names({0: 'numer_klienta', 11: 'tel_kom', 12: 'e_mail'}, src_dataframe)

            ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path, dtype='str')
            ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer'}, ext_dataframe)
            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe)
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
            ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer'}, ext_dataframe)
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer'}, tgt_dataframe)
            if tgt_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='numer_klienta')
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    @staticmethod
    def convert_src(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_src()')
        dataframe_tel = dataframe[['numer_klienta', 'tel_kom']].copy()
        dataframe_tel = dataframe_tel.dropna(subset=['tel_kom'])
        dataframe_tel['symbol'] = 'TLK'
        dataframe_tel = dataframe_tel.rename(columns={'tel_kom': 'numer'})

        dataframe_eml = dataframe[['numer_klienta', 'e_mail']].copy()
        dataframe_eml = dataframe_eml.dropna(subset=['e_mail'])
        dataframe_eml['symbol'] = 'EML'
        dataframe_eml = dataframe_eml.rename(columns={'e_mail': 'numer'})

        merged_dataframe = pandas.concat([dataframe_eml, dataframe_tel])
        merged_dataframe = merged_dataframe[merged_dataframe['numer'].notna()]
        return merged_dataframe[['numer_klienta', 'symbol', 'numer']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_ext()')
        return dataframe[['numer_klienta', 'symbol', 'numer']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_tgt()')
        return dataframe[['numer_klienta', 'symbol', 'numer']]

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"OiTelecom(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"OiTelecom(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["numer_klienta", "symbol"],
                    compare_cols=["numer"],
                    text_description="Numery łączności podmiotów")
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["numer_klienta", "symbol"],
                    compare_cols=["numer"],
                    text_description="Numery łączności podmiotów")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"OiTelecom(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"f2f_oi_telecom": f2f}, merge_on=["numer_klienta", "symbol"])
        except Exception as e:
            print(f"OiTelecom(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"OiTelecom(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True
