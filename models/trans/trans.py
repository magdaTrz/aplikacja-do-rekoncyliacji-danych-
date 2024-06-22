import os

import numpy
import pandas
from pydispatch import dispatcher
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.report_model import ReportModel
from models.dict_update import DictUpdate
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class Trans(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path='',
                 save_folder_report_path='', path_excel_file='report.xlsx', password=None):
        super().__init__()
        print('Trans: __init__')
        self.stage = stage
        self.path_src = path_src
        self.path_ext = path_ext
        self.path_tgt = path_tgt
        self.data_folder_report_path: str = data_folder_report_path
        self.save_folder_report_path: str = save_folder_report_path
        self.path_excel: str = path_excel_file
        self.dataframe_src: pandas.DataFrame | None = None
        self.dataframe_ext: pandas.DataFrame | None = None
        self.dataframe_tgt: pandas.DataFrame | None = None
        self.summary_dataframe: pandas.DataFrame | None = None
        self.merge_statistics_dataframe: pandas.DataFrame | None = None
        self.percent_reconciliation_dataframe: pandas.DataFrame | None = None
        self.sample_dataframe: pandas.DataFrame | None = None
        self.password: None | str = password

    def _carry_operations(self) -> bool:
        print(f'Trans: _carry_operations(stage={self.stage})')

        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names(
                {0: 'nr_noty', 1: 'lp', 2: 'typ_operacji', 3: 'cena_jedn', 4: 'data_sesji', 5: 'long_kod_pw',
                 6: 'kod_rynku', 7: 'liczba_pap', 8: 'nr_rach', 9: 'data_rozlicz', 10: 'kod_waluty', 11: 'wartosc_noty',
                 12: 'wartosc_zob', 13: 'kod_operacji_lp', 14: 'id_konta', 15: 'wyplata'}, src_dataframe)

            # ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
            # ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer'}, ext_dataframe)
            # if src_dataframe.empty or ext_dataframe.empty:
            #     return False
            # else:
            self.dataframe_src = self.convert_src(src_dataframe)
            self.dataframe_ext = self.convert_ext(ext_dataframe)
            ProgresBarStatus.increase()
            return True

        if self.stage == TextEnum.END:
            ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
            ext_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer'}, ext_dataframe)
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names({0: 'numer_klienta', 1: 'symbol', 2: 'numer'}, tgt_dataframe)
            if tgt_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='numer_klienta')
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('Trans: convert_src()')

        dict_update = DictUpdate()
        dict_id_depozyt = dict_update.get_dic_gielda_id_depozyt()
        dict_kody_oper = dict_update.get_dic_kody_operacji()

        merged_dataframe = pandas.merge(dataframe, dict_id_depozyt, on='kod_rynku', how='left')

        merged_dataframe['dzien_w_roku'] = pandas.to_datetime(merged_dataframe['data_sesji'],
                                                              format='%d-%m-%Y', errors='coerce').dt.dayofyear
        merged_dataframe['rok'] = pandas.to_datetime(merged_dataframe['data_sesji'], format='%d-%m-%Y', errors='coerce').dt.strftime(
            '%y')
        merged_dataframe.loc[merged_dataframe['gielda'] == 'WWA', 'nr_noty_wyliczone'] = (
                merged_dataframe['przedrostek'].astype(str) +
                merged_dataframe['rok'].astype(str) +
                merged_dataframe['dzien_w_roku'].astype(str).str.zfill(3) +
                merged_dataframe['wyroznik'].astype(str) +
                merged_dataframe['nr_noty'].astype(str).str[-7:].str.zfill(7)
        )

        merged_dataframe.loc[merged_dataframe['gielda'] != 'WWA', 'nr_noty_wyliczone'] = (
                'ZZ' +
                merged_dataframe['rok'] +
                merged_dataframe.loc[merged_dataframe['gielda'] != 'WWA', 'lp'].astype(str).str.zfill(10)
        )
        del merged_dataframe['rok']
        del merged_dataframe['dzien_w_roku']

        merged_dataframe['cena_jedn'] = (merged_dataframe['cena_jedn']).astype(float)
        merged_dataframe['liczba_pap'] = (merged_dataframe['liczba_pap']).astype(float)
        merged_dataframe['wartosc'] = merged_dataframe['cena_jedn'] * merged_dataframe['liczba_pap']
        merged_dataframe['wartosc'] = merged_dataframe['wartosc'].apply(lambda x: self.round_math(x, decimals=2))

        merged_dataframe['numpozrozl'] = merged_dataframe['typ_operacji'].replace({'K': 1, 'S': 2})
        merged_dataframe['prowizja'] = 0
        merged_dataframe.loc[merged_dataframe['numpozrozl'] == 1, 'prowizja'] = merged_dataframe['wartosc_noty'] - \
                                                                                merged_dataframe['wartosc']

        merged_dataframe.loc[merged_dataframe['numpozrozl'] == 2, 'prowizja'] = merged_dataframe['wartosc'] - \
                                                                                merged_dataframe['wartosc_noty']

        del merged_dataframe['nr_noty']
        merged_dataframe = merged_dataframe.rename(
            columns={'nr_noty_wyliczone': 'nr_noty', 'typ_operacji': 'strona', 'cena_jedn': 'kurs',
                     'data_sesji': 'datawyk', 'long_kod_pw': 'kodpapieru',
                     'liczba_pap': 'ilosc', 'nr_rach': 'klient',
                     'data_rozlicz': 'data_rozl', 'kod_waluty': 'waluta'})
        merged_dataframe[['rko_trans', 'rko_prw', 'blk_trans', 'blk_prw', 'otp_trans', 'otp_prw',
                          'otp_rko_trans', 'otp_rko_prw', 'otp_stan']] = 0
        merged_dataframe = pandas.merge(merged_dataframe, dict_kody_oper, on='kod_operacji_lp', how='left')
        # merged_dataframe['wartosc'] = (merged_dataframe['wartosc']).astype(str)
        merged_dataframe['prowizja'] = merged_dataframe['prowizja'].round(2)
        algorithm_dataframe = self.algorithm(merged_dataframe)
        for col in ['rko_trans', 'rko_prw', 'blk_trans', 'blk_prw', 'otp_trans', 'otp_prw', 'otp_rko_trans',
                    'otp_rko_prw', 'otp_stan']:
            merged_dataframe[col] = algorithm_dataframe[col]
        del algorithm_dataframe
        return merged_dataframe[['nr_noty', 'numpozrozl', 'kodpapieru', 'gielda', 'strona', 'kurs', 'datawyk', 'ilosc', 'wartosc',
                'klient', 'data_rozl', 'waluta', 'prowizja', 'rynekzlecen', 'kdpw_tryb_obr', 'kdpw_kod_rnk',
                'id_konta', 'rko_trans', 'rko_prw', 'blk_trans', 'blk_prw', 'otp_trans', 'otp_prw', 'otp_rko_trans',
                'otp_rko_prw', 'otp_stan']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame, is_eod=False) -> pandas.DataFrame:
        print('Trans: convert_ext()')
        dataframe['prowizja'] = (dataframe['prowizja']).round(2)
        if is_eod:
            dataframe['datawyk'] = pandas.to_datetime(dataframe['datawyk'].fillna('23-09-1677'), format='%d-%m-%Y',
                                                      errors='coerce')
            dataframe['datawyk'] = dataframe['datawyk'].dt.strftime('%Y-%m-%d')
            dataframe.loc[dataframe['datawyk'] == '1677-09-23', 'datawyk'] = numpy.nan
            dataframe['data_rozl'] = pandas.to_datetime(dataframe['data_rozl'].fillna('23-09-1677'), format='%d-%m-%Y',
                                                        errors='coerce')
            dataframe['data_rozl'] = dataframe['data_rozl'].dt.strftime('%Y-%m-%d')
            dataframe.loc[dataframe['data_rozl'] == '1677-09-23', 'data_rozl'] = numpy.nan
            dataframe['wartosc'] = (dataframe['wartosc']).astype(str)
            dataframe.fillna('', inplace=True)
        return dataframe[['nr_noty', 'numpozrozl', 'kodpapieru', 'gielda', 'strona', 'kurs', 'datawyk', 'ilosc', 'wartosc',
                'klient', 'data_rozl', 'waluta', 'prowizja', 'rynekzlecen', 'kdpw_tryb_obr', 'kdpw_kod_rnk',
                'id_konta', 'rko_trans', 'rko_prw', 'blk_trans', 'blk_prw', 'otp_trans', 'otp_prw', 'otp_rko_trans',
                'otp_rko_prw', 'otp_stan']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('OiTelecom: convert_tgt()')
        return dataframe[['numer_klienta', 'symbol', 'numer']]

    def round_math(self, value, decimals=2, increase_value=0.01):
        factor = 10.0 ** decimals
        return round(value + increase_value / factor, decimals)

    def sum_bag(self, bag_dataframe):
        return bag_dataframe['wartosc_noty'].sum()

    def create_bag(self, dataframe, klient, data_rozl, data_wyk, waluta):
        data_rozl = pandas.to_datetime(data_rozl, format='%d-%m-%Y')
        data_wyk = pandas.to_datetime(data_wyk, format='%d-%m-%Y')
        # Warunek dla daty mniejszej niż data_rozl
        condition_lt = (dataframe['klient'] == klient) & (
                dataframe['data_rozl'] < data_rozl) & (dataframe['datawyk'] <= data_wyk) & (
                               dataframe['waluta'] == waluta)

        # Warunek dla daty równej data_rozl
        condition_eq = (dataframe['klient'] == klient) & (
                dataframe['data_rozl'] == data_rozl) & (dataframe['datawyk'] <= data_wyk) & (
                               dataframe['waluta'] == waluta)

        conditions = condition_lt | condition_eq
        bag = dataframe[conditions].copy()
        del dataframe
        bag.sort_values(by='lp', inplace=True)
        return bag

    def create_dataframe_form_dict(self, path_is_file, direct_path, column_names):
        working_directory = os.getcwd()
        if os.path.isfile(f'{working_directory}//{direct_path}'):
            out_dic_dataframe = self.make_dataframe_from_file(path_is_file)
            out_dic_dataframe = self.set_colum_names(column_names, out_dic_dataframe)
        else:
            out_dic_dataframe = self.make_dataframe_from_file(path_to_file='', direct_path=direct_path)
            out_dic_dataframe = self.set_colum_names(column_names, out_dic_dataframe)
        return out_dic_dataframe

    def set_colum_names(self, col_names: dict[int, str], dataframe: pandas.DataFrame) -> pandas.DataFrame:
        if not dataframe.empty:
            dataframe = self.delete_empty_columns(dataframe)
            dataframe = dataframe.rename(columns=col_names)
            return dataframe

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
                            df_trans_kup.loc[index, 'rko_trans'] = self.round_math(trans_kup_cena_bez_prowizji,
                                                                                   decimals=2,
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
                            df_trans_sprzd.loc[
                                df_trans_sprzd['lp'] == lp_zlecenia, 'wartosc_noty'] -= trans_kup_rko_trans

                            worek.loc[index_worek, 'wartosc_noty'] -= trans_kup_rko_prw
                            df_trans_sprzd.loc[df_trans_sprzd['lp'] == lp_zlecenia, 'wartosc_noty'] -= trans_kup_rko_prw

                            wartosc_worek = wartosc_worek - trans_kup_rko_trans - trans_kup_rko_prw
                            break

                    if wartosc_worek > 0:
                        trans_kup_rko_prw = wartosc_worek
                        df_trans_kup.loc[index, 'rko_prw'] = self.round_math(trans_kup_rko_prw, decimals=2,
                                                                             increase_value=0.001)
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

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"Trans(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"Trans(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["numer_klienta", "symbol"],
                    compare_cols=["numer"],
                    text_description="Numery łączności podmiotów")
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["numer_klienta", "symbol"],
                    compare_cols=["numer"],
                    text_description="Numery łączności podmiotów")
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"Trans(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({f"f2f_oi_telecom": f2f}, merge_on=["numer_klienta", "symbol"])
        except Exception as e:
            print(f"Trans(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"Trans(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True
