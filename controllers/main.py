from models.main import Model
from models.report_model import ReportModel
from views.main import View

from .stage import StageController
from .flow_load import FlowLoadController
from .flow_end import FlowEndController
from .signin import SignInController
from .signup import SignUpController


class Controller:
    def __init__(self, model: Model, view: View) -> None:
        self.view = view
        self.model = model
        self.signin_controller = SignInController(model, view)
        self.signup_controller = SignUpController(model, view)
        self.stage_controller = StageController(model, view)
        self.flow_load_controller = FlowLoadController(model, view)
        self.flow_end_controller = FlowEndController(model, view)

        # self.model.auth.add_event_listener("auth_changed", self.auth_state_listener)
        self.model.report_model.add_event_listener("flow_changed", self.flow_state_listener)

    def flow_state_listener(self, data: ReportModel) -> None:
        print(f'Controller: flow_state_listener({data.current_report=})')
        # self.flow_load_controller.update_view()
        if data.flow_is_changed and data.current_report.get("stage_str", None) == 'load':
            self.flow_load_controller.update_view()
        elif data.flow_is_changed and data.current_report.get("stage_str", None) == 'end':
            self.flow_end_controller.update_view()

    # def auth_state_listener(self, data: Auth) -> None:
    #     print(f'Controller: auth_state_listener({data})')
    #     self.stage_controller.update_view()
    #     if data.is_stage_in:
    #         self.stage_controller.update_view()
    #         self.view.switch('flow_load')
    #     else:
    #         self.view.switch("start")

    def start(self) -> None:
        # Here, you can do operations required before launching the gui, for example,
        # self.model.auth.load_auth_state()
        print(f'Controller: start()')
        self.view.switch("start")
        self.view.start_mainloop()
