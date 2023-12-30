from typing import TypedDict

from .root import Root
# from .home import HomeView
from .stage import StageView
from .start import StartView
from .signup import SignUpView
from .flow import FlowView

class Frames(TypedDict):
    start: StartView
    stage: StageView
    flow: FlowView
    signup: SignUpView


class View:
    def __init__(self):
        self.root = Root()
        self.frames: Frames = {}  # type: ignore

        self._add_frame(StartView, 'start')
        self._add_frame(StageView, 'stage')
        self._add_frame(FlowView, 'flow')
        self._add_frame(SignUpView, "signup")

    def _add_frame(self, Frame, name: str) -> None:
        self.frames[name] = Frame(self.root)
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    def switch(self, name: str) -> None:
        print(f'View: switch({name})')
        frame = self.frames[name]
        frame.tkraise()

    def start_mainloop(self) -> None:
        self.root.mainloop()
