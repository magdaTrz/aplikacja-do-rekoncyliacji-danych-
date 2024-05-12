import pandas

from controllers.progress_bar import ProgresBarStatus
from models.report_model import ReportModel
from text_variables import TextEnum


class OiTelecom(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path=''):
        super().__init__()
        print('OiTelecom: __init__')
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.data_folder_report_path = data_folder_report_path
        self.path_excel = None

    def _carry_operations(self) -> bool:
        print(f'OiTelecom: _carry_operations(stage={self.stage})')

        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path, dtype='str')
            src_dataframe = self.set_colum_names({0: 'numer', 11: 'tel_kom', 12: 'e_mail'},
                                                 src_dataframe)

            ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path, dtype='str')
            ext_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer'},
                                                 ext_dataframe)
            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                src_dataframe = self.convert_src(src_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            ext_dataframe = self.make_dataframe_from_file(self.path_ext)
            ext_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer'},
                                                 ext_dataframe)
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt)
            tgt_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer'},
                                                 tgt_dataframe)
            if tgt_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                pass
                ProgresBarStatus.increase()
                return True

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_src()')

        dataframe_tel = dataframe[['numer', 'tel_kom']].copy()
        dataframe_tel = dataframe_tel.dropna(subset=['tel_kom'])
        dataframe_tel['symbol'] = 'TLK'
        dataframe_tel = dataframe_tel.rename(columns={'numer': 'oi_id', 'tel_kom': 'numer'})

        dataframe_eml = dataframe[['numer', 'e_mail']].copy()
        dataframe_eml = dataframe_eml.dropna(subset=['e_mail'])
        dataframe_eml['symbol'] = 'EML'
        dataframe_eml = dataframe_eml.rename(columns={'numer': 'oi_id', 'e_mail': 'numer'})

        merged_dataframe = pandas.concat([dataframe_eml, dataframe_tel])
        merged_dataframe = merged_dataframe[merged_dataframe['numer'].notna()]
        return merged_dataframe

    def convert_ext(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_ext()')

    def convert_tgt(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_ext()')
