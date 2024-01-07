from typing import TypedDict, Union

from models.base import ObservableModel
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
        self.directory_path = f'{paths.current_working_dir}\dane'

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


class BaseDataFrameModel(ObservableModel):
    def __init__(self):
        super().__init__()
        self.current_number_report = 1
        self.current_number_report_is_changed = False
        self.number_of_reports = 1
        self.dir_path = None
        self.path_src = None
        self.path_ext = None
        self.path_tgt = None
        self.progress_value = 0

    def get_dir_path(self) -> str:
        return self.dir_path

    def increase_progress_value(self):
        self.progress_value += 5
        self.trigger_event("current_number_report_changed")
        return self.progress_value

    def perform_operations(self, dir_path: str, stage: str, flow: str):
        print(f'BaseDataFrameModel: perform_operations({dir_path}, {flow})')
        self.dir_path = dir_path
        for path_info in eval(f'paths.{flow}_paths'):
            print(f' {path_info}')
            if stage == 'load':
                print('  load')
                if flow == 'koi':
                    from models.koi.oi_telecom import OiTelecom

                    self.number_of_reports = 7
                    self.progress_value = 4
                    if path_info['name'] == 'osoby_instytucje':
                        pass
                    if path_info['name'] == 'oi_password':
                        pass
                    if path_info['name'] == 'oi_numb':
                        pass
                    if path_info['name'] == 'oi_adresy':
                        pass
                    if path_info['name'] == 'oi_atryb':
                        pass
                    if path_info['name'] == 'oi_telecom':
                        OiTelecom(path_src=path_info['src'], path_ext=path_info['ext'])
                    # self.current_number_report_is_changed = True
                    # self.make_dataframe_from_file()
                    #
                elif flow == 'umo':
                    self.number_of_reports = 5

            if stage == 'end':
                if flow == 'koi':
                    self.number_of_reports = 7

    def make_dataframe_from_file(self, path_to_file: str) -> pandas.DataFrame:
        dataframe = pandas.read_csv(path_to_file, sep='|', header=None, low_memory=False)
        self.increase_progress_value()
        return dataframe

    def set_colum_names(self, col_names: dict[int, str], dataframe: pandas.DataFrame):
        print('BaseDataFrameModel: set_colum_names()')
        self.increase_progress_value()
        try:
            if dataframe is not None:
                dataframe = dataframe.rename(columns=col_names)
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
