from models.main import Model
from models.auth import Report
from views.main import View
from tkinter import filedialog

import os

current_working_dir = os.getcwd()

class StageController:
    def __init__(self, model: Model, view: View) -> None:
        print(f'StageController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["stage"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        print(f'StageController: _bind()')
        self.frame.supportfile_btn.config(command=self.handle_generate_support_files)
        self.frame.supportfile_filedialog_btn.config(command=self.choose_file)

        self.frame.reportload_btn.config(command=lambda: self.handle_selected_stage(stage='load'))
        self.frame.reportend_btn.config(command=lambda: self.handle_selected_stage(stage='end'))

        self.frame.back_btn.config(command=self.handle_back)

    def handle_back(self) -> None:
        current_report = self.model.auth.current_report
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('start')

    def logout(self) -> None:
        print(f'StageController: logout()')
        self.model.auth.logout()

    def handle_selected_stage(self, stage: str) -> None:
        print(f'StageController: handle_selected_stage({stage})')
        report: Report = {'stage_str': stage,
                          'flow_str': ''}
        self.model.auth.stage_save(report)

    def update_view(self):
        print(f'StageController: update_view()')
        current_report = self.model.auth.current_report
        if current_report:
            stage = current_report["stage_str"]
            self.frame.greeting.config(text=f"Welcome, {stage}!")
        else:
            self.frame.greeting.config(text=f"Brak")

    def choose_file(self) -> None:
        """File selection dialog"""
        print(f'StageController: choose_file()')
        file_path = filedialog.askopenfilename(
            title='Wybierz plik',
            filetypes=[('Pliki tekstowe', '*.txt'), ('Wszsytkie pliki', '*.*')]
        )
        if file_path:
            self.handle_generate_support_files(file_path)

    def handle_generate_support_files(self, file_path=f'{current_working_dir}\klienci_all.txt')-> None:
        """"Handles a file load event."""
        print(f'StageController: handle_generate_support_files({file_path})')
        success = self.model.support_files.load_data_from_file(file_path)
        if success:
            self.frame.supportfile_filedialog_label.config(text=f"Wybrano: {file_path}")
            data = self.model.support_files.get_data()
        else:
            self.frame.supportfile_filedialog_label.config(text=f"Nie znaleziono pliku potrzebnego do wygenerowania "
                                                                f"plików pomocniczych. ")

