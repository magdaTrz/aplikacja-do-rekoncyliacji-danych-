from typing import TypedDict, Union
from .base import ObservableModel
import pandas

class Report(TypedDict):
    stage_str: str
    flow_str: str


def delete_unmigrated_records(dataframe):
    unmigrated_dataframe = pandas.read_csv('support_file_unmigrated_id.csv')
    return dataframe[~dataframe['numer'].isin(unmigrated_dataframe['numer'])]


def mapp_values(dataframe, column_to_fill, column_to_take, map_dict):
    if column_to_fill not in dataframe.columns:
        raise ValueError(f"Kolumna {column_to_fill} nie istnieje w DataFrame.")
    if column_to_take not in dataframe.columns:
        raise ValueError(f"Kolumna {column_to_take} nie istnieje w DataFrame.")
    dataframe.loc[:, column_to_fill] = dataframe[column_to_take].map(map_dict).fillna(dataframe[column_to_fill])
    return dataframe


class ReportModel(ObservableModel):
    def __init__(self):
        super().__init__()
        self.flow_is_changed = False
        self.current_report: Union[Report, None] = None
        self.path_1 = None
        self.path_2 = None
        print(self.current_report)

    def report_save(self, report: Report) -> None:
        print(f'ReportModel: report_save({report=})')
        print(self.current_report)
        self.flow_is_changed = True
        self.current_report = report
        self.trigger_event("flow_changed")

    def path_save(self, path_type, path):
        if path_type == 'path_1':
            self.path_1 = path
        else:
            self.path_2 = path
        print(f"{self.path_1=} {self.path_2=}")
        self.trigger_event("flow_changed")

    def report_clear(self) -> None:
        print(f'ReportModel: report_clear({self.flow_is_changed=})')
        print(f'ReportModel: report_clear({self.current_report=})')
        self.flow_is_changed = False
        self.current_report = None
        self.trigger_event("flow_changed")
        