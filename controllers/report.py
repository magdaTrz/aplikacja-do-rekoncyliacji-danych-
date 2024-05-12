import os
import time
import tkinter as tk

import openpyxl

from models.main import Model
from views.main import View
from threading import Thread
from paths import flow_paths
from text_variables import TextGenerator, TextEnum
from controllers.progress_bar import ProgresBarStatus


class ReportController:
    def __init__(self, model: Model, view: View):
        print(f'ReportController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["report"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.back_btn.config(command=self.handle_back)
        self.frame.open_folder_btn.config(command=self.open_folder_with_reports)
        self.frame.summary_btn.config(command=self.view_the_summary)

    def handle_back(self) -> None:
        current_report = self.model.report_stage_flow_model.current_report
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('stage')

    def handle_generate_report(self):
        print(f'ReportController: handle_generate_report()')
        thread = Thread(target=self.perform_operations)
        thread.start()
        update_current_number_thread = Thread(target=self.update_view_current_number_report)
        update_current_number_thread.start()

    def perform_operations(self):
        print(f'ReportController: perform_operations()')
        stage = self.model.report_stage_flow_model.current_report['stage_str']
        flow = self.model.report_stage_flow_model.current_report['flow_str']
        for path_info in flow_paths.get(f'{flow}_paths', []):
            if stage == TextEnum.LOAD:
                if flow == TextEnum.KOI:
                    from models.koi.oi_adresy import OiAdresy
                    from models.koi.oi_telecom import OiTelecom
                    from models.koi.oi_numb import OiNumb
                    from models.koi.oi_password import OiPassword
                    from models.koi.osoby_instytucje import OsobyInstytucje
                    from models.koi.oi_atryb import OiAtryb

                    self.model.base_data_frame_model.number_of_reports = 6
                    if path_info['name'] == 'osoby_instytucje':
                        self.current_number_report_changed(1)
                        dataframes_osoby_instytucje = OsobyInstytucje(
                            stage=stage,
                            path_src=path_info['src'],
                            path_ext=path_info['ext'],
                            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path,
                            save_folder_report_path=self.model.base_data_frame_model.save_report_folder_path,
                            path_excel_file=path_info['excel']
                        )
                        osoby_instytucje_conversion_success = dataframes_osoby_instytucje._carry_operations()
                        if osoby_instytucje_conversion_success:
                            dataframes_osoby_instytucje.create_report()
                    if path_info['name'] == 'oi_password':
                        self.current_number_report_changed(2)
                        dataframes_oi_password = OiPassword(
                            stage=stage,
                            path_src=path_info['src'],
                            path_ext=path_info['ext'],
                            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path)
                        oi_password_conversion_success = dataframes_oi_password._carry_operations()
                    if path_info['name'] == 'oi_numb':
                        self.current_number_report_changed(3)
                        dataframes_oi_numb = OiNumb(
                            stage=stage,
                            path_src=path_info['src'],
                            path_ext=path_info['ext'],
                            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path)
                        oi_numb_conversion_success = dataframes_oi_numb._carry_operations()
                    if path_info['name'] == 'oi_adresy':
                        self.current_number_report_changed(4)
                        dataframes_oi_adresy = OiAdresy(
                            stage=stage,
                            path_src=path_info['src'],
                            path_ext=path_info['ext'],
                            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path)
                        oi_adresy_conversion_success = dataframes_oi_adresy._carry_operations()
                    if path_info['name'] == 'oi_atryb':
                        self.current_number_report_changed(5)
                        dataframes_oi_atrybuty = OiAtryb(
                            stage=stage,
                            path_src=path_info['src'],
                            path_ext=path_info['ext'],
                            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path)
                        oi_atrybuty_conversion_success = dataframes_oi_atrybuty._carry_operations()
                    if path_info['name'] == 'oi_telecom':
                        self.current_number_report_changed(6)
                        dataframes_oi_telecom = OiTelecom(
                            stage=stage,
                            path_src=path_info['src'],
                            path_ext=path_info['ext'],
                            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path)
                        dataframes_oi_telecom._carry_operations()

                elif flow == TextEnum.UMO:
                    self.number_of_reports = 5
                # will be two more flows KSGFIN, KSGPW, MATE

            else:  # stage == 'end' there will be simillar actions like in LOAD but different path_src, path_ext it will be ext and tgt:
                if flow == TextEnum.KOI:
                    self.number_of_reports = 7
            self.add_text_to_info_label(TextGenerator.report_lable_text(str(flow), str(path_info['name'])))
        self.model.report_model.update_view_report()
        self.model.report_model.report_end_is_changed = False

    def current_number_report_changed(self, number: int):
        self.model.base_data_frame_model.update_current_number_report(number)

    def update_view_current_number_report(self):
        current_number_report = self.model.base_data_frame_model.current_number_report
        number_of_reports = self.model.base_data_frame_model.number_of_reports
        self.frame.progress_bar_info.config(text=f'{current_number_report}/{number_of_reports}')
        self.model.base_data_frame_model.current_number_report_is_changed = False
        self.frame.update_idletasks()

    def update_view_report_ended(self):
        self.frame.open_folder_btn.place(x=290, y=380, width=110)
        self.frame.summary_btn.place(x=414, y=380, width=140)
        self.frame.details_btn.place(x=568, y=380, width=120)

    def open_folder_with_reports(self):
        path = self.model.base_data_frame_model.save_report_folder_path
        print(f'open_folder_with_reports(): {path}')
        try:
            # Check if the path exists
            if os.path.exists(path):
                # Open the folder in the system file explorer
                os.system(f'explorer "{os.path.abspath(path)}"')
                self.add_text_to_info_label(f"Otwieram folder z z raportami.")
            else:
                self.add_text_to_info_label("Folder z raportami nie istnieje.")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.add_text_to_info_label(f"Błąd otwierania folderu z raportami.")

    def add_text_to_info_label(self, new_text: str, error:bool=False, important:bool=False) -> None:
        print(f'ReportController: add_text_to_info_label()')
        tags = []
        if error:
            self.frame.info_label.tag_config("error", foreground="red")
            tags.append("error")
        if important:
            self.frame.info_label.tag_config("important", foreground="green")
            tags.append("important")

        if tags:
            self.frame.info_label.insert(tk.END, f"{new_text}\n", tags)
        else:
            self.frame.info_label.insert(tk.END, f"{new_text}\n")

    def save_excel_report_is_succes_controller(self, dataframes):
        self.add_text_to_info_label("Przechodzę do zapisywania raportu.")
        MAX_ATTEMPTS: int = 3
        for attempt in range(MAX_ATTEMPTS):
            ProgresBarStatus.increase()
            is_correct_saved = dataframes.create_report()

            if is_correct_saved:
                self.add_text_to_info_label("Zapisano poprawnie.", important=True)
                break
            elif is_correct_saved == TextEnum.SAVE_ERROR:
                if attempt < MAX_ATTEMPTS - 1:
                    self.add_text_to_info_label(
                        f"Nie udało się zapisać excela. Upewnij się, że zamknięto plik. "
                        f"Ponowna próba za 8 sekund. (Pozostało prób: {MAX_ATTEMPTS - attempt - 1})",
                        error=True,
                    )
                    time.sleep(8)
                else:
                    self.add_text_to_info_label("Pominięto.", error=True)
            else:
                return

    def view_the_summary(self):
        print("ReportController: view_the_summary()")