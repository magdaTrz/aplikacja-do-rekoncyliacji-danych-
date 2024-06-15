import os

import numpy
import pandas

from pydispatch import dispatcher
from controllers.progress_bar import ProgresBarStatus
from models.excel_report import ExcelReport
from models.koi import dict_KOI
from models.report_model import ReportModel
from models.support_files import mapp_values
from text_variables import TextEnum

UPDATE_TEXT_SIGNAL = 'update_text'


class Umowy(ReportModel):
    def __init__(self, stage: str, path_src=None, path_ext=None, path_tgt=None, data_folder_report_path='',
                 save_folder_report_path='', path_excel_file='report.xlsx', password=None):
        super().__init__()
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
        print(f'Umowy: _carry_operations(stage={self.stage})')

        ext_dataframe = self.make_dataframe_from_file(self.path_ext, self.data_folder_report_path)
        ext_dataframe = self.set_colum_names(
            {0: 'rachunek', 1: 'numer_klienta', 2: 'status_umowy', 3: 'typ_rachunku', 4: 'rachunek_nrb',
             5: 'procent', 6: 'limit_otp', 7: 'typumowy', 8: 'rynek_zag', 9: 'blokada', 10: 'typ_blokady',
             11: 'ike', 12: 'ike_stan', 13: 'typ_klienta', 14: 'drwnik'
             }, ext_dataframe)
        if self.stage == TextEnum.LOAD:
            src_dataframe = self.make_dataframe_from_file(self.path_src, self.data_folder_report_path)
            src_dataframe = self.set_colum_names(
                {0: "rachunek", 1: "nazwa_tablicy", 2: "numer_klienta", 3: "status_umowy", 4: "licz_kontr",
                 5: 'procent', 6: 'limit_otp', 7: 'rynek_zag', 8: 'ike', 9: 'ike_stan', 10: 'drwnik', 11: 'typ_klienta',
                 12: 'aneks_tel', 13: 'aneks_www'
                 }, src_dataframe)

            if src_dataframe.empty or ext_dataframe.empty:
                return False
            else:
                self.dataframe_src = self.convert_src(src_dataframe)
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                ProgresBarStatus.increase()
                return True

        if self.stage == TextEnum.END:
            tgt_dataframe = self.make_dataframe_from_file(self.path_tgt, self.data_folder_report_path)
            tgt_dataframe = self.set_colum_names(
                {0: 'rachunek', 1: 'numer_klienta', 2: 'status_umowy', 3: 'typ_rachunku', 4: 'rachunek_nrb',
                 5: 'procent', 6: 'limit_otp', 7: 'typumowy', 8: 'rynek_zag', 9: 'blokada', 10: 'typ_blokady',
                 11: 'ike', 12: 'ike_stan', 13: 'typ_klienta', 14: 'drwnik'
                 }, tgt_dataframe)

            if ext_dataframe.empty or tgt_dataframe.empty:
                return False
            else:
                ext_dataframe = self.delete_unmigrated_records(ext_dataframe, column_name='numer_klienta')
                self.dataframe_ext = self.convert_ext(ext_dataframe)
                self.dataframe_tgt = self.convert_tgt(tgt_dataframe)
                ProgresBarStatus.increase()
                return True

    def convert_src(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.loc[:, 'nazwa_tablicy'] = dataframe.loc[:, 'nazwa_tablicy'].str.upper()
        dataframe.loc[:, 'typ_klienta'] = dataframe.loc[:, 'typ_klienta'].str.upper()
        dataframe.loc[:, 'ike'] = dataframe.loc[:, 'ike'].str.upper()

        dataframe.loc[:, 'typ_blokady'] = None
        dataframe = mapp_values(
            dataframe=dataframe,
            column_to_fill='typ_blokady',
            column_to_take='status_umowy',
            map_dict={
                1: 'INNA',
                2: 'KOMORNICZA',
                3: 'OS.MAŁOLETNIA',
                4: 'INTERNETOWA',
                5: 'NIEODNOTOWANE_PW',
                6: 'INNA',
                7: 'PROFIT4U',
                8: 'ZGON',
                9: 'AML',
                10: 'UPADŁOŚĆ',
            })

        dataframe.loc[dataframe['status_umowy'].isnull(), 'status_umowy'] = 'A'
        dataframe.loc[(dataframe['status_umowy'] != 0) & (dataframe['status_umowy'] != 'A'), 'status_umowy'] = 'B'
        dataframe.loc[dataframe['status_umowy'] == 0, 'status_umowy'] = 'A'
        dataframe.loc[dataframe['nazwa_tablicy'] == 'REJ_NAL_SPON', 'status_umowy'] = 'A'

        dataframe.loc[:, 'typ_rachunku'] = None
        dataframe = mapp_values(
            dataframe=dataframe,
            column_to_fill='typ_rachunku',
            column_to_take='nazwa_tablicy',
            map_dict={
                'KLIENCI': 'AR',
                'ZEWNETRZNY': 'AR',
                'REJ_PW_SPON': 'AS',
                'REJ_NAL_SPON': 'AS',
            }
        )
        dataframe.loc[dataframe['ike'] == 'TAK', 'typ_rachunku'] = 'AI'

        dataframe.loc[:, "rachunek_nrb"] = None
        dataframe = self.map_values_rachunek_nrb(
            dataframe=dataframe,
            column_to_fill="rachunek_nrb",
            column1="licz_kontr",
            column2="rachunek"
        )

        dataframe.loc[:, "typumowy"] = None
        dataframe = self.map_values_based_on_two_columns(
            dataframe=dataframe,
            column_to_fill="typumowy",
            column1="aneks_www",
            column2="aneks_tel",
            map_dict={
                ("TAK", "TAK"): "T,W",
                ("NIE", "TAK"): "T",
                ("TAK", "NIE"): "T,W",
            }
        )
        dataframe.loc[:, 'blokada'] = None
        dataframe = mapp_values(dataframe=dataframe, column_to_fill='blokada', column_to_take='status_umowy',
                                map_dict={
                                    "A": "NIE",
                                    "B": "TAK",
                                })

        dataframe.loc[(dataframe['ike'] == 'TAK') & (dataframe['ike_stan'] == 'T'), 'ike_stan'] = 'O'
        dataframe.loc[(dataframe['ike'] == 'TAK') & (dataframe['ike_stan'] == 'N'), 'ike_stan'] = 'A'
        dataframe.loc[(dataframe['ike'] == 'NIE'), 'ike_stan'] = numpy.nan

        dataframe = mapp_values(
            dataframe=dataframe,
            column_to_fill='typ_klienta',
            column_to_take='typ_klienta',
            map_dict={"W": "0"}
        )
        dataframe.loc[:, 'rachunek'] = dataframe.loc[:, 'rachunek'].astype(int)

        mask = (dataframe['nazwa_tablicy'] != 'KLIENCI')
        dataframe.loc[mask, 'rynek_zag'] = 'NIE'
        dataframe.loc[mask, 'ike'] = 'NIE'
        dataframe.loc[mask, 'drwnik'] = 'NIE'
        dataframe.loc[mask, 'blokada'] = 'NIE'

        dataframe = dataframe.rename(columns={
            'ike': 'ike_aneks',
            'procent': 'procent_srodkow',
            'rynek_zag': 'zagr_aneks',
            'drwnik': 'derywaty_aneks'}
        )
        dataframe.fillna('', inplace=True)

        return dataframe[
            ['rachunek', 'numer_klienta', 'status_umowy', 'typ_rachunku', 'rachunek_nrb', 'procent_srodkow',
             'limit_otp', 'typumowy', 'zagr_aneks', 'blokada', 'typ_blokady', 'ike_aneks', 'ike_stan',
             'typ_klienta', 'derywaty_aneks']]

    @staticmethod
    def convert_ext(dataframe: pandas.DataFrame, is_eod: bool = False) -> pandas.DataFrame:
        if is_eod:
            try:
                df_pesel_numer = pandas.reaf_csv('_reko_pesel_wygr_przegr.csv', sep="|")
                dataframe = overwrite_nonmigrated_client(df_pesel_numer, dataframe)
            except:
                print(f'   Pominięto nadpisywanie niemigrowanych klientów w f2f_umowy. '
                      f'Dodaj plik _reko_pesel_wygr_przegr.csv do folderu.')
                pass
            condition1 = dataframe['ike'] == 'TAK'
            condition2 = dataframe['ike_stan'] == 'O'
            dataframe.loc[(condition1) & (condition2), 'status_umowy'] = 'B'
        dataframe.fillna('', inplace=True)
        df_ = dataframe.rename(columns={'ike': 'ike_aneks', 'procent': 'procent_srodkow', 'rynek_zag': 'zagr_aneks',
                                        'drwnik': 'derywaty_aneks'})

        return df_[
            ['rachunek', 'numer_klienta', 'status_umowy', 'typ_rachunku', 'rachunek_nrb', 'procent_srodkow',
             'limit_otp', 'typumowy', 'zagr_aneks', 'blokada', 'typ_blokady', 'ike_aneks', 'ike_stan',
             'typ_klienta', 'derywaty_aneks']]

    @staticmethod
    def convert_tgt(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        dataframe.fillna('', inplace=True)
        if 'typ_klienta' not in dataframe.columns:
            dataframe['typ_klienta'] = None

        dataframe = dataframe.astype({'numer': str})
        mask_82 = dataframe['numer'].str.startswith('82')
        dataframe.loc[mask_82, 'rachunek_nrb'] = ''

        dataframe = dataframe.rename(
            columns={'ike': 'ike_aneks',
                     'procent': 'procent_srodkow',
                     'rynek_zag': 'zagr_aneks',
                     'drwnik': 'derywaty_aneks'}
        )

        return dataframe[
            ['rachunek', 'numer_klienta', 'status_umowy', 'typ_rachunku', 'rachunek_nrb', 'procent_srodkow',
             'limit_otp', 'typumowy', 'zagr_aneks', 'blokada', 'typ_blokady', 'ike_aneks', 'ike_stan',
             'typ_klienta', 'derywaty_aneks']]

    def map_values_rachunek_nrb(self, dataframe, column_to_fill, column1, column2):
        mask = dataframe[column1].notna() & (dataframe[column1] != 0)
        try:
            dataframe[column1] = [str(int(x)) if x.is_integer() else str(x) for x in dataframe[column1]]
        except AttributeError:
            dataframe[column1] = [str(int(x)) if x else str(x) for x in dataframe[column1]]

        dataframe.loc[mask, column_to_fill] = (dataframe.loc[mask, column1].astype(str).str.zfill(2) + '10901867' +
                                               dataframe.loc[mask, column2].astype(str).str.zfill(16))
        return dataframe

    def map_values_based_on_two_columns(self, dataframe, column_to_fill, column1, column2, map_dict):
        key_column = tuple(zip(dataframe[column1], dataframe[column2]))
        dataframe[column_to_fill] = None
        mapped_values = pandas.Series(key_column).map(map_dict)
        dataframe[column_to_fill] = dataframe[column_to_fill].combine_first(mapped_values)
        return dataframe

    def create_report(self) -> TextEnum | bool:
        self.path_excel = self.modify_filename(self.path_excel, self.stage)
        print(f"Umowy(): create_report({self.path_excel}  {self.save_folder_report_path})")
        try:
            path_to_excel_file = os.path.join(self.save_folder_report_path, self.path_excel)
            excel_workbook = ExcelReport(path_to_excel_file, self.stage)
        except Exception as e:
            print(f"Umowy(): create_report  Error tworzenia excela : {e}")
            return TextEnum.EXCEL_ERROR

        try:
            if self.stage == TextEnum.LOAD:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_src,
                    dataframe_2=self.dataframe_ext,
                    merge_on_cols=["rachunek"],
                    compare_cols=['numer_klienta', 'status_umowy', 'typ_rachunku', 'rachunek_nrb', 'procent_srodkow',
                                  'limit_otp', 'typumowy', 'zagr_aneks', 'blokada', 'typ_blokady', 'ike_aneks',
                                  'ike_stan', 'typ_klienta', 'derywaty_aneks'],
                    text_description="Umowy o prowadzenie rachunków papierów wartościowych")
                checksum_drwik = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts="derywaty_aneks",
                    text_description="Sprawdzenie sumy kontrolnej rejestrów o prowadzenie rachunku zabezpieczającego"
                )
                checksum_ike = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts="ike_aneks",
                    text_description="Sprawdzenie sumy kontrolnej rejestrów o prowadzenie rachunku "
                                     "Indywidualnego Konta Emerytalnego"
                )
                checksum_zagr = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts="zagr_aneks",
                    text_description="Sprawdzenie sumy kontrolnej umów o składanie zleceń na rynkach zagraniczych"
                )
                checksum_typumo = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts="typumowy",
                    text_description="Sprawdzenie sumy kontrolnej umów o zdalne składanie zleceń"
                )
                checksum_typrach = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts="typ_rachunku",
                    text_description="Sprawdzenie sumy kontrolnej typów umów podmiotów"
                )
                checksum_statusumo = excel_workbook.check_sum(
                    dataframe1=self.dataframe_src,
                    dataframe2=self.dataframe_ext,
                    column_to_counts="status_umowy",
                    text_description="Sprawdzenie sumy kontrolnej statisów umów"
                )
            elif self.stage == TextEnum.END:
                f2f = excel_workbook.create_f2f_report(
                    dataframe_1=self.dataframe_ext,
                    dataframe_2=self.dataframe_tgt,
                    merge_on_cols=["rachunek"],
                    compare_cols=['numer_klienta', 'status_umowy', 'typ_rachunku', 'rachunek_nrb', 'procent_srodkow',
                                  'limit_otp', 'typumowy', 'zagr_aneks', 'blokada', 'typ_blokady', 'ike_aneks',
                                  'ike_stan', 'typ_klienta', 'derywaty_aneks'],
                    text_description="Umowy o prowadzenie rachunków papierów wartościowych")
                checksum_drwik = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts="derywaty_aneks",
                    text_description="Sprawdzenie sumy kontrolnej rejestrów o prowadzenie rachunku zabezpieczającego"
                )
                checksum_ike = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts="ike_aneks",
                    text_description="Sprawdzenie sumy kontrolnej rejestrów o prowadzenie rachunku "
                                     "Indywidualnego Konta Emerytalnego"
                )
                checksum_zagr = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts="zagr_aneks",
                    text_description="Sprawdzenie sumy kontrolnej umów o składanie zleceń na rynkach zagraniczych"
                )
                checksum_typumo = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts="typumowy",
                    text_description="Sprawdzenie sumy kontrolnej umów o zdalne składanie zleceń"
                )
                checksum_typrach = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts="typ_rachunku",
                    text_description="Sprawdzenie sumy kontrolnej typów umów podmiotów"
                )
                checksum_statusumo = excel_workbook.check_sum(
                    dataframe1=self.dataframe_ext,
                    dataframe2=self.dataframe_tgt,
                    column_to_counts="status_umowy",
                    text_description="Sprawdzenie sumy kontrolnej statisów umów"
                )
            self.summary_dataframe = excel_workbook.summary_dataframe
            self.merge_statistics_dataframe = excel_workbook.merge_statistics_dataframe
            self.percent_reconciliation_dataframe = excel_workbook.percent_reconciliation_dataframe
            self.sample_dataframe = excel_workbook.sample_dataframe
        except Exception as e:
            print(f"Umowy(): create_report  Error tworzenia raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd tworzenia raportu {e}", head='error')
            return TextEnum.CREATE_ERROR

        try:
            excel_workbook.save_to_excel({"f2f_oi_adresy": f2f,
                                          "check_sum_umowy_status_umowy": checksum_drwik,
                                          "check_sum_umowy_status_umowy": checksum_ike,
                                          "check_sum_umowy_status_umowy": checksum_zagr,
                                          "check_sum_umowy_status_umowy": checksum_typumo,
                                          "check_sum_umowy_status_umowy": checksum_typrach,
                                          "check_sum_umowy_status_umowy": checksum_statusumo,
                                          }, merge_on=["numer_klienta", "typ"])
        except Exception as e:
            print(f"Umowy(): create_report  Error zapisywania raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd zapisywania raportu {e}", head='error')
            return TextEnum.SAVE_ERROR

        try:
            excel_workbook.add_password_to_excel(self.path_excel, self.password)
        except Exception as e:
            print(f"Umowy(): add_password_to_excel  Error dodawania hasła do raportu : {e}")
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd dodawania hasła do raportu {e}", head='error')
        return True


def overwrite_nonmigrated_client(wygr_przegr_dataframe, main_dataframe):
    wygr_przegr_dataframe = wygr_przegr_dataframe[['numer_przegr', 'numer_wygr']]
    merged_df = pandas.merge(main_dataframe, wygr_przegr_dataframe, left_on='numer_klienta', right_on='numer_przegr',
                             how='left')
    del wygr_przegr_dataframe, main_dataframe
    merged_df['numer_klienta'] = merged_df['numer_wygr'].combine_first(merged_df['numer_klienta'])
    return merged_df[
        ['rachunek', 'numer_klienta', 'status_umowy', 'typ_rachunku', 'rachunek_nrb', 'procent', 'limit_otp',
         'typumowy', 'rynek_zag', 'blokada', 'typ_blokady', 'ike', 'ike_stan', 'typ_klienta', 'drwnik']]
