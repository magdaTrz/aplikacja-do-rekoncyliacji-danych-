from models.main import Model
from models.report_model import Report
from views.main import View
from tkinter import filedialog


class FlowLoadController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.frame = self.view.frames["flow_load"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.back_btn.config(command=self.handle_back)
        self.frame.koi_btn.config(command=lambda: self.handle_selected_flow(flow='koi'))
        self.frame.umo_btn.config(command=lambda: self.handle_selected_flow(flow='umo'))
        self.frame.ksgpw_btn.config(command=lambda: self.handle_selected_flow(flow='ksgpw'))
        self.frame.ksgfin_btn.config(command=lambda: self.handle_selected_flow(flow='ksgfin'))
        self.frame.mate_btn.config(command=lambda: self.handle_selected_flow(flow='mate'))

        self.frame.filedialog_src_btn.config(command=lambda: self.choose_file('src'))
        self.frame.filedialog_ext_btn.config(command=lambda: self.choose_file('ext'))

        self.frame.start_btn.config(command=self.handle_generate_report)

    def handle_back(self) -> None:
        current_report = self.model.report_model.current_report
        print(f'FlowLoadController: handle_back(){current_report=}')
        self.frame.filedialog_src_btn.config(text=f"")
        self.frame.filedialog_ext_btn.config(text=f"")
        self.frame.header_filedialog.config(text=f"")
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('stage')

    def handle_selected_flow(self, flow: str) -> None:
        print(f'FlowLoadController: handle_selected_flow()')
        report = {"stage_str": "load", "flow_str": flow}
        self.model.report_model.report_save(report)

    def update_view(self):
        current_report = self.model.report_model.current_report
        print(f'FlowLoadController: update_view() {current_report=}')
        if current_report:
            stage = current_report["stage_str"]
            flow = current_report["flow_str"]

            btn_name = f'{current_report["flow_str"]}_btn'
            grid_info_btn = getattr(self.frame, btn_name).grid_info()
            btn_row = grid_info_btn['row']

            self.frame.header_filedialog.grid(row=btn_row)
            self.frame.filedialog_src_btn.grid(row=btn_row + 1)
            self.frame.filedialog_ext_btn.grid(row=btn_row + 2)

            self.frame.filedialog_src_label.config(text=f"")
            self.frame.filedialog_ext_label.config(text=f"")
            self.frame.filedialog_src_label.grid(row=btn_row + 1)
            self.frame.filedialog_ext_label.grid(row=btn_row + 2)

            self.frame.greeting.config(text=f"{stage} {flow}")
            self.frame.header_filedialog.config(text=f"Wybierz pliki dla {flow}")
            self.frame.filedialog_src_btn.config(text=f"File dialog src")
            self.frame.filedialog_ext_btn.config(text=f"File dialog ext")

            self.frame.start_btn.grid(row=3, column=4)
            self.frame.start_btn.config(text=f"Rekoncyliuj")

    def choose_file(self, btn_type: str) -> None:
        print(f'FlowLoadController: choose_file({btn_type})')
        file_path = filedialog.askopenfilename(
            title='Wybierz plik',
            filetypes=[('Pliki tekstowe', '*.txt'), ('Wszsytkie pliki', '*.*')]
        )
        if file_path:
            if btn_type == 'src':
                self.model.report_model.path_save('path_1', file_path)
                self.frame.filedialog_src_label.config(text=file_path)
            else:
                self.model.report_model.path_save('path_2', file_path)
                self.frame.filedialog_ext_label.config(text=file_path)
            print(file_path)
        else:
            self.frame.filedialog_src_label.config(text='Brak')
            self.frame.filedialog_ext_label.config(text='Brak')

    def handle_generate_report(self) -> None:
        print(f'FlowLoadController: handle_generate_report()')
        print(self.model.report_model.path_1)
        print(self.model.report_model.path_2)
        print(self.model.report_model.current_report)

