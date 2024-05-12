import os
import time

import numpy
import pandas

from .base import ObservableModel
from paths import path_support_files_folder
from .koi import dict_KOI


def check_type(dataframe):
    """
    A function that checks the type and selects the winning customer_number.
    Args:
        dataframe: Data Frame on which operations are performed.
    Returns:
        dataframe: Dataframe containing only migrated records.
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
        elif ('Z' in group_df['typ'].values) and ('F' in group_df['typ'].values):
            selected_row = group_df[group_df['typ'] == 'F']

        if selected_row is None:
            for person_type, rule in rules.items():
                selected_row = group_df[rule(group_df)]
                if not selected_row.empty:
                    break
        if not selected_row.empty:
            filtered_rows.append(selected_row)

    filtered_df = pandas.concat(filtered_rows)
    filtered_df.loc[:, 'status'] = 'MIGRUJEMY'
    return filtered_df


def get_log_file_path():
    if not os.path.exists('_logi'):
        os.makedirs('_logi')
    return '_logi'


def map_values_based_on_two_columns(dataframe: pandas.DataFrame, column_to_fill: str, column1: str, column2,
                                    map_dict) -> pandas.DataFrame:
    dataframe[column1] = dataframe[column1].astype(str).str.rstrip('.0')
    dataframe.loc[:, column_to_fill] = dataframe.apply(
        lambda row: map_dict.get((str(row[column1]), str(row[column2])), None),
        axis=1)
    return dataframe


def mapp_values(dataframe: pandas.DataFrame, column_to_fill, column_to_take, map_dict) -> pandas.DataFrame:
    dataframe.loc[:, column_to_fill] = dataframe[column_to_take].map(map_dict).fillna(dataframe[column_to_fill])
    return dataframe


def file_csv_write(dataframe: pandas.DataFrame, name_file: str, na_rep=None) -> bool:
    while True:
        try:
            name_file = os.path.join(get_log_file_path(), name_file)
            dataframe.to_csv(name_file, index=False, na_rep=na_rep)
            return True
        except PermissionError:
            time.sleep(5)


class SupportFiles(ObservableModel):
    def __init__(self):
        super().__init__()
        self._path_support_file_folder = ''
        self.file_paths_list = []
        self.progress_value = 0

    def set_path(self, path: str) -> None:
        print(f'SupportFiles: set_path(): {path}')
        self._path_support_file_folder = path

    def check_for_files(self, file_name: str) -> bool:
        """Checking if files exist and """
        if self._path_support_file_folder == '':
            path = os.path.join(os.getcwd(), 'dane')
            self.set_path(path)
        file_path = os.path.join(self._path_support_file_folder, file_name)
        #  check if path to file exist
        if os.path.exists(file_path):
            # check if file is not empty
            if os.path.getsize(file_path) > 0:
                self.file_paths_list.append(file_path)
                return True
            else:
                return False
        else:
            return False

    def create_support_file_koi(self) -> None:
        self.progress_value += 10
        koi_dataframe = pandas.read_csv(self.file_paths_list[0], sep='|', header=None)
        col_names = {0: 'numer_maestro', 1: 'nazwa_tabeli', 2: 'osobowosc', 3: 'czy_sponsor', 4: 'pesel',
                     5: 'nazwa2', 6: 'nazwa1', 7: 'imie2'}
        koi_dataframe = koi_dataframe.rename(columns=col_names)
        koi_dataframe.loc[:, 'nazwa_tabeli'] = koi_dataframe.loc[:, 'nazwa_tabeli'].str.upper()
        koi_dataframe['numer'] = koi_dataframe['numer_maestro']
        koi_dataframe['typ'] = None
        koi_dataframe = map_values_based_on_two_columns(dataframe=koi_dataframe, column_to_fill='typ',
                                                        column1='osobowosc',
                                                        column2='czy_sponsor', map_dict=dict_KOI.dict_type_mapping)
        koi_dataframe = mapp_values(dataframe=koi_dataframe, column_to_fill='typ',
                                    column_to_take='nazwa_tabeli', map_dict=dict_KOI.dict_table_name_type)
        self.progress_value += 10
        del koi_dataframe['nazwa_tabeli']
        koi_dataframe['status'] = 'NIEMIGRUJEMY'
        koi_dataframe = mapp_values(dataframe=koi_dataframe, column_to_fill='status',
                                    column_to_take='typ', map_dict=dict_KOI.dict_table_name_migration)
        koi_dataframe.loc[koi_dataframe['pesel'].isnull(), 'status'] = 'MIGRUJEMY'

        file_csv_write(koi_dataframe[['numer_maestro', 'numer', 'typ', 'pesel', 'nazwa2',
                                      'nazwa1', 'imie2', 'status']], '_reko_osoby_instytucje_file.csv', na_rep='NULL')
        self.progress_value += 10
        return

    def create_support_file_is_migrated(self) -> None:
        dataframe_oi = pandas.read_csv(self.file_paths_list[1], sep='|', header=None,
                                       low_memory=False)
        dataframe_oi = dataframe_oi.rename(columns={0: "numer", 1: "typ"}).drop(columns=[2, 3, 4, 5])
        self.progress_value += 10

        dataframe_numb = pandas.read_csv(self.file_paths_list[2], sep='|', header=None, low_memory=False)
        dataframe_numb = dataframe_numb.rename(columns={0: "numer", 1: "symbol", 2: 'wartosc'}).drop(columns=[3, 4])
        dataframe_numb = dataframe_numb[dataframe_numb['symbol'].isin(['L', 'CIF'])]
        dataframe_numb = dataframe_numb.dropna(subset=['wartosc'])
        dataframe_numb['pesel'] = numpy.where(dataframe_numb['symbol'] == 'L', dataframe_numb['wartosc'], numpy.nan)
        dataframe_numb['cif'] = numpy.where(dataframe_numb['symbol'] == 'CIF', dataframe_numb['wartosc'], numpy.nan)
        dataframe_numb = dataframe_numb.groupby('numer').agg({'pesel': 'first', 'cif': 'first'}).reset_index()
        self.progress_value += 10

        dataframe = pandas.merge(dataframe_oi, dataframe_numb, on='numer', how='inner')
        del dataframe_numb, dataframe_oi
        dataframe['status'] = 'NIEMIGRUJEMY'
        dataframe = mapp_values(dataframe=dataframe, column_to_fill='status',
                                column_to_take='typ', map_dict=dict_KOI.dict_table_name_migration)
        dataframe.loc[dataframe['pesel'].isnull(), 'status'] = 'MIGRUJEMY'
        filtered = check_type(dataframe)
        merged_df = dataframe.merge(filtered, how='left', on=['numer', 'typ', 'pesel', 'cif'],
                                    suffixes=('', '_new'))
        merged_df['status'] = merged_df['status_new'].combine_first(merged_df['status'])
        dataframe.loc[:, 'status'] = merged_df.loc[:, 'status']
        self.progress_value += 10

        dataframe_umo_osoba = dataframe.sort_values(by='status', ascending=True)
        grouped_umo_osoba = dataframe_umo_osoba.groupby('pesel')['numer'].apply(list)
        filtered_umo_osoba = grouped_umo_osoba[grouped_umo_osoba.apply(len) > 1]
        result_umo_osoba = pandas.DataFrame(filtered_umo_osoba).reset_index()
        file_csv_write(result_umo_osoba, '_reko_dla_umo_osoba.csv')
        self.progress_value += 10

        df_niemigrujemy = dataframe[dataframe['status'] == 'NIEMIGRUJEMY']
        df_migrujemy = dataframe[dataframe['status'] == 'MIGRUJEMY']
        df_niemigrujemy = df_niemigrujemy.drop(columns=['status'])
        df_migrujemy = df_migrujemy.drop(columns=['status'])
        df_is_migrated = pandas.merge(df_niemigrujemy, df_migrujemy, on='pesel', how='inner',
                                      suffixes=('_przegr', '_wygr'))
        file_csv_write(df_is_migrated, '_reko_pesel_wygr_przegr.csv')
        self.progress_value += 10

        non_migrated = pandas.DataFrame()
        non_migrated['numer'] = dataframe.loc[dataframe['status'] == 'NIEMIGRUJEMY', 'numer']
        non_migrated['typ'] = dataframe.loc[dataframe['status'] == 'ds', 'typ']
        file_csv_write(non_migrated, '_reko_plik_pomocniczy_niemigrowane_id.csv')
        self.progress_value += 100
