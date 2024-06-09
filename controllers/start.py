from models.main import Model
from views.main import View


class StartController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.frame = self.view.frames["start"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.start_btn.config(command=self.start)

    def start(self) -> None:
        self.view.switch('stage')
