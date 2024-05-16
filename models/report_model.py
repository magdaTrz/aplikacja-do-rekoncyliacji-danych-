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


class ReportStageFlowModel(ObservableModel):
    def __init__(self):
        super().__init__()
        self.flow_is_changed: bool = False
        self.current_report: Union[Report, None] = None
        self.is_btn_clicked: bool = False

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
        self.number_of_reports = 6
        self.data_folder_report_path = ''
        self.data_folder_report_path_is_changed = False
        self.save_report_folder_path = ''
        self.save_report_path_is_changed = False
        self.password_report = ''
        self.migration_date = ''
        self.update_summary_is_clicked: bool = False
        self.summary_dataframes_dataframe: pandas.DataFrame = \
            pandas.DataFrame({'Raport': [], 'Plik Excel': [], 'Status': [], 'Czas wykonywania': []})

    def set_save_report_folder_path(self, path: str):
        print(f'MODEL: BaseDataFrameModel(): set_save_report_folder_path(): {path}')
        self.save_report_path_is_changed = True
        self.save_report_folder_path = path
        self.trigger_event('save_report_path_changed')

    def set_data_folder_path(self, path: str):
        print(f'set_data_folder_path(): {path}')
        self.data_folder_report_path_is_changed = True
        self.data_folder_report_path = path
        self.trigger_event('data_folder_report_path_changed')

    def add_value_to_summary_dataframes_dict(self, new_row_data: pandas.DataFrame):
        print(f'add_value_to_summary_dataframes_dict():')
        self.summary_dataframes_dataframe = pandas.concat(
            [self.summary_dataframes_dataframe, pandas.DataFrame([new_row_data])], ignore_index=True)

    def get_all_summary_dataframes(self):
        print(f'BaseDataFrameModel:get_all_summary_dataframes():')
        return self.summary_dataframes_dataframe

    def set_password_to_report(self, password: str):
        print(f"set_password_to_report(): {password} ")
        self.password_report = password

    def set_migration_date(self, date: str):
        print(f"set_migration_date(): {date}")
        self.migration_date = date

    def update_current_number_report(self, number: int):
        self.current_number_report_is_changed = True
        self.current_number_report = number
        self.trigger_event('current_number_report_changed')

    def add_data_to_summary_view(self) -> None:
        self.update_summary_is_clicked = True
        self.trigger_event("view_summary_event")


class ReportModel(ObservableModel):
    def __init__(self):
        super().__init__()
        print(f"ReportModel(): init class")
        self.report_end_is_changed = False

    def update_view_report(self):
        self.report_end_is_changed = True
        self.trigger_event('report_has_completed_event')

    @staticmethod
    def set_colum_names(col_names: dict[int, str], dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('ReportModel: set_colum_names()')
        try:
            ProgresBarStatus.increase()
            if dataframe is not None:
                dataframe = dataframe.rename(columns=col_names)
                ProgresBarStatus.increase()
                return dataframe
            else:
                print('ReportModel: set_colum_names(): ERROR: Dataframe is None')
        except pandas.errors.ParserError:
            print('ReportModel: set_colum_names(): ERROR: ParserError')
            return pandas.DataFrame()
        except AttributeError:
            print('ReportModel: set_colum_names(): ERROR: AttributeError')
            return pandas.DataFrame()

    @staticmethod
    def delete_unmigrated_records(dataframe: pandas.DataFrame, column_name: str='numer') -> pandas.DataFrame:
        path = os.path.join(os.getcwd(), '_logi')
        path_to_file = os.path.join(path, '_reko_plik_pomocniczy_niemigrowane_id.csv')
        unmigrated_dataframe = pandas.read_csv(path_to_file)
        return dataframe[~dataframe[column_name].isin(unmigrated_dataframe['numer'])]

    @staticmethod
    def delete_empty_columns(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        empty_col = dataframe.columns[dataframe.isnull().all()]
        dataframe = dataframe.drop(columns=empty_col)
        return dataframe

    @staticmethod
    def mapp_values(dataframe, columns_to_fill, columns_to_take, map_dict) -> pandas.DataFrame:
        if not isinstance(map_dict, dict):
            raise ValueError("map_dict powinien być słownikiem.")

        missing_columns = [col for col in columns_to_fill + columns_to_take if col not in dataframe.columns]
        if missing_columns:
            raise ValueError(f"Kolumny {missing_columns} nie istnieją w DataFrame.")

        for fill_col, take_col in zip(columns_to_fill, columns_to_take):
            dataframe[fill_col] = dataframe[take_col].map(map_dict).fillna(dataframe[fill_col])

        return dataframe

    @staticmethod
    def make_dataframe_from_file(path_to_file: str,
                                 path_to_folder: str, dtype=None,
                                 sep='|') -> DataFrame | ReconciliationFileNotFoundError | Any:
        dir_str_path = os.path.join(path_to_folder, path_to_file)
        if os.path.exists(dir_str_path):
            try:
                if dtype is None:
                    dataframe = pandas.read_csv(dir_str_path, sep=sep, header=None, low_memory=False)
                else:
                    dataframe = pandas.read_csv(dir_str_path, sep=sep, header=None, low_memory=False, dtype=dtype)
                ProgresBarStatus.increase()
                return dataframe
            except ParserError:
                print(f"make_dataframe_from_file() ParserError")
                # TODO: Obsłużyć taki wyjątek.
                return
        else:
            return ReconciliationFileNotFoundError()
