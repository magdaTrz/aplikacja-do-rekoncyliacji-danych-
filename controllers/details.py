import os
import time
import tkinter as tk

import openpyxl
import pandas

from models.main import Model
from views.main import View
from threading import Thread
from paths import flow_paths
from typing import List, Dict
from text_variables import TextGenerator, TextEnum
from controllers.progress_bar import ProgresBarStatus


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
        # TODO: przycisk który bedzie otwierał folder z raportami

    def handle_back(self) -> None:
        self.view.switch('report')

    def create_buttons(self):
        def get_names_from_flow() -> List[str]:
            path_key = f'{flow}_paths'
            if path_key in flow_paths:
                return [path_info['name'] for path_info in flow_paths[path_key]]
            return []

        print('DetailsController: create_buttons()')
        stage: str = self.model.report_stage_flow_model.current_report['stage_str']
        flow: str = self.model.report_stage_flow_model.current_report['flow_str']
        name_list = get_names_from_flow()
        self.frame.create_buttons(name_list)

    def handle_view_percent_reconciliation(self):
        # def show true false statistic
        name: str = self.frame.selected_btn
        print(f'DetailsController: handle_view_percent_reconciliation({name})')
        dataframe = self.model.base_data_frame_model.get_details_percent_reconciliation_dataframes(name)
        self.frame.select_right_button('true_false')
        self.frame.display_dataframe(dataframe)

    def handle_view_merge_statistic(self):
        # def show merge statistic
        name: str = self.frame.selected_btn
        print(f'DetailsController: handle_view_merge_statistic({name})')
        dataframe = self.model.base_data_frame_model.get_details_merge_dataframes(name)
        self.frame.select_right_button('merge')
        self.frame.display_dataframe(dataframe)

    def handle_view_data(self):
        # def show part of dataframe
        name: str = self.frame.selected_btn
        print(f'DetailsController: handle_view_merge_statistic({name})')
        dataframe = self.model.base_data_frame_model.get_details_data_dataframes(name)
        self.frame.select_right_button('data')
        self.frame.display_dataframe(dataframe)
