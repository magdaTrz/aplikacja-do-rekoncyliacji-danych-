from models.main import Model
from models.auth import Auth
from views.main import View

from .stage import StageController
from .signin import SignInController
from .signup import SignUpController


class Controller:
    def __init__(self, model: Model, view: View) -> None:
        print(f'Controller: __init__()')
        self.view = view
        self.model = model
        self.signin_controller = SignInController(model, view)
        self.signup_controller = SignUpController(model, view)
        self.stage_controller = StageController(model, view)

        self.model.auth.add_event_listener("auth_changed", self.auth_state_listener)

    def auth_state_listener(self, data: Auth) -> None:
        print(f'Controller: auth_state_listener({data})')
        self.stage_controller.update_view()
        if data.is_stage_in:
            self.stage_controller.update_view()
            self.view.switch('flow')
        else:
            self.view.switch("start")

    def start(self) -> None:
        # Here, you can do operations required before launching the gui, for example,
        # self.model.auth.load_auth_state()
        print(f'Controller: start()')
        self.view.switch("start")
        # if self.model.auth.is_logged_in:
        #     self.view.switch("home")
        # else:
        #     self.view.switch("start")

        self.view.start_mainloop()
