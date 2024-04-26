import os
from typing import TypedDict, Union, Any

from pandas import DataFrame
from pandas.errors import ParserError

from controllers.progress_bar import ProgresBarStatus
from models.base import ObservableModel
from models.custom_exceptions import ReconciliationFileNotFoundError
import pandas
import paths


class Report(TypedDict):
    stage_str: str
    flow_str: str


class ReportModel(ObservableModel):
    def __init__(self):
        super().__init__()
        self.flow_is_changed = False
        self.current_report: Union[Report, None] = None
        self.is_btn_clicked = False

    def call_the_report_generation_function(self):
        self.is_btn_clicked = True
        self.trigger_event("view_to_report_changed")

    def report_save(self, report: Report) -> None:
        self.flow_is_changed = True
        self.current_report = report
        self.trigger_event("flow_changed")

    def report_clear(self) -> None:
        self.flow_is_changed = False
        self.current_report = None
        self.trigger_event("flow_changed")


class BaseDataFrameModel(ObservableModel):
    def __init__(self):
        super().__init__()
        self.progress_value_is_changed = False
        self.current_number_report = 1
        self.current_number_report_is_changed = False
        self.number_of_reports = 1
        self.data_folder_report_path = ''
        self.save_report_folder_path = ''

    def set_save_report_folder_path(self, path: str):
        print(f'set_save_report_folder_path(): {path}')
        self.save_report_folder_path = path

    def set_data_folder_path(self, path: str):
        print(f'set_data_folder_path(): {path}')
        self.save_report_folder_path = path

    @property
    def dir_path(self) -> str:
        return self.directory_path

    @dir_path.setter
    def dir_path(self, path):
        self.directory_path = path

    def update_current_number_report(self, number: int):
        self.current_number_report_is_changed = True
        self.current_number_report = number
        self.trigger_event('current_number_report_changed')

    def make_dataframe_from_file(self, path_to_file: str) -> DataFrame | ReconciliationFileNotFoundError | Any:
        dir_str_path = os.path.join(self.dir_path, path_to_file)
        if os.path.exists(dir_str_path):
            try:
                dataframe = pandas.read_csv(dir_str_path, sep='|', header=None, low_memory=False)
                ProgresBarStatus.increase()
                return dataframe
            except ParserError:
                # TODO: Obsłużyć taki wyjątek.
                return
        else:
            return ReconciliationFileNotFoundError()

    def set_colum_names(self, col_names: dict[int, str], dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('BaseDataFrameModel: set_colum_names()')
        try:
            ProgresBarStatus.increase()
            if dataframe is not None:
                dataframe = dataframe.rename(columns=col_names)
                ProgresBarStatus.increase()
                return dataframe
            else:
                print('BaseDataFrameModel: set_colum_names(): ERROR: Dataframe is None')
        except pandas.errors.ParserError:
            print('BaseDataFrameModel: set_colum_names(): ERROR: ParserError')

    def delete_unmigrated_records(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        unmigrated_dataframe = pandas.read_csv('support_file_unmigrated_id.csv')
        return dataframe[~dataframe['numer'].isin(unmigrated_dataframe['numer'])]

    def delete_empty_columns(self, dataframe: pandas.DataFrame) -> pandas.DataFrame:
        empty_col = dataframe.columns[dataframe.isnull().all()]
        dataframe = dataframe.drop(columns=empty_col)
        return dataframe

    def mapp_values(self, dataframe, column_to_fill, column_to_take, map_dict) -> pandas.DataFrame:
        if column_to_fill not in dataframe.columns:
            raise ValueError(f"Kolumna {column_to_fill} nie istnieje w DataFrame.")
        if column_to_take not in dataframe.columns:
            raise ValueError(f"Kolumna {column_to_take} nie istnieje w DataFrame.")
        dataframe.loc[:, column_to_fill] = dataframe[column_to_take].map(map_dict).fillna(dataframe[column_to_fill])
        return dataframe

