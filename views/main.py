from typing import TypedDict

from views.root import Root
from views.stage import StageView
from views.start import StartView

from views.flow_load import FlowLoadView
from views.flow_end import FlowEndView
from views.report import ReportView
from views.summary import SummaryView
from views.details import DetailsView


class Frames(TypedDict):
    start: StartView
    stage: StageView
    flow_load: FlowLoadView
    flow_end: FlowEndView
    report: ReportView
    summary: SummaryView
    details: DetailsView


class View:
    def __init__(self):
        self.root = Root()
        self.frames: Frames = {}  # type: ignore

        self._add_frame(StartView, 'start')
        self._add_frame(StageView, 'stage')
        self._add_frame(FlowLoadView, 'flow_load')
        self._add_frame(FlowEndView, 'flow_end')
        self._add_frame(ReportView, 'report')
        self._add_frame(SummaryView, 'summary')
        self._add_frame(DetailsView, 'details')

    def _add_frame(self, Frame, name: str) -> None:
        self.frames[name] = Frame(self.root)
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    def switch(self, name: str) -> None:
        print(f'View: switch({name})')
        frame = self.frames[name]
        frame.tkraise()

    def start_mainloop(self) -> None:
        self.root.mainloop()
