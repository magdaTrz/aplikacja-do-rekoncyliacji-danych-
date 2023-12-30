from typing import TypedDict, Union
from .base import ObservableModel


class Report(TypedDict):
    stage_str: str
    flow_str: str


class Auth(ObservableModel):
    def __init__(self):
        super().__init__()
        self.is_stage_in = False
        self.current_report: Union[Report, None] = None

    def login(self, report: Report) -> None:
        print(f'Auth: login()')
        self.is_stage_in = True
        self.current_report = report
        self.trigger_event("auth_changed")

    def logout(self) -> None:
        print(f'Auth: logout()')
        self.is_stage_in = False
        self.current_report = None
        self.trigger_event("auth_changed")
