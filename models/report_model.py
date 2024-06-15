import os
import pandas
from typing import TypedDict, Union, Any, Dict
from text_variables import TextEnum
from pandas import DataFrame
from pandas.errors import ParserError
from pydispatch import dispatcher

from controllers.progress_bar import ProgresBarStatus
from models.base import ObservableModel
from models.custom_exceptions import ReconciliationFileNotFoundError
import paths

UPDATE_TEXT_SIGNAL = 'update_text'


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
        self.password_report: str | None = None
        self.data_folder_report_path = ''
        self.data_folder_report_path_is_changed = False
        self.save_report_folder_path = ''
        self.save_report_path_is_changed = False
        self.migration_date = ''
        self.update_summary_is_clicked: bool = False
        self.summary_tech_info_dataframes: pandas.DataFrame = \
            pandas.DataFrame({'Raport': [], 'Plik Excel': [], 'Status': [], 'Czas wykonywania': []})
        self.update_details_is_clicked = False
        self.details_percent_reconciliation_info_dataframes: Dict[str, pandas.DataFrame] = {}
        self.details_merge_info_dataframes: Dict[str, pandas.DataFrame] = {}
        self.details_data_info_dataframes: Dict[str, pandas.DataFrame] = {}

    def set_password_to_report(self, password: str):
        print(f"set_password_to_report(): {password} ")
        self.password_report = password
        self.trigger_event('password_changed')

    def set_save_report_folder_path(self, path: str):
        self.save_report_path_is_changed = True
        self.save_report_folder_path = path
        self.trigger_event('save_report_path_changed')

    def set_data_folder_path(self, path: str):
        self.data_folder_report_path_is_changed = True
        self.data_folder_report_path = path
        self.trigger_event('data_folder_report_path_changed')

    def add_value_summary_dataframes(self, new_row_data: pandas.DataFrame):
        print(f'BaseDataFrameModel: add_value_summary_dataframes():')
        self.summary_tech_info_dataframes = pandas.concat(
            [self.summary_tech_info_dataframes, pandas.DataFrame([new_row_data])], ignore_index=True)

    def get_summary_tech_info_dataframes(self):
        print(f'BaseDataFrameModel: get_summary_tech_info_dataframes():')
        return self.summary_tech_info_dataframes

    def add_value_details_percent_reconciliation_dataframes(self, name: str, dataframe: pandas.DataFrame):
        print(f'BaseDataFrameModel: add_value_details_percent_reconciliation_dataframes():')
        self.details_percent_reconciliation_info_dataframes[name] = dataframe

    def get_details_percent_reconciliation_dataframes(self, name: str) -> pandas.DataFrame:
        print(f'BaseDataFrameModel: get_details_percent_reconciliation_dataframes():')
        if name in self.details_percent_reconciliation_info_dataframes:
            return self.details_percent_reconciliation_info_dataframes[name]
        else:
            print(f"DataFrame with name '{name}' not found.")
            return pandas.DataFrame({"Informacja": ["brak danych"]})

    def add_value_details_merge_dataframes(self, name: str, dataframe: pandas.DataFrame):
        print(f'BaseDataFrameModel:add_value_details_merge_dataframes():')
        self.details_merge_info_dataframes[name] = dataframe

    def get_details_merge_dataframes(self, name: str) -> pandas.DataFrame:
        print(f'BaseDataFrameModel:get_details_merge_dataframes():')
        if name in self.details_merge_info_dataframes:
            return self.details_merge_info_dataframes[name]
        else:
            print(f"DataFrame with name '{name}' not found.")
            return pandas.DataFrame({"Informacja": ["brak danych"]})

    def add_value_details_data_dataframes(self, name: str, dataframe: pandas.DataFrame):
        print(f'BaseDataFrameModel:add_value_details_data_dataframes():')
        self.details_data_info_dataframes[name] = dataframe

    def get_details_data_dataframes(self, name: str) -> pandas.DataFrame:
        print(f'BaseDataFrameModel:get_details_data_dataframes():')
        if name in self.details_data_info_dataframes:
            return self.details_data_info_dataframes[name]
        else:
            print(f"DataFrame with name '{name}' not found.")
            return pandas.DataFrame({"Informacja": ["brak danych"]})

    def set_migration_date(self, date: str):
        print(f"BaseDataFrameModel: set_migration_date(): {date}")
        self.migration_date = date

    def update_current_number_report(self, number: int):
        self.current_number_report_is_changed = True
        self.current_number_report = number
        self.trigger_event('current_number_report_changed')

    def add_data_to_summary_view(self) -> None:
        self.update_summary_is_clicked = True
        self.trigger_event("view_summary_event")

    def add_buttons_to_details(self) -> None:
        self.update_details_is_clicked = True
        self.trigger_event("view_details_event")

    @staticmethod
    def read_excel_sheet(file_path: str) -> pandas.DataFrame:
        print(f'BaseDataFrameModel: read_excel_sheet():')
        excel_data = pandas.ExcelFile(file_path)
        data_frames = []

        for sheet_name in excel_data.sheet_names:
            df = pandas.read_excel(file_path, sheet_name=sheet_name)

            if '_merge' in df.columns:
                merge_idx = df[df['_merge'].notna()].index[0]
                df = df.iloc[:merge_idx - 2, :]

            new_columns = []
            for col in df.columns:
                if col.startswith('Unnamed'):
                    new_columns.append('')
                else:
                    new_columns.append(col)
            df.columns = new_columns

            df = df.iloc[:, :4]

            df['Sheet'] = sheet_name
            data_frames.append(df.head(10))

        combined_df = pandas.concat(data_frames, ignore_index=True)
        combined_df = combined_df.fillna('')
        return combined_df


class ReportModel(ObservableModel):
    def __init__(self):
        super().__init__()
        print(f"ReportModel(): init class")
        self.report_end_is_changed = False
        self.password_report: str | None = None

    def update_view_report(self):
        self.report_end_is_changed = True
        self.trigger_event('report_has_completed_event')

    def set_password_to_report(self, password: str):
        print(f"set_password_to_report(): {password} ")
        self.password_report = password

    @staticmethod
    def set_colum_names(col_names: dict[int, str], dataframe: pandas.DataFrame) -> pandas.DataFrame:
        print('ReportModel: set_colum_names()')
        try:
            ProgresBarStatus.increase()
            if dataframe.empty:
                print('ReportModel: set_colum_names(): ERROR: Dataframe is empty')
            elif dataframe is not None:
                dataframe = dataframe.rename(columns=col_names)
                ProgresBarStatus.increase()
                return dataframe
            else:
                dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Dataframe jest pusta", head='fail')
                print('ReportModel: set_colum_names(): ERROR: Dataframe is None')
        except pandas.errors.ParserError:
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd nadawania nazw kolum", head='fail')
            print('ReportModel: set_colum_names(): ERROR: ParserError')
            return pandas.DataFrame()
        except AttributeError:
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Błąd AttributeError podczas nadawania nazw",
                            head='fail')
            print('ReportModel: set_colum_names(): ERROR: AttributeError')
            return pandas.DataFrame()

    @staticmethod
    def delete_unmigrated_records(dataframe: pandas.DataFrame, column_name: str = 'numer') -> pandas.DataFrame:
        path = os.path.join(os.getcwd(), '_logi')
        path_to_file = os.path.join(path, '_reko_plik_pomocniczy_niemigrowane_id.csv')
        unmigrated_dataframe = pandas.read_csv(path_to_file)
        dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Usunięto klientów niemigrowanych", head='Success')
        return dataframe[~dataframe[column_name].isin(unmigrated_dataframe['numer'])]

    @staticmethod
    def delete_empty_columns(dataframe: pandas.DataFrame) -> pandas.DataFrame:
        empty_col = dataframe.columns[dataframe.isnull().all()]
        dataframe = dataframe.drop(columns=empty_col)
        return dataframe

    @staticmethod
    def mapp_values(dataframe, columns_to_fill, columns_to_take, map_dict) -> pandas.DataFrame:
        if not isinstance(map_dict, dict):
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Wybrany słownik nie jest słownikiem.",
                            head='fail')
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
                    dataframe = pandas.read_csv(dir_str_path, sep=sep, header=None, low_memory=False, encoding='utf-8')
                else:
                    dataframe = pandas.read_csv(dir_str_path, sep=sep, header=None, low_memory=False, dtype=dtype,
                                                encoding='utf-8')
                ProgresBarStatus.increase()
                dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Inicjalizowanie procesu tworzenia dataframe",
                                head='info')
                return dataframe
            except ParserError:
                dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                                message=f"Błąd inicjalizowania pliku, wykryto błąd w strukturze pliku: {path_to_file}",
                                head='fail')
                print(f"make_dataframe_from_file() ParserError")
                return pandas.DataFrame
        else:
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL,
                            message=f"Błąd inicjalizowania pliku, nie znaleziono pliku w folderze: {path_to_file}",
                            head='fail')
            return pandas.DataFrame

    @staticmethod
    def modify_filename(filename, stage):
        if stage == TextEnum.LOAD:
            filename = filename.replace(".xlsx", "_Go4Load.xlsx")
        elif stage == TextEnum.END:
            filename = filename.replace(".xlsx", "_Go4EndDay.xlsx")
        return filename
