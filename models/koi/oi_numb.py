import os

import numpy
import pandas

import paths
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from text_variables import TextEnum


class OiNumb(ReportModel):
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
        print(f'OiNumb: _carry_operations(stage={self.stage})')
        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer', 3: 'data'}, ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer', 3: 'data'}, src_dataframe)
            support_dataframe = self.make_dataframe_from_file('rfs_klienci_dodatkowe_src.txt',
                                                              self.data_folder_report_path)
            support_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'data', 2: 'pesel', 3: 'cif', 4: 'nip',
                                                      5: 'regon', 6: 'krs'}, support_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe, support_dataframe)
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer', 3: 'data'},
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
    def convert_src(dataframe: pandas.DataFrame, support_dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'symbol'] = dataframe.loc[:, 'symbol'].str.upper()
        dataframe.loc[dataframe['symbol'] == 'I', 'symbol'] = 'IN'
        dataframe.loc[dataframe['symbol'] == 'B', 'symbol'] = 'M'

        dataframe['data'] = pandas.to_datetime(dataframe['data'].fillna('23-09-1677'), format='%d-%m-%Y',
                                                      errors='coerce')
        dataframe['data'] = dataframe['data'].dt.strftime('%Y-%m-%d')
        dataframe.loc[dataframe['data'] == '1677-09-23', 'data'] = numpy.nan

        df_pesel = support_dataframe[['numer_klienta', 'pesel']].copy()
        df_pesel = df_pesel.dropna(subset=['pesel'])
        df_pesel.loc[:, 'symbol'] = "L"
        df_pesel.loc[:, 'pesel'] = df_pesel.loc[:, 'pesel'].astype(str)
        df_pesel.loc[df_pesel['pesel'].str.endswith('.0'), 'pesel'] = df_pesel['pesel'].str.replace('.0', '')
        df_pesel = df_pesel.dropna(subset=['pesel'])
        df_pesel = df_pesel.rename(columns={'pesel': 'numer'})

        df_nip = support_dataframe[['numer_klienta', 'nip']].copy()
        df_nip = df_nip.dropna(subset=['nip'])
        df_nip.loc[:, 'symbol'] = "NIP"
        df_nip.loc[:, 'nip'] = df_nip.loc[:, 'nip'].astype(str)
        df_nip.loc[df_nip['nip'].str.endswith('.0'), 'nip'] = df_nip['nip'].str.replace('.0', '')
        df_nip = df_nip.rename(columns={'nip': 'numer'})

        df_regon = support_dataframe[['numer_klienta', 'regon']].copy()
        df_regon = df_regon.dropna(subset=['regon'])
        df_regon.loc[:, 'symbol'] = "R"
        df_regon.loc[:, 'regon'] = df_regon.loc[:, 'regon'].astype(str).str.replace('.0', '')
        df_regon = df_regon[df_regon['regon'] != ' ']
        df_regon = df_regon.rename(columns={'regon': 'numer'})

        df_krs = support_dataframe[['numer_klienta', 'krs']].copy()
        df_krs = df_krs.dropna(subset=['krs'])
        df_krs.loc[:, 'symbol'] = "KRS"
        df_krs.loc[:, 'krs'] = df_krs.loc[:, 'krs'].astype(str)
        df_krs = df_krs[df_krs['krs'] != ' ']
        df_krs.loc[df_krs['krs'].str.endswith('.0'), 'krs'] = df_krs['krs'].str.replace('.0', '')
        df_krs = df_krs.rename(columns={'krs': 'numer'})

        df_cif = support_dataframe[['numer_klienta', 'cif']].copy()
        df_cif = df_cif.dropna(subset=['cif'])
        df_cif.loc[:, 'symbol'] = "CIF"
        df_cif.loc[:, 'cif'] = df_cif.loc[:, 'cif'].astype(str)
        df_cif.loc[:, 'cif'] = df_cif['cif'].apply(lambda x: x.replace('.0', ''))
        df_cif.loc[:, 'cif'] = df_cif['cif'].apply(lambda x: x.zfill(10))
        df_cif = df_cif.rename(columns={'cif': 'numer'})

        merged_dataframe = pandas.concat([df_pesel, df_cif, df_nip, df_regon, df_krs, dataframe])
        return merged_dataframe[['numer_klienta', 'symbol', 'numer', 'data']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({'symbol': str, 'numer': str})
        return dataframe[['numer_klienta', 'symbol', 'numer', 'data']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({'symbol': str, 'numer': str})
        return dataframe[['numer_klienta', 'symbol', 'numer', 'data']]

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"OiNumb(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"OiNumb (): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["numer_klienta", "symbol"],
                    compare_cols=["numer", "data"],
                    text_description="Numery dokumnetów podmiotów zarejestrowanych w systemie")
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["numer_klienta", "symbol"],
                    compare_cols=["numer", "data"],
                    text_description="Numery dokumnetów podmiotów zarejestrowanych w systemie")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"OiNumb(): create_report  Error tworzenia raportu : {e}")
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"f2f_oi_numb": f2f}, merge_on=["numer_klienta", "symbol"])
        except Exception as e:
            print(f"OiNumb(): create_report  Error zapisywania raportu : {e}")
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"OiNumb(): add_password_to_excel  Error daodawania hasła do raportu : {e}")
        return True
