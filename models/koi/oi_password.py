import numpy
import pandas

import paths
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from text_variables import TextEnum


class OiPassword(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path=''):
        super().__init__()
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.data_folder_report_path = data_folder_report_path
        self.path_excel = None

    def _carry_operations(self) -> bool:
        print(f'OiPassword: _carry_operations(stage={self.stage})')
        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: 'oi_id'}, ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: 'oi_id', 13: 'aneks_password'}, src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                src_dataframe = self.convert_src(src_dataframe)
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
            tgt_dataframe = self.set_colum_names({0: 'oi_id'}, tgt_dataframe)

            if ext_dataframe or tgt_dataframe is None:
                return False
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='oi_id')
                ext_dataframe = self.convert_ext(ext_dataframe)
                tgt_dataframe = self.convert_tgt(tgt_dataframe)
                return True

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[dataframe['aneks_password'] == 0, 'oi_id'] = numpy.nan
        dataframe = dataframe.dropna(subset=['oi_id'])
        return dataframe[['oi_id', 'aneks_password']]

    def convert_ext(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'aneks_password'] = 1
        return dataframe[['oi_id', 'aneks_password']]

    def convert_tgt(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'aneks_password'] = 1
        return dataframe[['oi_id', 'aneks_password']]
