import numpy
import pandas

from controllers.progress_bar import ProgresBarStatus
from models.koi import dict_KOI
from models.report_model import BaseDataFrameModel


class OsobyInstytucjeFile(BaseDataFrameModel):
    def __init__(self, dataframe_rfs_klienci_all: pandas.DataFrame):
        super().__init__()
        self.klienci_all_dataframe = dataframe_rfs_klienci_all
        self._carry_operations()

    def _carry_operations(self):
        ProgresBarStatus.increase_stage()
        klienci_all_dataframe = self.set_colum_names(
            {0: 'numer_maestro', 1: 'nazwa_tabeli', 2: 'osobowosc', 3: 'czy_sponsor', 4: 'pesel',
             5: 'nazwa2', 6: 'nazwa1'}, self.klienci_all_dataframe)

        ProgresBarStatus.increase_stage()
        self.create_files_from_src(klienci_all_dataframe)
        ProgresBarStatus.clear_stage()
        ProgresBarStatus.clear()

    def deleted_non_migrated_record(self, main_dataframe: pandas.DataFrame, column_name='numer'):
        """
            Wczytuje niemigrowane id z pliku 'plik_pomocniczy_niemigrowane_id.csv'. Usuwa niemigrowane rekordy z DataFrame.

            Args:
                main_dataframe (DataFrame): Data Frame w ktorym funkcja usuwa niemigrowane id.
                column_name (str, optional): Nazwa kolumny która zawiera id.
            Raises:
                KeyError: Gdy `column_name` jest nie znajduje się w `main_dataframe`. Zwraca `main_dataframe`.
                FileNotFoundError: Gdy plik 'plik_pomocniczy_niemigrowane_id.csv' nie znajduje sie w katalogu. Zwraca `main_dataframe`.
            Returns:
                DataFrame: Dataframe zawierająca tylko migrowane rekordy.
        # try:
        #     non_migrated = pandas.read_csv('plik_pomocniczy_niemigrowane_id.csv', sep='|')
        # except FileNotFoundError:
        #     print(text_variables.no_file_non_migrated)
        #     return main_dataframe"""
        non_migrated = self.file_csv_open(name_file='plik_pomocniczy_niemigrowane_id.csv')
        del non_migrated['typ']
        try:
            _df = main_dataframe[~main_dataframe[column_name].isin(non_migrated['numer'])]
        except KeyError:
            print('text_variables.non_migrated_fail')
            return main_dataframe
        return _df

    def create_files_from_src(self, dataframe):
        df_c = dataframe.copy()
        ProgresBarStatus.increase_stage()
        '''Tworzenie pliku pomocniczego dla osoby instytucje'''
        df_c.loc[:, 'nazwa_tabeli'] = df_c.loc[:, 'nazwa_tabeli'].str.upper()
        df_c['numer'] = df_c['numer_maestro']
        df_c['typ'] = None
        df_c = self.map_values_based_on_two_columns(dataframe=df_c, column_to_fill='typ', column1='osobowosc',
                                                    column2='czy_sponsor', map_dict=dict_KOI.dict_type_mapping)
        ProgresBarStatus.increase_stage()
        df_c = self.mapp_values(dataframe=df_c, column_to_fill='typ',
                                column_to_take='nazwa_tabeli', map_dict=dict_KOI.dict_table_name_type)
        ProgresBarStatus.increase_stage()
        del df_c['nazwa_tabeli']
        df_c['status'] = 'NIEMIGRUJEMY'
        df_c = self.mapp_values(dataframe=df_c, column_to_fill='status',
                                column_to_take='typ', map_dict=dict_KOI.dict_table_name_migration)
        ProgresBarStatus.increase_stage()
        df_c.loc[df_c['pesel'].isnull(), 'status'] = 'MIGRUJEMY'

        osoby_instytucje_df = self.create_koi_file(dataframe=df_c[['numer_maestro', 'numer', 'typ', 'pesel', 'nazwa2',
                                                                   'nazwa1', 'status']])
        ProgresBarStatus.increase_stage()
        self.file_csv_write(osoby_instytucje_df, 'osoby_instytucje_file.csv', na_rep='NULL')
        ProgresBarStatus.increase_stage()
        """ Note: Wywołanie funckcji tworzącej plik pomocniczy umo_osoba_file.csv """
        self.create_umo_osoba_file(dataframe=osoby_instytucje_df)
        ProgresBarStatus.increase_stage()
        """ Note: Wywołanie funckcji tworzącej plik pomocniczy niemigrowane.csv """
        self.create_niemigrowane_file(dataframe=osoby_instytucje_df)
        ProgresBarStatus.increase_stage()
        del df_c['status']
        del df_c['pesel']
        del df_c['osobowosc']
        return df_c[['numer_maestro', 'numer', 'typ', 'nazwa2']]

    def create_koi_file(self, dataframe):
        filtered = self.check_type(dataframe)
        merged_df = dataframe.merge(filtered, how='left', on=['numer_maestro', 'numer', 'typ', 'pesel'],
                                    suffixes=('', '_new'))
        merged_df['status'] = merged_df['status_new'].combine_first(merged_df['status'])
        dataframe.loc[:, 'status'] = merged_df.loc[:, 'status']
        del dataframe['numer_maestro']
        return dataframe

    def create_umo_osoba_file(self, dataframe: pandas.DataFrame):
        df_c_sorted = dataframe.sort_values(by='status', ascending=True)
        grouped_pesel_numer = df_c_sorted.groupby('pesel')['numer'].apply(list)
        filtered_pesel_numer = grouped_pesel_numer[grouped_pesel_numer.apply(len) > 1]
        result_df = pandas.DataFrame(filtered_pesel_numer).reset_index()
        self.file_csv_write(result_df, 'plik_pomocniczy_dla_umo_osoba.csv')
        return

    def create_niemigrowane_file(self, dataframe: pandas.DataFrame):
        filtered_ids = pandas.DataFrame()
        filtered_ids['numer'] = dataframe.loc[dataframe['status'] == 'NIEMIGRUJEMY', 'numer']
        filtered_ids['typ'] = dataframe.loc[dataframe['status'] == 'NIEMIGRUJEMY', 'typ']
        self.file_csv_write(filtered_ids, 'plik_pomocniczy_niemigrowane_id.csv')

    def check_type(self, dataframe):
        """
            Funkcja która sprawdza typ i wybiera wygrywający numer_klienta.

            Args:
                dataframe (dataframe): Data Frame na której wykonywane są operacje.
            Returns:
                dataframe: Dataframe zawierająca tylko migrowane rekordy.
            """
        rules = {
            'F': lambda x: x['typ'] == 'F',
            'U': lambda x: x['typ'] == 'U',
            'R': lambda x: x['typ'] == 'R',
            'E': lambda x: x['typ'] == 'E',
            'Z': lambda x: x['typ'] == 'Z',
        }
        filtered_rows = []
        grouped_df = dataframe[dataframe['typ'].isin(['E', 'F', 'Z', 'R', 'U'])].groupby('pesel')
        for _, group_df in grouped_df:
            selected_row = None
            if ('E' in group_df['typ'].values) and ('U' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'E']
            elif ('E' in group_df['typ'].values) and ('R' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'E']
            elif ('E' in group_df['typ'].values) and ('F' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'F']
            elif ('F' in group_df['typ'].values) and ('U' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'F']
            elif ('F' in group_df['typ'].values) and ('R' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'F']
            elif ('U' in group_df['typ'].values) and ('R' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'U']
            elif ('Z' in group_df['typ'].values) and ('U' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'Z']
            elif ('Z' in group_df['typ'].values) and ('R' in group_df['typ'].values):
                selected_row = group_df[group_df['typ'] == 'Z']

            if selected_row is None:
                for typ_osoby, rule in rules.items():
                    selected_row = group_df[rule(group_df)]
                    if not selected_row.empty:
                        break

            if not selected_row.empty:
                filtered_rows.append(selected_row)

        filtered_df = pandas.concat(filtered_rows)
        filtered_df.loc[:, 'status'] = 'MIGRUJEMY'
        ProgresBarStatus.increase_stage()
        try:
            dataframe.loc[dataframe['pesel'].str.len() < 11, 'status'] = 'MIGRUJEMY'
            dataframe.loc[dataframe['pesel'].str.len() < 11, 'pesel'] = numpy.nan
            print("   Pesele krotsze niz 11 znaków sa migrowane. ")
        except AttributeError:
            print("   Błąd usunięcia peseli krótszych niż 11 znaków. ")
        dataframe.loc[dataframe['pesel'].isin(['00000000000', '11111111111']), 'status'] = 'MIGRUJEMY'
        dataframe.loc[dataframe['pesel'].isin(['00000000000', '11111111111']), 'pesel'] = numpy.nan
        return filtered_df