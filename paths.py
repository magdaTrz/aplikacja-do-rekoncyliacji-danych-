import os
from datetime import datetime

current_working_dir = os.getcwd()

path_background_color = fr'{current_working_dir}\img\background color.png'
path_help_icon = fr'{current_working_dir}\img\question_icon.png'
path_background_start = fr'{current_working_dir}\img\bg_start.png'
path_background_stage = fr'{current_working_dir}\img\bg_stage.png'
path_background_flow = fr'{current_working_dir}\img\bg_flow.png'
path_background_report = fr'{current_working_dir}\img\bg_raport.png'
path_background_details = fr'{current_working_dir}\img\bg_details.png'
path_background_stage_settings = fr'{current_working_dir}\img\bg_stage_settings.png'
path_back_icon = fr'{current_working_dir}\img\left_back.png'
path_start_text = fr'{current_working_dir}\img\text_start.png'
path_save_icon = fr'{current_working_dir}\img\save_icon.png'
path_lock_icon = fr'{current_working_dir}\img\lock_icon.png'
path_check_icon = fr'{current_working_dir}\img\check_icon.png'
path_xmark_icon = fr'{current_working_dir}\img\xmark_icon.png'
path_calendar_icon = fr'{current_working_dir}\img\calendar_icon.png'
path_open_folder_icon = fr'{current_working_dir}\img\open_folder_icon.png'
path_loupe_icon = fr'{current_working_dir}\img\loupe_icon.png'
path_statistic_icon = fr'{current_working_dir}\img\statistic_icon.png'
path_chart_icon = fr'{current_working_dir}\img\chart_icon.png'
path_group_icon = fr'{current_working_dir}\img\group_icon.png'
path_table_icon = fr'{current_working_dir}\img\table_icon.png'
path_acn = fr'{current_working_dir}\img\acn_logo.png'
path_sbm = fr'{current_working_dir}\img\sbm_logo.png'
path_add_file_icon = fr'{current_working_dir}\img\add_file_icon.png'
path_gear_icon = fr'{current_working_dir}\img\gear_icon.png'
path_folder_icon = fr'{current_working_dir}\img\folder_icon.png'
path_add_folder_icon = fr'{current_working_dir}\img\add_folder_icon.png'
path_excel_icon = fr'{current_working_dir}\img\excel_icon.png'
path_support_files = fr'{current_working_dir}\dane\klienci_all.txt'
path_support_files_folder = fr'{current_working_dir}\dane'
path_dict_folder = fr'{current_working_dir}\słowniki'
path_loading = fr"{current_working_dir}\img\Dual Ring-2.4s-30px.gif"


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
            'tgt': 'rfs_salda_fin_tgt_tgt.csv',
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
