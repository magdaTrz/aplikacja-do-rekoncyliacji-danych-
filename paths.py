import os
import sys
from datetime import datetime

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

current_working_dir = os.getcwd()
path_background_color = resource_path('img/background_color.png')
path_help_icon = resource_path('img/question_icon.png')
path_background_start = resource_path('img/bg_start.png')
path_background_stage = resource_path('img/bg_stage.png')
path_background_flow = resource_path('img/bg_flow.png')
path_background_report = resource_path('img/bg_raport.png')
path_background_details = resource_path('img/bg_details.png')
path_background_stage_settings = resource_path('img/bg_stage_settings.png')
path_back_icon = resource_path('img/left_back.png')
path_start_text = resource_path('img/text_start.png')
path_save_icon = resource_path('img/save_icon.png')
path_lock_icon = resource_path('img/lock_icon.png')
path_check_icon = resource_path('img/check_icon.png')
path_xmark_icon = resource_path('img/xmark_icon.png')
path_calendar_icon = resource_path('img/calendar_icon.png')
path_open_folder_icon = resource_path('img/open_folder_icon.png')
path_loupe_icon = resource_path('img/loupe_icon.png')
path_statistic_icon = resource_path('img/statistic_icon.png')
path_chart_icon = resource_path('img/chart_icon.png')
path_group_icon = resource_path('img/group_icon.png')
path_table_icon = resource_path('img/table_icon.png')
path_add_file_icon = resource_path('img/add_file_icon.png')
path_gear_icon = resource_path('img/gear_icon.png')
path_folder_icon = resource_path('img/folder_icon.png')
path_add_folder_icon = resource_path('img/add_folder_icon.png')
path_excel_icon = resource_path('img/excel_icon.png')

path_support_files = resource_path('dane/klienci_all.txt')
path_support_files_folder = resource_path('dane')
path_dict_folder = resource_path('slowniki')


def get_timestamp():
    "Funkcja tworząca timestamp umieszczany w nazwie plików"
    now = datetime.now()
    formatted_timestamp = now.strftime("%Y%m%d_%H")
    return formatted_timestamp


timestamp = get_timestamp()

flow_paths = {
    'KOI_paths': [
        {
            'name': 'osoby_instytucje',
            'src': 'rfs_klienci_dodatkowe_src.txt',
            'ext': 'rfs_out_osoby_instytucje_ext.csv',
            'tgt': 'rfs_osoby_instytucje_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_1_{timestamp}.xlsx'
        },
        {
            'name': 'oi_password',
            'src': 'rfs_klienci_dodatkowe_src.txt',
            'ext': 'rfs_out_oi_password_ext.csv',
            'tgt': 'rfs_oi_password_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_1_{timestamp}.xlsx'
        },
        {
            'name': 'oi_numb',
            'src': 'rfs_oi_numb_src.txt',
            'ext': 'rfs_out_oi_numb_ext.csv',
            'tgt': 'rfs_oi_numb_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_2_{timestamp}.xlsx'
        },
        {
            'name': 'oi_adresy',
            'src': 'rfs_oi_adresy_src.txt',
            'ext': 'rfs_out_oi_adresy_ext.csv',
            'tgt': 'rfs_oi_adresy_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_2_{timestamp}.xlsx'
        },
        {
            'name': 'oi_atryb',
            'src': 'rfs_klienci_dodatkowe_src.txt',
            'ext': 'rfs_out_oi_atryb_ext.csv',
            'tgt': 'rfs_oi_atryb_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_3_{timestamp}.xlsx'
        },
        {
            'name': 'oi_telecom',
            'src': 'rfs_klienci_dodatkowe_src.txt',
            'ext': 'rfs_out_oi_telecom_ext.csv',
            'tgt': 'rfs_oi_telecom_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_3_{timestamp}.xlsx'
        },
        {
            'name': 'oi_consents',
            'src': 'rfs_oi_consents_src.txt',
            'ext': 'rfs_out_oi_consents_ext.csv',
            'tgt': 'rfs_oi_consents_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KOI_4_{timestamp}.xlsx'
        }
    ],

    'UMO_paths': [
        {
            'name': 'umowy',
            'src': 'rfs_umowy_src.txt',
            'ext': 'rfs_out_umowy_ext.csv',
            'tgt': 'rfs_umowy_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_UMO_1_{timestamp}.xlsx'
        },
        {
            'name': 'umo_osoba',
            'src': 'rfs_umo_osoba_src.txt',
            'ext': 'rfs_out_umo_osoba_ext.csv',
            'tgt': 'rfs_umo_osoba_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_UMO_1_{timestamp}.xlsx'
        },
        {
            'name': 'derywaty',
            'src': 'rfs_derywaty_src.txt',
            'ext': 'rfs_out_derywaty_ext.csv',
            'tgt': 'rfs_derywaty_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_UMO_1_{timestamp}.xlsx'
        },
        {
            'name': 'rachunki_przelewy',
            'src': 'rfs_rachunki_przelewy_src.txt',
            'ext': 'rfs_out_rachunki_przelewy_ext.csv',
            'tgt': 'rfs_rachunki_przelewy_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_UMO_2_{timestamp}.xlsx'
        },
        {
            'name': 'brokerage_agreement',
            'src': 'rfs_brokerage_agreement_src.txt',
            'ext': 'rfs_out_brokerage_agreement_ext.csv',
            'tgt': 'rfs_brokerage_agreement_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_UMO_2_{timestamp}.xlsx'
        }
    ],

    'KSGPW_paths': [
        {
            'name': 'salda_pw',
            'src': 'rfs_salda_pw_src.txt',
            'ext': 'rfs_out_salda_pw_ext.csv',
            'tgt': 'rfs_salda_pw_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KSGPW_1_{timestamp}.xlsx'
        }
    ],

    'KSGFIN_paths': [
        {
            'name': 'salda_fin',
            'src': 'rfs_salda_fin_src.txt',
            'ext': 'rfs_out_salda_fin_ext.csv',
            'tgt': 'rfs_salda_fin_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_KSGFIN_1_{timestamp}.xlsx'
        }
    ],

    'MATE_paths': [
        {
            'name': 'mate',
            'src': 'rfs_mate_src.txt',
            'ext': 'rfs_out_mate_ext.csv',
            'tgt': 'rfs_mate_tgt.csv',
            'excel': f'Rekoncyliacja_RekomendacjaObszaru_MATE_1_{timestamp}.xlsx'
        }
    ],
}
