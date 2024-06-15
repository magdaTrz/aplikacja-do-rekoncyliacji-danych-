class SaldaFin:
    def __init__(self, src_df=None, ext_df=None, tgt_df=None, excel_path=""):
        print("Salda Finansowe Klienckie")
        self.src_df = src_df
        self.ext_df = ext_df
        self.tgt_df = tgt_df
        self.excel_path = excel_path
        self.carry_operation()

    def carry_operation(self):
        balance_accounts = ['24504', '24505', '24506', '24507', '24508']
        self.add_column_names()
        if self.src_df is not None and self.ext_df is not None:
            self.src_df = self.src_df[self.src_df['rachunek'] != 13]
            self.ext_df = self.ext_df[self.ext_df['rachunek'] != 13]
            src_Maestro = self.convert_src()
            converted_src = src_Maestro[['rachunek', 'konto', 'subkonto', 'waluta', 'czy_konto_pdst_klienta', 'saldo',
                                         'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]
            converted_ext = self.convert_ext()
            del self.src_df, self.ext_df
            print(text_variables.do_report)
            report = ExcelReport(self.excel_path)

            '''Raport waluta|saldo'''
            waluta_df_src = converted_src[['waluta', 'saldo']].copy()
            waluta_df_ext = converted_ext[['waluta', 'saldo']].copy()
            waluta_df_src = waluta_df_src.groupby(['waluta'], as_index=False)['saldo'].sum()
            waluta_df_ext = waluta_df_ext.groupby(['waluta'], as_index=False)['saldo'].sum()
            report.field_to_field_load(df_1=waluta_df_src, df_2=waluta_df_ext,
                                       sheet_name="waluta_klient_suma_sald",
                                       merge_on=['waluta'])
            del waluta_df_ext

            '''Raport oznaczeniaMaestro'''
            saldo_df_src = src_Maestro.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'],as_index=False).agg({
                'saldo': 'sum',
                'konto_Maestro': 'first',
                'subkonto_Maestro': 'first',
                'subkonto_pdst_Maestro': 'first',
                'spw_r_Maestro': 'first',
                'nr_swiadectwa_Maestro': 'first',
                'kod_papieru_Maestro': 'first'
            })
            saldo_df_ext = converted_ext.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'], as_index=False)['saldo'].sum()
            del src_Maestro, converted_ext,

            pandas.set_option('display.float_format', '{:.2f}'.format)
            saldo_df_src = saldo_df_src.astype({'konto': str, 'subkonto': str})
            saldo_df_ext = saldo_df_ext.astype({'konto': str, 'subkonto': str})
            report.field_to_field_load(
                df_1=saldo_df_src[['rachunek', 'konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro',
                                   'subkonto_pdst_Maestro', 'spw_r_Maestro', 'nr_swiadectwa_Maestro',
                                   'kod_papieru_Maestro', 'saldo']],
                df_2=saldo_df_ext[['rachunek', 'konto', 'subkonto', 'waluta', 'saldo']],
                sheet_name="rach_klient_suma_sald",
                merge_on=['rachunek', 'konto', 'subkonto', 'waluta'],
                maestro_keys=['konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro',
                              'spw_r_Maestro', 'nr_swiadectwa_Maestro', 'kod_papieru_Maestro'])

            waluty = saldo_df_src['waluta'].unique().tolist()
            for waluta in waluty:
                saldo_df_src_filtered = saldo_df_src[saldo_df_src['waluta'] == waluta]
                saldo_df_ext_filtered = saldo_df_ext[saldo_df_ext['waluta'] == waluta]

                if not saldo_df_src_filtered.empty and not saldo_df_ext_filtered.empty:
                    sheet_name = f"rach_klient_{waluta.lower()}"

                    report.field_to_field_load(
                        df_1=saldo_df_src_filtered[
                            ['rachunek', 'konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro',
                             'subkonto_pdst_Maestro', 'spw_r_Maestro', 'nr_swiadectwa_Maestro',
                             'kod_papieru_Maestro', 'saldo']],
                        df_2=saldo_df_ext_filtered[['rachunek', 'konto', 'subkonto', 'waluta', 'saldo']],
                        sheet_name=sheet_name,
                        merge_on=['rachunek', 'konto', 'subkonto', 'waluta'],
                        maestro_keys=['konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro',
                                      'spw_r_Maestro', 'nr_swiadectwa_Maestro', 'kod_papieru_Maestro']
                    )
                    del saldo_df_src_filtered, saldo_df_ext_filtered
            report.save_report()

            elif self.ext_df is not None and self.tgt_df is not None:
            self.ext_df = self.ext_df[self.ext_df['rachunek'] != 13]
            self.tgt_df = self.tgt_df[self.tgt_df['rachunek'] != 13]
            self.tgt_df = self.tgt_df[self.tgt_df['saldo'] != 0]

            converted_ext = self.convert_ext(is_eod=True)
            converted_tgt = self.convert_tgt()
            del self.ext_df
            print(text_variables.do_report)
            report = ExcelReport(self.excel_path)

            '''Raport waluta|konto|saldo'''
            waluta_df_ext = converted_ext[['waluta', 'konto', 'saldo']].copy()
            waluta_df_tgt = converted_tgt[['waluta', 'konto', 'saldo']].copy()
            waluta_df_tgt = waluta_df_tgt[~waluta_df_tgt['konto'].isin(balance_accounts)]
            waluta_df_ext = waluta_df_ext.groupby(['waluta'], as_index=False)['saldo'].sum()
            waluta_df_tgt = waluta_df_tgt.groupby(['waluta'], as_index=False)['saldo'].sum()
            report.field_to_field_target(df_1=waluta_df_ext, df_2=waluta_df_tgt,
                                         sheet_name="waluta_klient_suma_sald",
                                         merge_on=['waluta'])
            del waluta_df_ext

            '''Raport oznaczeniaMaestro'''
            saldo_df_ext = converted_ext.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'],
                as_index=False)['saldo'].sum()
            saldo_df_tgt = converted_tgt.groupby(
                ['rachunek', 'konto', 'subkonto', 'waluta'],
                as_index=False)['saldo'].sum()
            pandas.set_option('display.float_format', '{:.2f}'.format)
            saldo_df_ext = saldo_df_ext.astype({'konto': str, 'subkonto': str})
            saldo_df_tgt = saldo_df_tgt.astype({'konto': str, 'subkonto': str})
            saldo_df_tgt = saldo_df_tgt[~saldo_df_tgt['konto'].isin(balance_accounts)]
            # report.field_to_field_target(df_1=saldo_df_ext, df_2=saldo_df_tgt,
            #                              sheet_name="rach_klient_suma_sald",
            #                              merge_on=['rachunek', 'konto', 'subkonto', 'waluta'],
            #                              maestro_keys=['konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro',
            #                                            'spw_r_Maestro'])

            waluty = saldo_df_ext['waluta'].unique().tolist()
            for waluta in waluty:
                saldo_df_ext_filtered = saldo_df_ext[saldo_df_ext['waluta'] == waluta]
                saldo_df_tgt_filtered = saldo_df_tgt[saldo_df_tgt['waluta'] == waluta]

                if not saldo_df_tgt_filtered.empty and not saldo_df_ext_filtered.empty:
                    sheet_name = f"rach_klient_{waluta.lower()}"

                    # report.field_to_field_target(
                    #     df_1=saldo_df_ext_filtered,
                    #     df_2=saldo_df_tgt_filtered,
                    #     sheet_name=sheet_name,
                    #     merge_on=['rachunek', 'konto', 'subkonto', 'waluta'],
                    #     maestro_keys=['konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro','spw_r_Maestro']
                    # )
                    del saldo_df_ext_filtered, saldo_df_tgt_filtered
            report.save_report()

            '''Raport SRC - TGT'''
            timestamp = get_timestamp()
            try:
                print('Raport Maestro-Promak')
                working_directory = os.getcwd()
                working_directory_dane = os.path.join(working_directory, 'dane')
                self.src_df = pandas.read_csv(fr'{working_directory_dane}\rfs_salda_fin_src.txt', sep='|',
                                              header=None, low_memory=False)
                src_column_names = {0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto',
                                    4: 'subkonto_pdst',
                                    5: 'spw_r', 6: 'waluta', 7: 'czy_saldo_wn', 8: 'saldo', 9: 'rach_13',
                                    10: 'konto_13',
                                    11: 'subkonto_13', 12: 'strona_13', 13: 'nr_swiadectwa_Maestro',
                                    14: 'kod_papieru_Maestro'}
                self.src_df = delete_empty_column(self.src_df)
                self.src_df = self.src_df.rename(columns=src_column_names)
                self.src_df = self.src_df[self.src_df['rachunek'] != 13]
                src_Maestro = self.convert_src()
                converted_src = src_Maestro[
                    ['rachunek', 'konto', 'subkonto', 'waluta', 'czy_konto_pdst_klienta', 'saldo',
                     'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]

                converted_tgt = self.convert_tgt()

                working_directory_report = os.path.join(working_directory,
                                                        f'PromakNext_RekomendacjaObszaru_Reko_FIN_{timestamp}.xlsx')
                report_maestro_promak = ExcelReport(working_directory_report)

                '''Raport waluta|saldo'''
                waluta_df_src = converted_src[['waluta', 'saldo']].copy()
                waluta_df_src = waluta_df_src.groupby(['waluta'], as_index=False)['saldo'].sum()
                waluta_df_tgt = converted_tgt[['waluta', 'saldo']].copy()
                waluta_df_tgt = waluta_df_tgt.groupby(['waluta'], as_index=False)['saldo'].sum()
                report_maestro_promak.field_to_field_load(df_1=waluta_df_src, df_2=waluta_df_tgt,
                                                          sheet_name="waluta_klient_suma_sald",
                                                          merge_on=['waluta'],
                                                          description=text_variables.description_fin_maestro_vs_promak_1)
                del waluta_df_src, waluta_df_tgt

                saldo_df_src = src_Maestro.groupby(
                    ['rachunek', 'konto', 'subkonto', 'waluta'], as_index=False).agg({
                    'saldo': 'sum',
                    'konto_Maestro': 'first',
                    'subkonto_Maestro': 'first',
                    'subkonto_pdst_Maestro': 'first',
                    'spw_r_Maestro': 'first',
                    'nr_swiadectwa_Maestro': 'first',
                    'kod_papieru_Maestro': 'first',
                })
                saldo_df_src = saldo_df_src.astype({'konto': str, 'subkonto': str})

                con_1 = (saldo_df_src['subkonto'] == '80100')
                con_2 = (saldo_df_src['saldo'] < 0)
                saldo_df_src.loc[(con_1 & con_2), 'subkonto'] = '802'

                report_maestro_promak.field_to_field_load(
                    df_1=saldo_df_src[['rachunek', 'konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro',
                                       'subkonto_pdst_Maestro', 'spw_r_Maestro', 'nr_swiadectwa_Maestro',
                                       'kod_papieru_Maestro', 'saldo']],
                    df_2=saldo_df_tgt[['rachunek', 'konto', 'subkonto', 'waluta', 'saldo']],
                    sheet_name="rach_klient_suma_sald",
                    merge_on=['rachunek', 'konto', 'subkonto', 'waluta'],
                    maestro_keys=['konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro', 'spw_r_Maestro',
                                  'nr_swiadectwa_Maestro', 'kod_papieru_Maestro'],
                    description=text_variables.description_fin_maestro_vs_promak_1)

                src_Maestro = src_Maestro.astype({'konto': str, 'subkonto': str})
                saldo_konto_sub_wal_src = src_Maestro.groupby(
                    ['konto', 'subkonto', 'waluta'], as_index=False).agg({
                    'saldo': 'sum',
                    'konto_Maestro': 'first',
                    'subkonto_Maestro': 'first',
                    'subkonto_pdst_Maestro': 'first',
                    'spw_r_Maestro': 'first',
                    'nr_swiadectwa_Maestro': 'first',
                    'kod_papieru_Maestro': 'first',
                })
                saldo_df_tgt = saldo_df_tgt.astype({'konto': str, 'subkonto': str})
                saldo_konto_sub_wal_tgt = saldo_df_tgt.groupby(
                    ['konto', 'subkonto', 'waluta'], as_index=False).agg({
                    'saldo': 'sum'
                })

                report_maestro_promak.field_to_field_load(
                    df_1=saldo_konto_sub_wal_src[['konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro',
                                                  'subkonto_pdst_Maestro', 'spw_r_Maestro', 'nr_swiadectwa_Maestro',
                                                  'kod_papieru_Maestro', 'saldo']],
                    df_2=saldo_konto_sub_wal_tgt[['konto', 'subkonto', 'waluta', 'saldo']],
                    sheet_name="konto_subkonto_waluta",
                    merge_on=['konto', 'subkonto', 'waluta'],
                    maestro_keys=['konto_Maestro', 'subkonto_Maestro', 'subkonto_pdst_Maestro', 'spw_r_Maestro',
                                  'nr_swiadectwa_Maestro', 'kod_papieru_Maestro'])

                del saldo_df_src, saldo_df_tgt

                report_maestro_promak.save_report()
            except FileNotFoundError:
                print(f'   Pominięto wykonywanie raportu PromakNext_RekomendacjaObszaru_Reko_FIN_{timestamp}.xlsx')
        else:
            print(text_variables.wrong_inputs)

        def add_column_names(self):
            src_column_names = {0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto',
                                4: 'subkonto_pdst',
                                5: 'spw_r', 6: 'waluta', 7: 'czy_saldo_wn', 8: 'saldo', 9: 'rach_13', 10: 'konto_13',
                                11: 'subkonto_13', 12: 'strona_13', 13: 'nr_swiadectwa_Maestro',
                                14: 'kod_papieru_Maestro'}
            ext_column_names = {0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto', 4: 'waluta',
                                5: 'czy_saldo_wn', 6: 'saldo', 7: 'rach_13', 8: 'konto_13',
                                9: 'subkonto_13', 10: 'strona_13'}
            tgt_column_names = {0: 'rachunek', 1: 'konto', 2: 'czy_konto_pdst_klienta', 3: 'subkonto', 4: 'waluta',
                                5: 'czy_saldo_wn', 6: 'saldo', 7: 'rach_13', 8: 'konto_13',
                                9: 'subkonto_13', 10: 'strona_13', 11: 'numerf'}
            try:
                self.ext_df = delete_empty_column(self.ext_df)
                self.ext_df = self.ext_df.rename(columns=ext_column_names)
                if self.tgt_df is not None:
                    self.tgt_df = delete_empty_column(self.tgt_df)
                    self.tgt_df = self.tgt_df.rename(columns=tgt_column_names)
                elif self.src_df is not None:
                    self.src_df = delete_empty_column(self.src_df)
                    self.src_df = self.src_df.rename(columns=src_column_names)
            except pandas.errors.ParserError:
                print(text_variables.quantity_col)

        def convert_src(self):
            df_c = self.src_df.copy()
            print(text_variables.do_mapp)
            df_c['key_three'] = None
            df_c['key_four'] = None

            try:
                df_c['czy_sponsor'] = df_c.apply(
                    lambda row: 'T' if str(row['nr_swiadectwa_Maestro']).lstrip('0') != str(row['rachunek']) else 'F',
                    axis=1)
                df_c.loc[df_c['czy_sponsor'] == 'F', ['nr_swiadectwa_Maestro', 'kod_papieru_Maestro']] = None
            except:
                print("   Błąd kolumn pomocniczych: ['nr_swiadectwa_Maestro','kod_papieru_Maestro']")
            dict_konto_fin = [konto for konto in _dict_konto_fin]
            df_c['konto_Maestro'] = df_c['konto']
            df_c['subkonto_Maestro'] = df_c['subkonto']
            df_c['subkonto_pdst_Maestro'] = df_c['subkonto_pdst']
            df_c['spw_r_Maestro'] = df_c['spw_r']

            condition = df_c['konto'].isin(dict_konto_fin)
            df_c.loc[:, 'subkonto'] = df_c.loc[:, 'subkonto'].astype(str).str.lstrip('0')
            df_c.loc[:, 'subkonto_pdst'] = df_c.loc[:, 'subkonto_pdst'].astype(str).str.lstrip('0')

            df_c.loc[condition, 'key_four'] = df_c['konto'].astype(str) + df_c['subkonto'].astype(str) \
                                              + df_c['subkonto_pdst'].astype(str) + df_c['spw_r'].astype(str)
            df_c.loc[~condition, 'key_three'] = df_c['konto'].astype(str) + df_c['subkonto'].astype(str) \
                                                + df_c['subkonto_pdst'].astype(str)
            condition_2 = (df_c['konto'] == 139)
            condition_3 = (df_c['subkonto'].isin(['23', '24', '25', '26', '27', '22']))
            df_c.loc[(condition_2 & condition_3), 'key_three'] = df_c['konto'].astype(str) + df_c['subkonto'].astype(
                str) \
                                                                 + df_c['subkonto_pdst'].astype(str)

            df_c = map_values_to_columns(df_c, 'key_three', 'konto', 'subkonto', _dict_konto_subkonto)
            df_c = map_values_to_columns(df_c, 'key_four', 'konto', 'subkonto', _dict_spwr_konto_subkonto)

            del df_c['key_three']
            del df_c['key_four']
            return df_c[
                ['rachunek', 'konto', 'subkonto', 'waluta', 'konto_Maestro', 'subkonto_Maestro',
                 'subkonto_pdst_Maestro',
                 'spw_r_Maestro', 'nr_swiadectwa_Maestro', 'kod_papieru_Maestro', 'czy_saldo_wn',
                 'czy_konto_pdst_klienta',
                 'saldo', 'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]

        def convert_ext(self, is_eod=False):
            print(text_variables.do_mapp)
            df_c = self.ext_df.copy()
            df_c.loc[:, 'konto'] = df_c.loc[:, 'konto'].astype(str)
            df_c.loc[:, 'subkonto'] = df_c.loc[:, 'subkonto'].astype(str).str.lstrip('0')
            if is_eod:
                con_1 = (df_c['subkonto'] == '80100')
                con_2 = (df_c['saldo'] < 0)
                df_c.loc[(con_1 & con_2), 'subkonto'] = '80200'
            return df_c[['rachunek', 'konto', 'subkonto', 'waluta', 'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo',
                         'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]

        def convert_tgt(self):
            print(text_variables.do_mapp)
            df_c = self.tgt_df.copy()
            df_c.loc[:, 'konto'] = df_c.loc[:, 'konto'].astype(str)
            df_c.loc[:, 'subkonto'] = df_c.loc[:, 'subkonto'].astype(str)
            df_c.loc[:, 'konto'] = df_c['konto'].apply(lambda x: x.replace('.0', ''))
            df_c.loc[:, 'subkonto'] = df_c['subkonto'].apply(lambda x: x.replace('.0', ''))
            df_c.loc[:, 'subkonto'] = df_c.loc[:, 'subkonto'].str.lstrip('0')
            return df_c[['rachunek', 'konto', 'subkonto', 'waluta', 'czy_saldo_wn', 'czy_konto_pdst_klienta', 'saldo',
                         'rach_13', 'konto_13', 'subkonto_13', 'strona_13']]