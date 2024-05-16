import os
import time
import tkinter as tk

import openpyxl
import pandas

from models.main import Model
from views.main import View
from threading import Thread
from paths import flow_paths
from text_variables import TextGenerator, TextEnum
from controllers.progress_bar import ProgresBarStatus


class SummaryController:
    def __init__(self, model: Model, view: View):
        print(f'SummaryController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["summary"]
        self._bind()

    def _bind(self) -> None:
        self.frame.back_btn.config(command=self.handle_back)

    def handle_back(self) -> None:
        self.view.switch('report')

    def display_dataframe(self, dataframes):
        self.frame.display_dataframe(dataframes)
