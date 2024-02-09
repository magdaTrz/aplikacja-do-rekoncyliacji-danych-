import numpy
import pandas

from controllers.progress_bar import ProgresBarStatus
from models.koi import dict_KOI
from models.report_model import BaseDataFrameModel


class OiAtryb(BaseDataFrameModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None):
        super().__init__()
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.path_excel = None

    def _carry_operations(self):
        ext_dataframe = self.make_dataframe_from_file(self.path_ext)
        ext_dataframe = self.set_colum_names({0: "oi_id", 1: "symbol", 2: "wartosc"},
                                             ext_dataframe)
        if self.stage == 'load':
            src_dataframe = self.make_dataframe_from_file(self.path_src)
            src_dataframe = self.set_colum_names({0: 'numer', 1: 'data', 2: 'pesel', 3: 'cif', 4: 'nip', 5: 'regon', 6: 'krs', 7: 'fop',
                            8: 'rezydent', 9: 'obywatelstwo', 10: 'nr_nik'},
                                                 src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return
            else:
                src_dataframe = self.convert_src(src_dataframe)
                return
            ProgresBarStatus.increase()

        if self.stage == 'end':
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt)
            tgt_dataframe = self.set_colum_names({0: "oi_id", 1: "symbol", 2: "wartosc"},
                                                 tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='oi_id')

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        df_tos = dataframe[['numer', 'fop', 'rezydent']].copy()
        df_tos = df_tos.dropna(subset=['fop', 'rezydent'])
        df_tos.loc[:, 'tos'] = 'TOS'
        df_tos.loc[:, 'wartosc'] = None
        # df_tos.loc[:, 'rezydent'] = df_tos.loc[:, 'rezydent'].astype(str)
        df_tos = self.map_values_based_on_two_columns(dataframe=df_tos, column_to_fill='wartosc', column1='fop',
                                                 column2='rezydent', map_dict=dict_KOI.dict_atryb_tos)
        del df_tos['fop']
        del df_tos['rezydent']
        df_tos = df_tos.rename(columns={'numer': 'oi_id', 'tos': 'symbol'})
        df_obw = dataframe[['numer', 'rezydent', 'obywatelstwo']].copy()
        df_obw = df_obw.dropna(subset=['obywatelstwo'])
        df_obw.loc[:, 'rezydent'] = "OBW"
        df_obw = df_obw.rename(columns={'numer': 'oi_id', 'rezydent': 'symbol', 'obywatelstwo': 'wartosc'})
        df_obw = df_obw.loc[~(df_obw['wartosc'] == 'XX')]

        df_www = dataframe[['numer', 'rezydent', 'nr_nik']].copy()
        df_www = df_www.dropna(subset=['nr_nik'])
        df_www.loc[:, 'rezydent'] = "WWW"
        df_www = df_www.rename(columns={'numer': 'oi_id', 'rezydent': 'symbol', 'nr_nik': 'wartosc'})
        df_www = df_www.loc[~(df_www['wartosc'] == ' ')]

        df_fop = dataframe[['numer', 'rezydent', 'fop']].copy()
        df_fop = df_fop.dropna(subset=['fop'])
        df_fop.loc[:, 'fop'] = df_fop.loc[:, 'fop'].astype(str)
        df_fop.loc[:, 'rezydent'] = "FOP"
        df_fop = df_fop.rename(columns={'numer': 'oi_id', 'rezydent': 'symbol', 'fop': 'wartosc'})
        df_fop = self.mapp_values(dataframe=df_fop, column_to_take='wartosc', column_to_fill='wartosc',
                             map_dict=dict_KOI.dict_atryb_fop)

        merged_df = pandas.concat([df_fop, df_www, df_obw, df_tos])
        return merged_df

    def convert_ext(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
       pass

    def convert_tgt(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        pass