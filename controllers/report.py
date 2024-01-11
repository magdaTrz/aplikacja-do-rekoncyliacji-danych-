import time
import tkinter as tk

from models.main import Model
from views.main import View
from threading import Thread


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

    def handle_back(self) -> None:
        current_report = self.model.report_model.current_report
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('stage')

    def handle_generate_report(self):
        print(f'ReportController: handle_generate_report()')
        stage = self.model.report_model.current_report['stage_str']
        flow = self.model.report_model.current_report['flow_str']
        directory_path = self.model.base_data_frame_model.directory_path
        self.add_text_to_info_label(f'Trwa przygotowanie danych dla przepływu {stage}: {flow}')

        thread = Thread(target=self.perform_operations)
        thread.start()
        update_current_number_thread = Thread(target=self.update_view_current_number_report)
        update_current_number_thread.start()

    def perform_operations(self):
        print(f'ReportController: perform_operations()')
        stage = self.model.report_model.current_report['stage_str']
        flow = self.model.report_model.current_report['flow_str']
        for path_info in eval(f'paths.{flow}_paths'):
            if stage == 'load':
                if flow == 'koi':
                    from models.koi.oi_telecom import OiTelecom

                    self.model.base_data_frame_model.number_of_reports = 7
                    if path_info['name'] == 'osoby_instytucje':
                        self.current_number_report_changed(1)
                        time.sleep(1)
                        pass
                    if path_info['name'] == 'oi_password':
                        self.current_number_report_changed(2)
                        pass
                    if path_info['name'] == 'oi_numb':
                        self.current_number_report_changed(3)
                        time.sleep(10)
                        pass
                    if path_info['name'] == 'oi_adresy':
                        self.current_number_report_changed(4)
                        pass
                    if path_info['name'] == 'oi_atryb':
                        self.current_number_report_changed(5)
                        pass
                    if path_info['name'] == 'oi_telecom':
                        self.current_number_report_changed(6)
                        dataframes_oi_telecom = OiTelecom(stage=stage,
                                                          path_src=path_info['src'],
                                                          path_ext=path_info['ext'])
                        dataframes_oi_telecom._carry_operations()

                elif flow == 'umo':
                    self.number_of_reports = 5

            if stage == 'end':
                if flow == 'koi':
                    self.number_of_reports = 7
        print('zakończono')

    def current_number_report_changed(self, number: int):
        self.model.base_data_frame_model.update_current_number_report(number)

    def update_view_current_number_report(self):
        current_number_report = self.model.base_data_frame_model.current_number_report
        number_of_reports = self.model.base_data_frame_model.number_of_reports
        self.frame.progress_bar_info.config(text=f'{current_number_report}/{number_of_reports}')
        self.model.base_data_frame_model.current_number_report_is_changed = False
        self.frame.update_idletasks()

    def add_text_to_info_label(self, new_text: str) -> None:
        print(f'ReportController: add_text_to_info_label()')
        self.frame.info_label.insert(tk.END, f'{new_text}\n\n')
