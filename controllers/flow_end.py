from models.main import Model
from models.auth import Report
from views.main import View
from tkinter import filedialog


class FlowEndController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.frame = self.view.frames["flow_end"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.back_btn.config(command=self.handle_back)
        self.frame.koi_btn.config(command=lambda: self.handle_selected_flow(flow='koi'))
        self.frame.umo_btn.config(command=lambda: self.handle_selected_flow(flow='umo'))


    def handle_back(self) -> None:
        current_report = self.model.report_model.current_report
        print(f'FlowLoadController: handle_back(){current_report=}')
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('stage')

    def handle_selected_flow(self, flow: str) -> None:
        print(f'FlowLoadController: handle_selected_flow()')
        report = {"stage_str": "end", "flow_str": flow}
        self.model.report_model.report_save(report)

    def update_view(self):
        current_report = self.model.report_model.current_report
        print(f'FlowLoadController: update_view() {current_report=}')
        if current_report:
            stage = current_report["stage_str"]
            flow = current_report["flow_str"]
            self.frame.greeting.config(text=f"{stage} {flow}")
            self.frame.filedialog_ext_btn.config(text=f"File dialog ext")
            self.frame.filedialog_tgt_btn.config(text=f"File dialog tgt")

            grid_info_src_btn = self.frame.filedialog_src_btn.grid_info()
            print(grid_info_src_btn)

        else:
            self.frame.filedialog_src_btn.config(text=f"Brak")
            self.frame.filedialog_ext_btn.config(text=f"Brak")
