import os
import tkinter as tk
from tkinter import messagebox
from typing import List

from models.main import Model
from paths import flow_paths
from text_variables import TextEnum
from views.main import View


class DetailsController:
    def __init__(self, model: Model, view: View):
        print(f'DetailsController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["details"]
        self._bind()

    def _bind(self) -> None:
        self.frame.back_btn.config(command=self.handle_back)
        self.frame.show_true_false_statistic_btn.config(command=self.handle_view_percent_reconciliation)
        self.frame.show_merge_statistic_btn.config(command=self.handle_view_merge_statistic)
        self.frame.show_data_btn.config(command=self.handle_view_data)
        self.frame.open_file_btn.config(command=self.open_excel_file)

    def handle_back(self) -> None:
        self.view.switch('report')

    def create_buttons(self):
        def get_names_from_flow() -> List[str]:
            path_key = f'{flow}_paths'
            if path_key in flow_paths:
                return [path_info['name'] for path_info in flow_paths[path_key]]
            return []

        print('DetailsController: create_buttons()')
        flow: str = self.model.report_stage_flow_model.current_report['flow_str']
        name_list = get_names_from_flow()
        self.frame.create_buttons(name_list)

    def handle_view_percent_reconciliation(self):
        # def show true false statistic
        self.frame.treeview_frame.config(text='Statystyki procent rekoncyliacji ')
        name: str = self.frame.selected_btn
        print(f'DetailsController: handle_view_percent_reconciliation({name})')
        dataframe = self.model.base_data_frame_model.get_details_percent_reconciliation_dataframes(name)
        self.frame.select_right_button('true_false')
        self.frame.display_dataframe(dataframe)

    def handle_view_merge_statistic(self):
        # def show merge statistic
        self.frame.treeview_frame.config(text='Statystyki połączenia')
        name: str = self.frame.selected_btn
        print(f'DetailsController: handle_view_merge_statistic({name})')
        dataframe = self.model.base_data_frame_model.get_details_merge_dataframes(name)
        self.frame.select_right_button('merge')
        self.frame.display_dataframe(dataframe)

    def handle_view_data(self):
        # def show part of dataframe
        self.frame.treeview_frame.config(text='Próbka danych')
        name: str = self.frame.selected_btn
        print(f'DetailsController: handle_view_merge_statistic({name})')
        dataframe = self.model.base_data_frame_model.get_details_data_dataframes(name)
        self.frame.select_right_button('data')
        self.frame.display_dataframe(dataframe)
        self.frame.open_file_btn.place(x=50, y=417, width=190)

    def open_excel_file(self):
        file_name = self.get_excel_path()
        try:
            path = self.model.base_data_frame_model.save_report_folder_path
            file_path = os.path.join(path, file_name)
            os.startfile(file_path)
        except FileNotFoundError:
            print(f"Plik '{file_name}' nie został znaleziony.")
            tk.messagebox.showerror("Info", "Plik '{file_name}' nie został znaleziony.")
        except Exception as e:
            print(f"Wystąpił błąd podczas otwierania pliku: {e}")
            tk.messagebox.showerror("Info", "Wystąpił błąd podczas otwierania pliku.")

    def get_excel_path(self) -> str | None:
        stage: str = self.model.report_stage_flow_model.current_report['stage_str']
        flow: str = self.model.report_stage_flow_model.current_report['flow_str']
        name: str = self.frame.selected_btn
        if f'{flow}_paths' in flow_paths:
            for item in flow_paths[f'{flow}_paths']:
                if item['name'] == name:
                    return self.modify_filename(item.get('excel'), stage)
        return None

    @staticmethod
    def modify_filename(filename: str, stage: str):
        if stage == TextEnum.LOAD:
            filename = filename.replace(".xlsx", "_Go4Load.xlsx")
        elif stage == TextEnum.END:
            filename = filename.replace(".xlsx", "_Go4EndDay.xlsx")
        return filename
