import os.path
import time

import tkinter as tk
from typing import List

from models.main import Model
from models.report_model import Report
from views.main import View
from tkinter import filedialog
from threading import Thread

import paths


class FlowLoadController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.frame = self.view.frames["flow_load"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.back_btn.config(command=self.handle_back)
        self.frame.koi_btn.config(command=lambda: self.handle_selected_flow(flow='koi'))
        self.frame.umo_btn.config(command=lambda: self.handle_selected_flow(flow='umo'))
        self.frame.ksgpw_btn.config(command=lambda: self.handle_selected_flow(flow='ksgpw'))
        self.frame.ksgfin_btn.config(command=lambda: self.handle_selected_flow(flow='ksgfin'))
        self.frame.mate_btn.config(command=lambda: self.handle_selected_flow(flow='mate'))

        self.frame.header_filedialog.bind('<Button-1>', self.set_directory())
        self.frame.filedialog_btn.config(command=self.choose_folder)
        self.frame.start_btn.config(command=self.handle_generate_report)

    def set_directory(self, path=None) -> None:
        if path is None:
            self.frame.header_filedialog.config(text=f'Pliki pobierane są z folderu:\n'
                                                     f'{self.model.report_model.directory_path}')
        else:
            self.model.report_model.directory_path = path
            self.frame.header_filedialog.config(text=f'Pliki pobierane są z folderu:\n'
                                                     f'{self.model.report_model.directory_path}')

    def handle_back(self) -> None:
        current_report = self.model.report_model.current_report
        print(f'FlowLoadController: handle_back(){current_report=}')
        self.frame.header_filedialog.config(text=f"")
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('stage')

    def handle_selected_flow(self, flow: str) -> None:
        print(f'FlowLoadController: handle_selected_flow()')
        report = {"stage_str": "load", "flow_str": flow}
        self.model.report_model.report_save(report)

        for child in self.frame.winfo_children():
            if child.winfo_class() == "Button":
                child.config(bg="SystemButtonFace", fg="black")
        name_btn = flow + '_btn'
        if hasattr(self.frame, name_btn):
            getattr(self.frame, name_btn).config(bg="red", fg="white")
        else:
            print(f"Naciśnięto nieznany przycisk: {flow}")

    def update_view(self):
        current_report = self.model.report_model.current_report
        print(f'FlowLoadController: update_view() {current_report=}')
        if current_report:
            stage = current_report["stage_str"]
            flow = current_report["flow_str"]

            self.add_text_to_info_label(f'Sprawdzam czy dla raportu GoForLoad {flow} są wszystkie potrzebne pliki...')
            missing_files = self.check_folder_for_files(eval(f'paths.{flow}_paths'))
            if missing_files is None:
                self.add_text_to_info_label('Wszytkie potrzebne pliki znajdują się w folderze.')
            else:
                self.add_text_to_info_label(f'Brak następujących plików w folderze: {missing_files}')

            self.frame.start_btn.place(x=140, y=380, width=165, height=40)

    def update_progress(self) -> None:
        while True:
            self.frame.progress_bar['value'] = self.model.base_data_frame_model.progress_value
            self.frame.update_idletasks()
            time.sleep(0.1)
            self.frame.progress_bar_info.config(text=f'{self.model.base_data_frame_model.current_number_report}/'
                                                     f'{self.model.base_data_frame_model.number_of_reports}')

    def choose_folder(self) -> None:
        print(f'FlowLoadController: choose_folder( )')
        folder_path = filedialog.askdirectory()
        if folder_path:
            print(folder_path)
            self.set_directory(folder_path)
            self.add_text_to_info_label('Zmieniono folder.')

    def handle_generate_report(self) -> None:
        print(f'FlowLoadController: handle_generate_report()')
        directory_path = self.model.report_model.directory_path
        flow = self.model.report_model.current_report["flow_str"]
        stage = self.model.report_model.current_report["stage_str"]
        self.frame.progress_bar.place(x=60, y=350)
        self.frame.progress_bar_info.config(text=f'{self.model.base_data_frame_model.current_number_report}/'
                                                 f'{self.model.base_data_frame_model.number_of_reports}')
        self.frame.progress_bar_info.place(x=32, y=350, width=25, height=22)
        threat = Thread(target=self.model.base_data_frame_model.perform_operations(directory_path, stage, flow))
        threat.start()
        progress_threat = Thread(target=self.update_progress)
        progress_threat.start()

    def check_folder_for_files(self, paths_: str) -> list[str] | None:
        print(f'FlowLoadController: check_folder_for_files()')
        directory_path = self.model.report_model.directory_path
        missing_files = []

        for path_info in paths_:
            src_path = os.path.join(directory_path, path_info['src'])
            ext_path = os.path.join(directory_path, path_info['src'])

            if not os.path.isfile(src_path):
                missing_files.append(path_info['src'])
            if not os.path.isfile(ext_path):
                missing_files.append(path_info['ext'])

        if missing_files:
            return missing_files  # Returns a list of missing files
        else:
            return None  # All files for this flow have been found

    def add_text_to_info_label(self, new_text: str) -> None:
        print(f'FlowLoadController: add_text_to_info_label()')
        self.frame.info_label.insert(tk.END, f'\n{new_text}')
