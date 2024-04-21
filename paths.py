import os

current_working_dir = os.getcwd()

path_background_color = fr'{current_working_dir}\img\background color.png'
path_help_icon = fr'{current_working_dir}\img\question_icon.png'
path_background = fr'{current_working_dir}\img\bg_start.png'
path_start_text = fr'{current_working_dir}\img\text_start.png'
path_acn = fr'{current_working_dir}\img\acn_logo.png'
path_sbm = fr'{current_working_dir}\img\sbm_logo.png'
path_add_file_icon = fr'{current_working_dir}\img\add_file_icon.png'
path_folder_icon = fr'{current_working_dir}\img\folder_icon.png'
path_support_files = fr'{current_working_dir}\dane\klienci_all.txt'
path_support_files_folder = fr'{current_working_dir}\dane'
path_dict_folder = fr'{current_working_dir}\słowniki'
path_loading = fr"{current_working_dir}\img\Dual Ring-2.4s-30px.gif"

koi_paths = [
    {'name': 'osoby_instytucje', 'src': 'rfs_klienci_dodatkowe_src.txt', 'ext': 'rfs_out_osoby_instytucje_ext.csv',
     'tgt': 'rfs_osoby_instytucje_tgt.csv'},
    {'name': 'oi_password', 'src': 'rfs_klienci_dodatkowe_src.txt', 'ext': 'rfs_out_oi_password_ext.csv',
     'tgt': 'rfs_oi_password_tgt.csv'},
    {'name': 'oi_numb', 'src': 'rfs_oi_numb_src.txt', 'ext': 'rfs_out_oi_numb_ext.csv','tgt': 'rfs_oi_numb_tgt.csv'},
    {'name': 'oi_adresy', 'src': 'rfs_oi_adresy_src.txt', 'ext': 'rfs_out_oi_adresy_ext.csv',
     'tgt': 'rfs_oi_adresy_tgt.csv'},
    {'name': 'oi_atryb', 'src': 'rfs_klienci_dodatkowe_src.txt', 'ext': 'rfs_out_oi_atryb_ext.csv',
     'tgt': 'rfs_oi_atryb_tgt.csv'},
    {'name': 'oi_telecom', 'src': 'rfs_klienci_dodatkowe_src.txt', 'ext': 'rfs_out_oi_telecom_ext.csv',
     'tgt': 'rfs_oi_telecom_tgt.csv'},
    {'name': 'oi_consents', 'src': 'rfs_oi_consents_src.txt', 'ext': 'rfs_out_oi_consents_ext.csv',
     'tgt': 'rfs_oi_consents_tgt.csv'}]

umo_paths = [
    {'name': 'umowy', 'src': 'rfs_umowy_src.txt', 'ext': 'rfs_out_umowy_ext.csv',
     'tgt': 'rfs_umowy_tgt.csv'},
    {'name': 'umo_osoba', 'src': 'rfs_umo_osoba_src.txt', 'ext': 'rfs_out_umo_osoba_ext.csv',
     'tgt': 'rfs_umo_osoba_tgt.csv'},
    {'name': 'derywaty', 'src': 'rfs_derywaty_src.txt', 'ext': 'rfs_out_derywaty_ext.csv',
     'tgt': 'rfs_derywaty_tgt.csv'},
    {'name': 'rachunki_przelewy', 'src': 'rfs_rachunki_przelewy_src.txt', 'ext': 'rfs_out_rachunki_przelewy_ext.csv',
     'tgt': 'rfs_rachunki_przelewy_tgt.csv'},
    {'name': 'brokerage_agreement', 'src': 'rfs_brokerage_agreement_src.txt', 'ext': 'rfs_out_brokerage_agreement_ext.csv',
     'tgt': 'rfs_brokerage_agreement_tgt.csv'}]

ksgpw_paths = [{'name': 'salda_pw', 'src': 'rfs_salda_pw_src.txt', 'ext': 'rfs_out_salda_pw_ext.csv',
                'tgt': 'rfs_salda_pw_tgt.csv'}]

ksgfin_paths = [{'name': 'salda_fin', 'src': 'rfs_salda_fin_src.txt', 'ext': 'rfs_out_salda_fin_ext.csv',
                 'tgt': 'rfs_salda_fin_tgt_tgt.csv'}]

mate_paths = [{'name': 'mate', 'src': 'rfs_mate_src.txt', 'ext': 'rfs_out_mate_ext.csv',
               'tgt': 'rfs_mate_tgt.csv'}]
