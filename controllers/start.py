from models.main import Model
from models.report_model import Report
from views.main import View


class StartController:
    def __init__(self, model: Model, view: View) -> None:
        print(f'StartController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["start"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        print(f'StartController: _bind()')
        self.frame.start_btn.config(command=self.start)

    def start(self) -> None:
        print(f'StartController: start()')
        self.view.switch('stage')
