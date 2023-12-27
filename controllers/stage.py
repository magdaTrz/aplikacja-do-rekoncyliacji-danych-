from models.main import Model
from models.auth import Report
from views.main import View


class StageController:
    def __init__(self, model: Model, view: View) -> None:
        print(f'StageController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["stage"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        print(f'StageController: _bind()')
        self.frame.reportload_btn.config(command=lambda: self.handle_selected_stage(stage='load'))
        self.frame.reportend_btn.config(command=lambda: self.handle_selected_stage(stage='end'))

        self.frame.back_btn.config(command=self.handle_back)

    def handle_back(self) -> None:
        current_report = self.model.auth.current_report
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('start')

    def logout(self) -> None:
        print(f'StageController: logout()')
        self.model.auth.logout()

    def handle_selected_stage(self, stage: str) -> None:
        report: Report = {'stage_str': stage,
                          'flow_str': ''}
        self.model.auth.login(report)
        print(f'StageController: handle_selected_stage({stage})')
        # if current_report:
        #     current_report.stage_str = stage
        #     self.frame.greeting.config(text=f"Welcome, {stage}!")
        # else:
        #     self.frame.greeting.config(text=f"Brak")

    def update_view(self):
        current_report = self.model.auth.current_report
        if current_report:
            stage = current_report["stage_str"]
            self.frame.greeting.config(text=f"Welcome, {stage}!")
        else:
            self.frame.greeting.config(text=f"Brak")
