import os.path

import pandas

from models.report_model import BaseDataFrameModel


class OiTelecom(BaseDataFrameModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None):
        super().__init__()
        print('OiTelecom: __init__')
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.path_excel = None
        self._carry_operations()

    def _carry_operations(self):
        print(f'OiTelecom: _carry_operations(stage={self.stage})')
        dir_path = self.get_dir_path()

        if self.stage == 'load':
            src_dataframe = self.make_dataframe_from_file(os.path.join(dir_path, self.path_src))
            src_dataframe = self.set_colum_names({0: 'numer', 11: 'tel_kom', 12: 'e_mail'},
                                                 src_dataframe)
            ext_dataframe = self.make_dataframe_from_file(os.path.join(dir_path, self.path_ext))
            ext_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer'},
                                                 ext_dataframe)
            src_dataframe = self.convert_src(src_dataframe)


        if self.stage == 'end':
            ext_dataframe = self.make_dataframe_from_file(os.path.join(dir_path, self.path_ext))
            ext_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer'},
                                                 ext_dataframe)
            tgt_dataframe = self.make_dataframe_from_file(os.path.join(dir_path, self.path_tgt))
            tgt_dataframe = self.set_colum_names({0: 'oi_id', 1: 'symbol', 2: 'numer'},
                                                 tgt_dataframe)

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

