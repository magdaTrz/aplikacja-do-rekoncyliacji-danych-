import os
import time
import tkinter as tk
from typing import Dict

import openpyxl
import pandas

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
        self.frame.summary_btn.config(command=self.handle_view_the_summary)

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

    def add_text_to_info_label(self, new_text: str, error: bool = False, important: bool = False) -> None:
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

    def handle_view_the_summary(self):
        print("ReportController: view_the_summary()")
        self.model.base_data_frame_model.add_data_to_summary_view()
        self.view.switch('summary')

    def perform_operations(self) -> None:
        stage: str = self.model.report_stage_flow_model.current_report['stage_str']
        flow: str = self.model.report_stage_flow_model.current_report['flow_str']
        self.add_text_to_info_label(f"Wykonuję raporty: {(str(flow))}")
        i = 1
        for path_info in flow_paths.get(f'{flow}_paths', []):
            self.current_number_report_changed(i)
            if stage == TextEnum.LOAD:
                # wykonuje się tyle razy ile jest pod przepływów
                self.add_text_to_info_label(TextGenerator.flow_lable_text())
                self.process_path_info(flow, stage, path_info)
            if stage == TextEnum.END:
                print(TextEnum.END)
            i+=1
        self.model.report_model.update_view_report()
        self.model.report_model.report_end_is_changed = False

    def process_path_info(self, flow: str, stage: str, path_info: Dict[str, str]) -> None:
        if flow == TextEnum.KOI:
            self.model.base_data_frame_model.number_of_reports = 6
            from models.koi.oi_adresy import OiAdresy
            from models.koi.oi_telecom import OiTelecom
            from models.koi.oi_numb import OiNumb
            from models.koi.oi_password import OiPassword
            from models.koi.osoby_instytucje import OsobyInstytucje
            from models.koi.oi_atryb import OiAtryb
            model_classes = {
                'osoby_instytucje': OsobyInstytucje,
                'oi_password': OiPassword,
                # 'oi_atryb': OiAtryb,
                # 'oi_adresy': OiAdresy,
                # 'oi_telecom': OiTelecom,
                # 'oi_numb': OiNumb,
            }
        elif flow == TextEnum.UMO:
            self.model.base_data_frame_model.number_of_reports = 4
            #...

        for name, ModelClass in model_classes.items():
            if path_info['name'] == name:
                self.process_model(flow, stage, path_info, ModelClass)

    def process_model(self, flow: str, stage: str, path_info: Dict[str, str], ModelClass: Model) -> None:
        start_time: float = time.time()
        self.add_text_to_info_label(TextGenerator.flow_lable_text())
        dataframes = ModelClass(
            stage=stage,
            path_src=path_info['src'],
            path_ext=path_info['ext'],
            data_folder_report_path=self.model.base_data_frame_model.data_folder_report_path,
            save_folder_report_path=self.model.base_data_frame_model.save_report_folder_path,
            path_excel_file=path_info['excel']
        )
        self.add_text_to_info_label(TextGenerator.mapping_lable_text())
        success: bool = dataframes._carry_operations()

        total_rows = (dataframes.dataframe_src.shape[0] if dataframes.dataframe_src is not None else 0) + \
                     (dataframes.dataframe_ext.shape[0] if dataframes.dataframe_ext is not None else 0)

        report_data: Dict[str, str] = {
            "Raport": path_info['name'],
            'Plik Excel': path_info['excel'],
            'Status': 'Sukces' if success else 'Błąd zapisu',
            'Czas wykonywania': f'{time.time() - start_time:.2f} sec' if success else '-- sec',
            'Liczba wierszy (dataframe_src)': f"{dataframes.dataframe_src.shape[0]} wierszy" if dataframes.dataframe_src is not None else "Brak danych",
            'Liczba wierszy (dataframe_ext)': f"{dataframes.dataframe_ext.shape[0]} wierszy" if dataframes.dataframe_ext is not None else "Brak danych",
            'Suma wierszy (łącznie z obu dataframe)': f"{total_rows} wierszy"
        }

        self.add_text_to_info_label(TextGenerator.report_lable_text())
        dataframes.create_report()
        self.model.base_data_frame_model.add_value_to_summary_dataframes_dict(report_data)

