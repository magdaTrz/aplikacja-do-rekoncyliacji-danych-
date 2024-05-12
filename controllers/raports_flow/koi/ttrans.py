import pandas


def algorithm(self, main_dataframe):
    #  Inicjacja nowych kolumn w ramce danych, wszsytkie ustawione są na 0
    main_dataframe.sort_values(by='lp', inplace=True)
    main_dataframe['otp_trans'] = 0
    main_dataframe['otp_prw'] = 0
    main_dataframe['rko_trans'] = 0
    main_dataframe['rko_prw'] = 0
    main_dataframe['blk_trans'] = 0
    main_dataframe['blk_prw'] = 0
    main_dataframe['otp_rko_trans'] = 0
    main_dataframe['otp_rko_prw'] = 0
    main_dataframe['otp_stan'] = '-'
    #  Tworzenie ramek danych z transakcjami sprzedaży oraz przekształcenie kolumn na daty
    df_trans_sprzd = main_dataframe.loc[main_dataframe['strona'] == 'S']
    df_trans_sprzd['data_rozl'] = pandas.to_datetime(df_trans_sprzd['data_rozl'], format='%d-%m-%Y')
    df_trans_sprzd['datawyk'] = pandas.to_datetime(df_trans_sprzd['datawyk'], format='%d-%m-%Y')
    #  Tworzenie ramek danych z transakcjami kupna
    df_trans_kup = main_dataframe.loc[main_dataframe['strona'] == 'K']

    for index, row in df_trans_kup.iterrows():
        #  W pętli przetwarzana jest każda transakcja kupna
        trans_kup_nr_noty = row['nr_noty']  # object
        trans_kup_wartosc_noty = row['wartosc_noty']  # float
        trans_kup_wartosc_zob = row['wartosc_zob']  # float
        trans_kup_waluta = row['waluta']  # object
        trans_kup_klient = row['klient']  # int
        trans_kup_data_wyk = row['datawyk']
        trans_kup_data_rozl = row['data_rozl']  # object
        trans_kup_otp_trans = row['otp_trans']
        trans_kup_otp_prw = row['otp_prw']
        trans_kup_prowizja = row['prowizja']
        trans_kup_cena_bez_prowizji = row['wartosc']  # (cena_jedn * liczba_pap)

        if trans_kup_klient == 83398499:
            if trans_kup_nr_noty == 'Z2403000000339':
                pass
            pass

        if trans_kup_wartosc_zob != 0:
            #  Finansowanie noty z otp
            wspolczynnik_proporcji = trans_kup_wartosc_zob / trans_kup_wartosc_noty
            trans_kup_otp_trans = wspolczynnik_proporcji * trans_kup_cena_bez_prowizji
            trans_kup_otp_prw = wspolczynnik_proporcji * trans_kup_prowizja
            trans_kup_prowizja = trans_kup_prowizja - trans_kup_otp_prw
            trans_kup_cena_bez_prowizji = trans_kup_cena_bez_prowizji - trans_kup_otp_trans
            # zapis do dataframe
            df_trans_kup.loc[index, 'otp_trans'] = self.round_math(trans_kup_otp_trans, decimals=2,
                                                                   increase_value=0.001)
            df_trans_kup.loc[index, 'otp_prw'] = self.round_math(trans_kup_otp_prw, decimals=2,
                                                                 increase_value=0.001)
            df_trans_kup.loc[index, 'prowizja'] = trans_kup_prowizja
            df_trans_kup.loc[index, 'wartosc'] = trans_kup_cena_bez_prowizji
            trans_kup_wartosc_noty = trans_kup_cena_bez_prowizji
        else:
            #  Finansowanie nie odbywa się z otp
            df_trans_kup.loc[index, 'otp_trans'] = 0
            df_trans_kup.loc[index, 'otp_prw'] = 0

        if trans_kup_otp_trans + trans_kup_otp_prw > 0:
            #  Wyliczenie otp_stan
            df_trans_kup.loc[index, 'otp_stan'] = 'T'
        else:
            df_trans_kup.loc[index, 'otp_stan'] = '-'

        #  Tworzenie worka
        worek = self.create_bag(df_trans_sprzd, trans_kup_klient, trans_kup_data_rozl, trans_kup_data_wyk,
                                trans_kup_waluta)
        wartosc_worek = self.sum_bag(worek)

        if trans_kup_wartosc_noty <= wartosc_worek:
            #  Finansowanie noty w całości z rko
            for index_worek in worek.index:
                trans_sprzed_wartosc_noty = worek.loc[index_worek, 'wartosc_noty']
                if trans_sprzed_wartosc_noty > 0:
                    lp_zlecenia = worek.loc[index_worek, 'lp']
                    odejmowana_wartosc = min(trans_kup_wartosc_noty, trans_sprzed_wartosc_noty)

                    #  Aktualizacja worka utworzonego woka oraz dataframe z transakcjami sprzedazy
                    worek.loc[index_worek, 'wartosc_noty'] -= odejmowana_wartosc
                    wartosc_worek = self.sum_bag(worek)
                    df_trans_sprzd.loc[df_trans_sprzd['lp'] == lp_zlecenia, 'wartosc_noty'] -= odejmowana_wartosc

                    #  Aktualizacja wartości noty transakcji kupna
                    trans_kup_wartosc_noty -= odejmowana_wartosc
                    df_trans_kup.loc[index, 'wartosc_noty'] = trans_kup_wartosc_noty

                    if trans_kup_wartosc_noty <= 0:
                        #  Nota została roziczona wychodzimy z pentli
                        df_trans_kup.loc[index, 'rko_trans'] = self.round_math(trans_kup_cena_bez_prowizji, decimals=2,
                                                                               increase_value=0.001)
                        df_trans_kup.loc[index, 'rko_prw'] = self.round_math(trans_kup_prowizja, decimals=2,
                                                                             increase_value=0.001)
                        break
                    df_trans_kup.loc[index, 'rko_trans'] = self.round_math(trans_kup_cena_bez_prowizji, decimals=2,
                                                                           increase_value=0.001)
                    df_trans_kup.loc[index, 'rko_prw'] = self.round_math(trans_kup_prowizja, decimals=2,
                                                                         increase_value=0.001)
                    df_trans_kup.loc[index, 'blk_trans'] = 0
                    df_trans_kup.loc[index, 'blk_prw'] = 0
        else:
            #  Warość worka nie pozwala na całkowite poktycie transakcji wykorzytsująć rko
            if wartosc_worek > 0:
                wspolczynnik_proporcji = (wartosc_worek * trans_kup_cena_bez_prowizji) / \
                                         (trans_kup_cena_bez_prowizji + trans_kup_prowizja)
                #  Częściowe pokrycie transakcji używając rko
                trans_kup_rko_trans = wspolczynnik_proporcji
                trans_kup_rko_prw = wartosc_worek - wspolczynnik_proporcji
                df_trans_kup.loc[index, 'rko_trans'] = self.round_math(trans_kup_rko_trans, decimals=2,
                                                                       increase_value=0.001)
                df_trans_kup.loc[index, 'rko_prw'] = self.round_math(trans_kup_rko_prw, decimals=2,
                                                                     increase_value=0.001)

                for index_worek in worek.index:
                    #  Aktualizacja worka utworzonego woka oraz dataframe z transakcjami sprzedazy
                    if worek.loc[index_worek, 'wartosc_noty'] > 0:
                        #  Sprawdzane są tylko te noty których wartość jest > 0
                        lp_zlecenia = worek.loc[index_worek, 'lp']

                        worek.loc[index_worek, 'wartosc_noty'] -= trans_kup_rko_trans
                        df_trans_sprzd.loc[df_trans_sprzd['lp'] == lp_zlecenia, 'wartosc_noty'] -= trans_kup_rko_trans

                        worek.loc[index_worek, 'wartosc_noty'] -= trans_kup_rko_prw
                        df_trans_sprzd.loc[df_trans_sprzd['lp'] == lp_zlecenia, 'wartosc_noty'] -= trans_kup_rko_prw

                        wartosc_worek = wartosc_worek - trans_kup_rko_trans - trans_kup_rko_prw
                        break

                if wartosc_worek > 0:
                    trans_kup_rko_prw = wartosc_worek
                    df_trans_kup.loc[index, 'rko_prw'] = self.round_math(trans_kup_rko_prw, decimals=2,
                                                                         increase_value=0.001)
                # else:
                # trans_kup_rko_prw = 0
                # df_trans_kup.loc[index, 'rko_prw'] = 0
                trans_kup_blk_trans = trans_kup_cena_bez_prowizji - trans_kup_rko_trans
                trans_kup_blk_prw = trans_kup_prowizja - trans_kup_rko_prw
                df_trans_kup.loc[index, 'blk_trans'] = self.round_math(trans_kup_blk_trans, decimals=2,
                                                                       increase_value=0.0001)
                df_trans_kup.loc[index, 'blk_prw'] = self.round_math(trans_kup_blk_prw, decimals=2,
                                                                     increase_value=0.0001)
            else:
                #  Cała płatność następuje z blk, worek jest pusty
                trans_kup_blk_trans = trans_kup_cena_bez_prowizji
                trans_kup_blk_prw = trans_kup_prowizja
                df_trans_kup.loc[index, 'blk_trans'] = self.round_math(trans_kup_blk_trans, decimals=2,
                                                                       increase_value=0.001)
                df_trans_kup.loc[index, 'blk_prw'] = self.round_math(trans_kup_blk_prw, decimals=2,
                                                                     increase_value=0.001)

        if trans_kup_waluta != 'PLN':
            df_trans_kup.loc[index, 'otp_trans'] = 0
            df_trans_kup.loc[index, 'otp_prw'] = 0
            df_trans_kup.loc[index, 'rko_trans'] = 0
            df_trans_kup.loc[index, 'rko_prw'] = 0

        result_dataframe = pandas.concat([df_trans_sprzd, df_trans_kup])
    return result_dataframe