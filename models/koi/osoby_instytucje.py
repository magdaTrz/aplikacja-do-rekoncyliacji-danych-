import os

import pandas

from pydispatch import dispatcher
from controllers.progress_bar import ProgresBarStatus
from models.report_model import ReportModel
from text_variables import TextEnum
from models.excel_report import ExcelReport

UPDATE_TEXT_SIGNAL = 'update_text'


class OsobyInstytucje(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path='',
                 save_folder_report_path='', path_excel_file='report.xlsx', password: None = None):
        super().__init__()
        print('OsobyInstytucje: __init__')
        self.stage = stage
        self.path_src: str = path_src
        self.path_ext: str = path_ext
        self.path_tgt: str = path_tgt
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
        self.password: str | None = password

    def _carry_operations(self) -> bool:
        print(f'OsobyInstytucje: _carry_operations({self.stage=})')

        if self.stage == TextEnum.LOAD:
            path = os.path.join(os.getcwd(), '_logi')
            klienci_all_dataframe = self.make_dataframe_from_file(path_to_file='_reko_osoby_instytucje_file.csv',
                                                                  path_to_folder=path, sep=",")
            klienci_all_dataframe = self.set_colum_names(
                {0: 'numer_klienta', 1: 'numer_klienta_Maestro', 2: 'typ', 3: 'pesel', 4: 'nazwa2',
                 5: 'nazwa1', 6: 'imie2', 7: 'status'}, klienci_all_dataframe)
            klienci_all_dataframe = klienci_all_dataframe.drop(klienci_all_dataframe.index[0])

            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path, dtype='str')
            src_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'data', 2: 'pesel'},
                                                 src_dataframe)

            ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path, dtype='str')
            ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'typ', 2: 'nazwa1', 3: 'nazwa2', 4: 'data'},
                                                 ext_dataframe)

            if src_dataframe.empty or ext_dataframe.empty or klienci_all_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe,
                                                      klienci_all_dataframe[['numer_klienta', 'typ', 'nazwa2',
                                                                             'nazwa1', 'imie2']])
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            ext_dataframe = self.make_dataframe_from_file(self.path_ext)
            ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'typ', 2: 'nazwa1', 3: 'nazwa2', 4: 'data'},
                                                 ext_dataframe)
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt)
            tgt_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'typ', 2: 'nazwa1', 3: 'nazwa2', 4: 'data'},
                                                 tgt_dataframe)
            if tgt_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    @staticmethod
    def convert_src(dataframe: pandas.DataFrame, dataframe_2: pandas.DataFrame) -> pandas.DataFrame:
        print('OsobyInstytucje: convert_src()')

        dataframe = dataframe[['numer_klienta', 'data']].copy()
        dataframe_merged = pandas.merge(dataframe, dataframe_2, on='numer_klienta', how='outer')
        dataframe_merged.loc[~dataframe_merged['typ'].isin(['E', 'F', 'U', 'Z']), 'data'] = None
        condition_is_corporation = dataframe_merged['typ'].isin(['R', 'U', 'G', 'P', 'S', 'T', 'F', 'E', 'Z'])
        dataframe_merged.loc[condition_is_corporation, ['nazwa1', 'nazwa2']] = \
            dataframe_merged.loc[condition_is_corporation, ['nazwa2', 'nazwa1']].to_numpy()

        condition_has_middle_name = ~dataframe_merged['imie2'].isna()
        dataframe_merged.loc[condition_has_middle_name, 'nazwa2'] = \
            dataframe_merged.loc[condition_has_middle_name, 'nazwa2'] + ' ' + \
            dataframe_merged.loc[condition_has_middle_name, 'imie2'].astype(str)
        dataframe_merged.loc[:, 'nazwa2'] = dataframe_merged.loc[:, 'nazwa2'].astype(str).str.lstrip().str.rstrip()
        dataframe_merged.loc[:, 'nazwa1'] = dataframe_merged.loc[:, 'nazwa1'].astype(str).str.lstrip().str.rstrip()
        return dataframe_merged[['numer_klienta', 'typ', 'nazwa1', 'nazwa2', 'data']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OsobyInstytucje: convert_ext()')
        return dataframe

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OsobyInstytucje: convert_tgt()')
        return dataframe

    def create_report(self) -> TextEnum | bool:
        print(f"OsobyInstytucje(): create_report({self.path_excel}  {self.save_folder_report_path} )")

        try:
            path = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path, self.stage)
        except Exception as e:
            print(f"OsobyInstytucje(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            f2f = excel_workbook.create_f2f_report(
                dataframe_1=self.dataframe_src,
                dataframe_2=self.dataframe_ext,
                merge_on_cols=["numer_klienta"],
                compare_cols=["typ", "nazwa1", "nazwa2", "data"],
                text_description="")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"OsobyInstytucje(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"report_name": f2f}, merge_on=["numer_klienta"])
        except Exception as e:
            print(f"OsobyInstytucje(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR
        try:
            excel_workbook.add_password_to_excel(path, self.password)
        except Exception as e:
            print(f"OiPassword(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True

