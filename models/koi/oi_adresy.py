import numpy
import pandas

from controllers.progress_bar import ProgresBarStatus
from models.koi import dict_KOI
from models.report_model import ReportModel
from text_variables import TextEnum


class OiAdresy(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path=''):
        super().__init__()
        print('OiAdresy: __init__')
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.data_folder_report_path = data_folder_report_path
        self.path_excel = None

    def _carry_operations(self) -> bool:
        print(f'OiAdresy: _carry_operations(stage={self.stage})')

        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names({0: "oi_id", 1: "typ", 2: "ulica", 3: "dom", 4: "miejscowosc",
                                              5: "poczta", 6: "kod", 7: "kraj"},
                                             ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names({0: "oi_id", 1: "typ", 2: "ulica", 3: "dom", 4: "miejscowosc",
                                                  5: "poczta", 6: "kod", 7: "kraj"},
                                                 src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                src_dataframe = self.convert_src(src_dataframe)
                ext_dataframe = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.LOAD:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt)
            tgt_dataframe = self.set_colum_names({0: "oi_id", 1: "typ", 2: "ulica", 3: "dom", 4: "miejscowosc",
                                                  5: "poczta", 6: "kod", 7: "kraj"},
                                                 tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='oi_id')
                ext_dataframe = self.convert_ext(ext_dataframe)
                tgt_dataframe = self.convert_tgt(tgt_dataframe)

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"typ": str, "ulica": str, "dom": str, "miejscowosc": str, "poczta": str,
                                      "kod": str, "kraj": str})
        dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'dom'] = dataframe.loc[:, 'dom'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kraj'] = dataframe.loc[:, 'kraj'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'typ'] = dataframe.loc[:, 'typ'].astype(str).str.upper()

        dataframe = dataframe.loc[dataframe['typ'].isin(['KLIENCI', 'KL_ADRESY'])]
        dataframe.loc[dataframe['typ'] == 'KLIENCI', 'typ'] = 'Z'
        dataframe.loc[dataframe['typ'] == 'KL_ADRESY', 'typ'] = 'K'
        return dataframe

    def convert_ext(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"typ": str, "ulica": str, "dom": str, "miejscowosc": str, "poczta": str,
                                      "kod": str, "kraj": str})
        dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'dom'] = dataframe.loc[:, 'dom'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'poczta'] = dataframe.loc[:, 'poczta'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].astype(str).str.lstrip().str.rstrip()
        return dataframe

    def convert_tgt(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'dom'] = dataframe.loc[:, 'dom'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'poczta'] = dataframe.loc[:, 'poczta'].astype(str).str.lstrip().str.rstrip()
        dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].astype(str).str.lstrip().str.rstrip()
