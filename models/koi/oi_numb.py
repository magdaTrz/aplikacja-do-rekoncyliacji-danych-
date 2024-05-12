import numpy
import pandas

import paths
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from text_variables import TextEnum


class OiNumb(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path=''):
        super().__init__()
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.data_folder_report_path = data_folder_report_path
        self.path_excel = None

    def _carry_operations(self) -> bool:
        print(f'OiNumb: _carry_operations(stage={self.stage})')
        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer', 3: 'data'}, ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer', 3: 'data'}, src_dataframe)

            support_dataframe = self.make_dataframe_from_file('rfs_klienci_dodatkowe_src.txt',
                                                              self.data_folder_report_path)
            support_dataframe = self.set_colum_names({0: 'numer', 1: 'data', 2: 'pesel', 3: 'cif', 4: 'nip',
                                                      5: 'regon', 6: 'krs'}, support_dataframe)

            if src_dataframe.empty or ext_dataframe.empty or support_dataframe.empty:
                return False
            else:
                src_dataframe = self.convert_src(src_dataframe, support_dataframe)
                ext_dataframe = self.convert_ext(ext_dataframe)
                # excel_workbook = ExcelReport(paths.oi_numb_excel_path)
                # excel_workbook.create_f2f_report(stage='load', dataframe_1=src_dataframe, dataframe_2=ext_dataframe,
                #                                  merge_on_cols=["oi_id", "symbol"], compare_cols=['numer', 'data'],
                #                                  text_description='', file_name=paths.oi_numb_excel_path,
                #                                  sheet_name="f2f_oi_numb")
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer', 3: 'data'}, tgt_dataframe)

            if ext_dataframe or tgt_dataframe is None:
                return
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='oi_id')
                ext_dataframe = self.convert_ext(ext_dataframe)
                tgt_dataframe = self.convert_tgt(tgt_dataframe)

    def convert_src(self, dataframe: pandas.DataFrame, support_dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'symbol'] = dataframe.loc[:, 'symbol'].str.upper()
        dataframe.loc[dataframe['symbol'] == 'I', 'symbol'] = 'IN'
        dataframe.loc[dataframe['symbol'] == 'B', 'symbol'] = 'M'

        df_pesel = support_dataframe[['numer', 'data', 'pesel']].copy()
        df_pesel = df_pesel.dropna(subset=['pesel'])
        df_pesel.loc[:, 'data'] = "L"
        df_pesel.loc[:, 'pesel'] = df_pesel.loc[:, 'pesel'].astype(str)
        df_pesel.loc[df_pesel['pesel'].str.endswith('.0'), 'pesel'] = df_pesel['pesel'].str.replace('.0', '')
        df_pesel = df_pesel.dropna(subset=['pesel'])
        df_pesel = df_pesel.rename(columns={'numer': 'oi_id', 'data': 'symbol', 'pesel': 'numer'})

        df_nip = support_dataframe[['numer', 'data', 'nip']].copy()
        df_nip = df_nip.dropna(subset=['nip'])
        df_nip.loc[:, 'data'] = "NIP"
        df_nip.loc[:, 'nip'] = df_nip.loc[:, 'nip'].astype(str)
        df_nip.loc[df_nip['nip'].str.endswith('.0'), 'nip'] = df_nip['nip'].str.replace('.0', '')
        df_nip = df_nip[df_nip['nip'] != ' ']
        df_nip = df_nip.rename(columns={'numer': 'oi_id', 'data': 'symbol', 'nip': 'numer'})

        df_regon = support_dataframe[['numer', 'data', 'regon']].copy()
        df_regon = df_regon.dropna(subset=['regon'])
        df_regon.loc[:, 'data'] = "R"
        df_regon.loc[:, 'regon'] = df_regon.loc[:, 'regon'].astype(str)
        df_regon = df_regon[df_regon['regon'] != ' ']
        df_regon = df_regon.rename(columns={'numer': 'oi_id', 'data': 'symbol', 'regon': 'numer'})

        df_krs = support_dataframe[['numer', 'data', 'krs']].copy()
        df_krs = df_krs.dropna(subset=['krs'])
        df_krs.loc[:, 'data'] = "KRS"
        df_krs.loc[:, 'krs'] = df_krs.loc[:, 'krs'].astype(str)
        df_krs = df_krs[df_krs['krs'] != ' ']
        df_krs.loc[df_krs['krs'].str.endswith('.0'), 'krs'] = df_krs['krs'].str.replace('.0', '')
        df_krs = df_krs.rename(columns={'numer': 'oi_id', 'data': 'symbol', 'krs': 'numer'})

        df_cif = support_dataframe[['numer', 'data', 'cif']].copy()
        df_cif = df_cif.dropna(subset=['cif'])
        df_cif.loc[:, 'data'] = "CIF"
        df_cif.loc[:, 'cif'] = df_cif.loc[:, 'cif'].astype(str)
        df_cif.loc[:, 'cif'] = df_cif['cif'].apply(lambda x: x.replace('.0', ''))
        df_cif.loc[:, 'cif'] = df_cif['cif'].apply(lambda x: x.zfill(10))
        df_cif = df_cif.rename(columns={'numer': 'oi_id', 'data': 'symbol', 'cif': 'numer'})

        merged_dataframe = pandas.concat([df_pesel, df_cif, df_nip, df_regon, df_krs, dataframe])
        merged_dataframe.loc[:, 'numer'] = merged_dataframe.loc[:, 'numer'].astype(str)
        merged_dataframe = merged_dataframe.loc[~(merged_dataframe['numer'] == '')]
        merged_dataframe = merged_dataframe.astype({'symbol': str, 'numer': str})
        merged_dataframe['data'] = pandas.to_datetime(merged_dataframe['data'].fillna('23-09-1677'), format='%d-%m-%Y',
                                                      errors='coerce')
        merged_dataframe['data'] = merged_dataframe['data'].dt.strftime('%Y-%m-%d')
        merged_dataframe.loc[merged_dataframe['data'] == '1677-09-23', 'data'] = numpy.nan
        return merged_dataframe

    def convert_ext(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({'symbol': str, 'numer': str})
        dataframe = dataframe[dataframe['numer'] != 'nan']
        dataframe['data'] = pandas.to_datetime(dataframe['data'].fillna('23-09-1677'), format='%d-%m-%Y',
                                               errors='coerce')
        dataframe['data'] = dataframe['data'].dt.strftime('%Y-%m-%d')
        dataframe.loc[dataframe['data'] == '1677-09-23', 'data'] = numpy.nan
        return dataframe[['oi_id', 'symbol', 'numer', 'data']]

    def convert_tgt(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({'symbol': str, 'numer': str})
        return dataframe
