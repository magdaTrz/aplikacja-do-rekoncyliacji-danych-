import numpy
import pandas

from controllers.progress_bar import ProgresBarStatus
from models.koi import dict_KOI
from models.report_model import BaseDataFrameModel


class OiAdresy(BaseDataFrameModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None):
        super().__init__()
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.path_excel = None

    def _carry_operations(self):
        ext_dataframe = self.make_dataframe_from_file(self.path_ext)
        ext_dataframe = self.set_colum_names({0: "oi_id", 1: "typ", 2: "ulica", 3: "dom", 4: "miejscowosc",
                                              5: "poczta", 6: "kod", 7: "kraj"},
                                             ext_dataframe)
        if self.stage == 'load':
            src_dataframe = self.make_dataframe_from_file(self.path_src)
            src_dataframe = self.set_colum_names({0: "oi_id", 1: "typ", 2: "ulica", 3: "dom", 4: "miejscowosc",
                                                  5: "poczta", 6: "kod", 7: "kraj"},
                                                 src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return
            else:
                src_dataframe = self.convert_src(src_dataframe)
                return
            ProgresBarStatus.increase()

        if self.stage == 'end':
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt)
            tgt_dataframe = self.set_colum_names({0: "oi_id", 1: "typ", 2: "ulica", 3: "dom", 4: "miejscowosc",
                                                  5: "poczta", 6: "kod", 7: "kraj"},
                                                 tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='oi_id')

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"typ": str, "ulica": str, "dom": str, "miejscowosc": str, "poczta": str,
                                      "kod": str, "kraj": str})
        dataframe.loc[:, 'ulica'] = dataframe['ulica'].str.replace('?>', '"')
        dataframe.loc[:, 'dom'] = dataframe['dom'].str.replace('?>', '"')
        dataframe.loc[:, 'miejscowosc'] = dataframe['miejscowosc'].str.replace('?>', '"')
        df_c = dataframe.copy()
        try:
            df_c.loc[df_c['miejscowosc'] == ' ', 'miejscowosc'] = str("\ ")
            df_c.loc[:, 'miejscowosc'] = df_c.loc[:, 'miejscowosc'].str.lstrip()
        except AttributeError:
            pass

        try:
            df_c.loc[df_c['ulica'] == ' ', 'ulica'] = str('\ ')
            df_c.loc[df_c['ulica'] != '\ ', 'ulica'] = df_c.loc[df_c['ulica'] != '\ ', 'ulica'].astype(str).str.rstrip()
            df_c.loc[:, 'ulica'] = df_c.loc[:, 'ulica'].str.lstrip()
        except AttributeError:
            pass

        try:
            df_c.loc[df_c['dom'] == ' ', 'dom'] = str('\ ')
            df_c.loc[:, 'dom'] = df_c.loc[:, 'dom'].str.lstrip()
        except AttributeError:
            pass

        try:
            df_c.loc[:, 'kraj'] = df_c.loc[:, 'kraj'].str.lstrip()
        except AttributeError:
            pass

        try:
            df_c.loc[df_c['kod'] == ' ', 'kod'] = str("\ ")
            df_c.loc[:, 'kod'] = df_c.loc[:, 'kod'].str.lstrip()
        except AttributeError:
            pass

        try:
            df_c.loc[:, 'typ'] = df_c.loc[:, 'typ'].str.upper().str.lstrip()
        except AttributeError:
            pass
        df_c = df_c.loc[df_c['typ'].isin(['KLIENCI', 'KL_ADRESY'])]
        df_c = self.mapp_values(dataframe=df_c, column_to_take='typ', column_to_fill='typ',
                                map_dict=dict_KOI.dict_adresy)
        return df_c

    def convert_ext(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = dataframe.astype({"typ": str, "ulica": str, "dom": str, "miejscowosc": str, "poczta": str,
                                      "kod": str, "kraj": str})
        dataframe.loc[:, 'ulica'] = dataframe['ulica'].str.replace('?>', '"')
        dataframe.loc[:, 'dom'] = dataframe['dom'].str.replace('?>', '"')
        dataframe.loc[:, 'miejscowosc'] = dataframe['miejscowosc'].str.replace('?>', '"')
        try:
            dataframe.loc[dataframe['ulica'] == '\ ', 'ulica'] = numpy.nan
        except AttributeError:
            pass
        try:
            dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].str.lstrip()
            dataframe.loc[:, 'ulica'] = dataframe.loc[:, 'ulica'].str.rstrip()
        except AttributeError:
            pass
        try:
            dataframe.loc[dataframe['ulica'] == ' ', 'ulica'] = ''
        except AttributeError:
            pass

        try:
            dataframe.loc[dataframe['dom'] == '\ ', 'dom'] = numpy.nan
            dataframe.loc[:, 'dom'] = dataframe.loc[:, 'dom'].str.replace('"', ' ')
            dataframe.loc[dataframe['dom'] == ' ', 'dom'] = ''
            dataframe.loc[:, 'dom'] = dataframe.loc[:, 'dom'].str.lstrip()
            dataframe.loc[:, 'dom'] = dataframe.loc[:, 'dom'].str.rstrip()
        except AttributeError:
            pass

        try:
            dataframe.loc[dataframe['miejscowosc'] == '\ ', 'miejscowosc'] = numpy.nan
            dataframe.loc[:, 'miejscowosc'] = dataframe.loc[:, 'miejscowosc'].str.lstrip()
            dataframe.loc[dataframe['miejscowosc'] == ' ', 'miejscowosc'] = ''
        except AttributeError:
            pass

        try:
            dataframe.loc[dataframe['poczta'] == ' ', 'poczta'] = numpy.nan
            dataframe.loc[:, 'poczta'] = dataframe.loc[:, 'poczta'].str.lstrip()
        except AttributeError:
            pass
            # print("   Błąd zmiany 'miejscowosc': ")

        try:
            dataframe.loc[dataframe['kod'] == '\ ', 'kod'] = numpy.nan
            dataframe.loc[:, 'kod'] = dataframe.loc[:, 'kod'].str.lstrip()
        except AttributeError:
            pass
            print("   Błąd zmiany 'kod': ")

    def convert_tgt(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[dataframe['poczta'] == '', 'poczta'] = numpy.nan