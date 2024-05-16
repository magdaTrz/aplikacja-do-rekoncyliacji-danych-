import os
import time

import paths
from models.main import Model
from paths import path_support_files_folder, path_dict_folder
from text_variables import TextEnum
from views.main import View
from tkinter import filedialog, ttk
from threading import Thread


class StageController:
    def __init__(self, model: Model, view: View) -> None:
        self.folder_path_support_files = ''
        self.folder_path_dicts = ''
        self.folder_path_save_reports = ''
        self.model = model
        self.view = view
        self.frame = self.view.frames["stage"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view."""
        # binds for support files
        self.frame.generate_support_files_btn.config(command=lambda: self.start_process(folder='support_files'))
        self.frame.support_file_filedialog_btn.config(command=lambda: self.choose_folder(folder='support_files_folder_path'))

        # binds for dicts
        self.frame.update_dictionaries_btn.config(command=lambda: self.start_process(folder='dict'))
        self.frame.dictionaries_filedialog_btn.config(command=lambda: self.choose_folder(folder='dict_folder_path'))

        # binds for choosing stage
        self.frame.report_load_btn.config(command=lambda: self.handle_selected_stage(stage=TextEnum.LOAD))
        self.frame.report_end_btn.config(command=lambda: self.handle_selected_stage(stage=TextEnum.END))

        # binds settings save_report_folder_path
        self.frame.save_dictionaries_btn.config(command=lambda: self.choose_folder(folder='save_report_folder_path'))

        # binds settings data_folder_report_path
        self.frame.choose_folder_btn.config(command=lambda: self.choose_folder(folder='data_folder_report_path'))

        self.frame.back_btn.config(command=self.handle_back)

    def check_directory(self) -> bool:
        """Updated support file status label"""
        #  check if path to file exist
        if os.path.exists(paths.path_support_files):
            # check if file is not empty
            if os.path.getsize(paths.path_support_files) > 0:
                self.frame.supportfile_filedialog_label.config(
                    text=f"Pliki do stworzenia plików pomocniczych są gotowe do generowania.", wraplength=380,
                    justify="left", anchor='w')
                return True
            else:
                self.frame.supportfile_filedialog_label.config(
                    text=f"Pliki do stworzenia plików pomocniczych są puste.", wraplength=380,
                    justify="left", anchor='w')
                return False
        else:
            self.frame.supportfile_filedialog_label.config(
                text=f"Wskaż plik do stworzenia plików pomocniczych.", wraplength=380,
                justify="left", anchor='w')
            return False

    def handle_back(self) -> None:
        """Return to previous screen function"""
        self.model.report_stage_flow_model.report_clear()
        self.view.switch('start')

    def handle_selected_stage(self, stage: str) -> None:
        print(f'StageController: handle_selected_stage({stage=})')
        if stage == TextEnum.LOAD:
            self.view.switch('flow_load')
        elif stage == TextEnum.END:
            self.view.switch('flow_end')

    def choose_folder(self, folder: str) -> None:
        """Folder selection dialog."""
        print(f"StageController: choose_folder(): {folder}")
        folder_path = filedialog.askdirectory()
        if folder_path:
            if folder == 'dict_folder_path':
                self.folder_path_dicts = folder_path
                self.model.dict_update.set_path(folder_path)
                self.frame.show_popup_window(title='Zakończono',
                                             text=f"Zmieniono folder z którego pobierane są pliki słowników: "
                                                  f"\n{folder_path}")
            elif folder == 'support_files_folder_path':
                self.folder_path_support_files = folder_path
                self.model.support_files.set_path(folder_path)
                self.frame.show_popup_window(title='Zakończono',
                                             text=f"Zamieniono folder z którego pobierane są pliki pomocnicze:"
                                                  f"\n{folder_path}")
            elif folder == 'save_report_folder_path':
                self.model.base_data_frame_model.set_save_report_folder_path(folder_path)
                self.frame.show_popup_window(title='Zakończono',
                                             text=f"Zamieniono folder w którym zostaną zapisane raporty:"
                                                  f"\n{folder_path}")
            elif folder == 'data_folder_report_path':
                self.model.base_data_frame_model.set_data_folder_path(folder_path)
                self.frame.show_popup_window(title='Zakończono',
                                             text=f"'Zmieniono folder z którego pobiane są dane do raportów:"
                                                  f"\n{folder_path}")

    def start_process(self, folder: str) -> None:
        self.frame.progress_bar.place(x=60, y=75)
        if folder == 'support_files':
            thread = Thread(target=self.handle_generate_support_files)
            thread.start()
        elif folder == 'dict':
            thread = Thread(target=self.handle_dict_updates)
            thread.start()
        progress_thread = Thread(target=self.update_progress)
        progress_thread.start()

    def update_progress(self):
        while True:
            self.frame.progress_bar['value'] = self.model.support_files.progress_value
            self.frame.update_idletasks()
            time.sleep(0.1)

    def handle_generate_support_files(self) -> None:
        """"Handles a file load event."""
        success_file0 = self.model.support_files.check_for_files(file_name='rfs_klienci_all_src.txt')
        success_file1 = self.model.support_files.check_for_files(file_name='rfs_out_osoby_instytucje_ext.csv')
        success_file2 = self.model.support_files.check_for_files(file_name='rfs_out_oi_numb_ext.csv')
        if success_file2 and success_file1 and success_file0:
            self.model.support_files.create_support_file_koi()
            self.model.support_files.create_support_file_is_migrated()
            style = ttk.Style()
            style.configure("Green.TButton", background="green", foreground="green")
            style.map("Green.TButton",
                      background=[("pressed", "green")],
                      foreground=[("pressed", "green")])
            self.frame.generate_support_files_btn.config(style="Green.TButton")
            self.frame.show_popup_window(title='Zakończono', text=f"Poprawnie zakończono tworzenie plików pomocniczych.")
        else:
            self.frame.show_popup_window(title='Error', text=f"Nie znaleziono pliku potrzebnego do wygenerowania plików pomocniczych.")

    def handle_dict_updates(self) -> None:
        self.model.dict_update.update_KSFIN_dict()
        self.model.dict_update.update_KSGPW_dict()
        self.model.dict_update.update_TRANS_dict()
        style = ttk.Style()
        style.configure("Green.TButton", background="green", foreground="green")
        style.map("Green.TButton",
                  background=[("pressed", "green")],
                  foreground=[("pressed", "green")])
        self.frame.update_dictionaries_btn.config(style="Green.TButton")
        self.frame.show_popup_window(title='Zakończono', text=f"Poprawnie zakończono aktualizację słowników.")
        return

