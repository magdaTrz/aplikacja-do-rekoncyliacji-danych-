from models.main import Model
from models.report_model import ReportStageFlowModel, BaseDataFrameModel, ReportModel
from views.main import View
from text_variables import TextEnum
from pydispatch import dispatcher

from controllers.progress_bar import ProgresBarStatus
from controllers.start import StartController
from controllers.stage import StageController
from controllers.flow_load import FlowLoadController
from controllers.flow_end import FlowEndController
from controllers.report import ReportController
from controllers.summary import SummaryController
from controllers.details import DetailsController

UPDATE_TEXT_SIGNAL = 'update_text'


class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.view = view
        self.model = model
        self.start_controller = StartController(model, view)
        self.stage_controller = StageController(model, view)
        self.flow_end_controller = FlowEndController(model, view)
        self.flow_load_controller = FlowLoadController(model, view)
        self.report_controller = ReportController(model, view)
        self.summary_controller = SummaryController(model, view)
        self.details_controller = DetailsController(model, view)

        self.model.report_stage_flow_model.add_event_listener("flow_changed", self.flow_state_listener)
        self.model.report_stage_flow_model.add_event_listener("view_to_report_changed",
                                                              self.view_to_report_state_listener)
        self.model.base_data_frame_model.add_event_listener("current_number_report_changed",
                                                            self.current_number_report_state_listener)
        self.model.base_data_frame_model.add_event_listener("save_report_path_changed",
                                                            self.save_report_path_state_listener)
        self.model.base_data_frame_model.add_event_listener("data_folder_report_path_changed",
                                                            self.data_folder_report_path_state_listener)
        self.model.report_model.add_event_listener("report_has_completed_event", self.report_has_ended_state_listener)
        self.model.base_data_frame_model.add_event_listener("view_summary_event", self.summary_view_state_listener)
        self.model.base_data_frame_model.add_event_listener("view_details_event", self.details_view_state_listener)
        self.model.base_data_frame_model.add_event_listener("password_changed", self.set_password_state_listener)

    def set_password_state_listener(self, data: ReportModel) -> None:
        password = self.model.base_data_frame_model.password_report
        self.model.report_model.set_password_to_report(password)

    def current_number_report_state_listener(self, data: BaseDataFrameModel) -> None:
        if data.current_number_report_is_changed:
            print(f'current_number_report_state_listener: {data.current_number_report}')
            self.report_controller.update_view_current_number_report()
            self.view.switch('report')

    def flow_state_listener(self, data: ReportStageFlowModel) -> None:
        if data.flow_is_changed and data.current_report.get("stage_str", None) == TextEnum.LOAD:
            self.flow_load_controller.update_view()
        elif data.flow_is_changed and data.current_report.get("stage_str", None) == TextEnum.END:
            self.flow_end_controller.update_view()

    def view_to_report_state_listener(self, data: ReportStageFlowModel) -> None:
        print(f'Controller: flow_state_listener({data.is_btn_clicked=})')
        if data.is_btn_clicked and data.current_report.get("stage_str", None) == TextEnum.LOAD:
            self.view.switch("report")
            self.report_controller.handle_generate_report()
        elif data.is_btn_clicked and data.current_report.get("stage_str", None) == TextEnum.END:
            self.report_controller.handle_generate_report()

    def data_folder_report_path_state_listener(self, data: BaseDataFrameModel) -> None:
        if data.save_report_path_is_changed:
            print(f'STATE LISTENER: data_folder_report_path_state_listener():')
            self.flow_load_controller.data_folder_report_path_update_view()

    def save_report_path_state_listener(self, data: BaseDataFrameModel) -> None:
        if data.save_report_path_is_changed:
            print(f'STATE LISTENER: save_report_path_state_listener(): {data.current_number_report}')
            self.flow_load_controller.save_report_folder_path_update_view()

    def report_has_ended_state_listener(self, data: ReportModel) -> None:
        if data.report_end_is_changed:
            print(f'STATE LISTENER: report_has_ended_state_listener():')
            dispatcher.send(signal=UPDATE_TEXT_SIGNAL, message=f"Zakończono pracę.", head='logi')
            ProgresBarStatus.set_100_percent()
            self.report_controller.update_view_report_ended()

    def summary_view_state_listener(self, data: BaseDataFrameModel) -> None:
        if data.update_summary_is_clicked:
            print(f'STATE LISTENER: summary_view_state_listener():')
            dataframe = data.get_summary_tech_info_dataframes()
            self.summary_controller.display_dataframe(dataframe)

    def details_view_state_listener(self, data: BaseDataFrameModel) -> None:
        if data.update_details_is_clicked:
            print(f'STATE LISTENER: details_view_state_listener():')
            self.details_controller.create_buttons()

    def start(self) -> None:
        self.view.switch("start")
        self.view.start_mainloop()
