def convert_src(self):
    print(text_variables.do_mapp)
    df = self.src_df.copy()
    df.loc[:, 'kod_produktu'] = df.loc[:, 'kod_produktu'].str.lower()
    df.loc[:, 'nr_konta'] = df.loc[:, 'nr_konta'].str.lower()
    df['key_two'] = None
    df['key_three'] = None

    try:
        # wyliczanie id konta
        path = os.path.join(working_directory_dane, 'rfs_aneks_zagr_broker_src.txt')
        aneks_zagr_broker_df = pandas.read_csv(path, sep='|',
                                               header=None, names=['klient'], index_col=False)
        path = os.path.join(working_directory_dane, 'rfs_umowy_src.txt')
        umowy_df = pandas.read_csv(path, sep='|',
                                   header=None, names=['numer_rachunku', 'nazwa_tablicy', 'klient', 'status_umowy',
                                                       'licz_kontr', 'procent', 'limit_otp', 'rynek_zag',
                                                       'ike', 'ike_stan', 'drwnik', 'typ_klienta', 'aneks_tel',
                                                       'aneks_www'],
                                   usecols=['klient', 'numer_rachunku'], index_col=False)
        id_konta_dataframe = pandas.merge(aneks_zagr_broker_df, umowy_df, on='klient', how='inner')
        id_konta_dataframe['numer_rachunku'] = id_konta_dataframe['numer_rachunku'].astype(str)
        del aneks_zagr_broker_df, umowy_df
        path = os.path.join(working_directory_dict, 'out_dic_gielda_id_depozyt.unl')
        gielda_depozyt_df = pandas.read_csv(path, sep='|',
                                            header=None, names=['id_depozyt', 'gielda', 'KDPW', 'BZ',
                                                                'G', 'Z', 'zero', 'id_konta_qi', 'id_konta_non_qi'],
                                            usecols=['id_depozyt', 'id_konta_qi', 'id_konta_non_qi'],
                                            index_col=False)
        gielda_depozyt_df = gielda_depozyt_df.dropna(subset=['id_konta_qi', 'id_konta_non_qi'])
        # stworzenie słownika mapowania 'rynek_wyceny' na 'id_konta' jak ma aneks to ten z końcóką 0161247

        mapowanie_id_konta = gielda_depozyt_df.set_index('id_depozyt')[['id_konta_qi', 'id_konta_non_qi']].to_dict()

        def mapp_id_konta(row):
            rachunek_str = str(row['rachunek']).strip()
            if id_konta_dataframe['numer_rachunku'].isin([rachunek_str]).any():
                return mapowanie_id_konta['id_konta_non_qi'].get(row['id_depozyt'], row['id_konta'])
            else:
                return mapowanie_id_konta['id_konta_qi'].get(row['id_depozyt'], row['id_konta'])

        df['id_konta_copy'] = df['id_konta']
        df['id_konta'] = df.apply(mapp_id_konta, axis=1)
        df['id_konta'] = df['id_konta'].fillna(df['id_konta_copy'])
        df.loc[:, 'id_konta'] = df.loc[:, 'id_konta'].astype(str)
        df.loc[:, 'id_konta'] = df['id_konta'].apply(lambda x: x.replace('.0', ''))
        df.loc[df['id_konta'] != '0000000000000000', 'id_konta'] = df.loc[
            df['id_konta'] != '0000000000000000', 'id_konta'].str.lstrip('0')
        df.drop(columns=['id_konta_copy'], inplace=True)
    except:
        print('   Pominieto mapowanie id_konta dla KSGPW')

    try:
        path = os.path.join(working_directory_dict, 'out_dic_gielda_id_depozyt.unl')
        dict_gielda_depozyt_df = pandas.read_csv(path, sep='|',
                                                 header=None)
        print('   Trwa mapowanie używajac słownika out_dic_gielda_id_depozyt.unl ...')
        dict_gielda_depozyt_local = {}
        for index, row in dict_gielda_depozyt_df.iterrows():
            key = row[0]
            values = (row[1], row[2])
            dict_gielda_depozyt_local[key] = values
        df = map_values_to_columns(df, 'id_depozyt', 'gielda', 'id_depozyt', dict_gielda_depozyt_local)
    except:
        print('   Trwa mapowanie używajac lokalnego out_dic_gielda_id_depozyt.unl ...')
        df = map_values_to_columns(df, 'id_depozyt', 'gielda', 'id_depozyt', dict_gielda_depozyt)

    dict_rachunki_str = [str(rachunek) for rachunek in dict_rachunki]
    condition = df['rachunek'].isin(dict_rachunki_str)
    print(f"   Rachunki zamieniane na '13': {dict_rachunki_str}")

    df.loc[condition, 'key_three'] = df['rachunek'].astype(str) + df['nr_konta'].astype(str) + df[
        'kod_produktu'].astype(str)
    df.loc[~condition, 'key_two'] = df['nr_konta'].astype(str) + df['kod_produktu'].astype(str)

    df['klasa_konta'] = None
    df['status_aktyw'] = None

    df = map_values_to_columns(df, 'key_two', 'klasa_konta', 'status_aktyw',
                               dict_klasa_konta_status_aktyw)
    df = map_values_to_columns(df, 'key_three', 'rachunek', 'klasa_konta',
                               dict_rachunek_klasa_konta_status_aktyw, 'status_aktyw')
    del df['key_three']
    del df['key_two']
    df['rachunek_maestro'] = df['rachunek']
    df.loc[df['rachunek'].str.len() < 8, 'rachunek'] = '13'
    df['key_two'] = None
    df.loc[df['klasa_konta'] == 'nan', 'key_two'] = df['nr_konta'].astype(str) + df['kod_produktu'].astype(str)
    df = map_values_to_columns(df, 'key_two', 'klasa_konta', 'status_aktyw',
                               dict_klasa_konta_status_aktyw)
    df['rachunek'] = df['rachunek'].astype(str)
    del df['key_two']
    df = df.rename(columns={'kod_produktu': 'kod_produktu_maestro', 'nr_konta': 'nr_konta_maestro'})
    return df[['rachunek', 'kod_papieru', 'gielda', 'id_depozyt', 'status_aktyw', 'klasa_konta', 'id_konta',
               'rachunek_maestro', 'nr_konta_maestro', 'kod_produktu_maestro', 'saldo']]