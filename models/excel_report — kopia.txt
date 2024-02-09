from zipfile import BadZipFile

import numpy
import openpyxl
from  openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from models.base import ObservableModel

import pandas
import time


class ExcelReport(ObservableModel):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
        try:
            self.workbook = openpyxl.load_workbook(self.file_name)
        except FileNotFoundError:
            self.workbook = openpyxl.Workbook()
        except BadZipFile:
            self.workbook = openpyxl.Workbook()
            self.file_name = self.file_name[:-6]+'_BadZipFile'+self.file_name[-6:]
        self.sheet = self.workbook.active
