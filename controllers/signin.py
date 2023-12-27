from models.main import Model
from models.auth import Report
from views.main import View


class SignInController:
    def __init__(self, model: Model, view: View) -> None:
        print(f'SignInController: __init__()')
        self.model = model
        self.view = view
        self.frame = self.view.frames["start"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        print(f'SignInController: _bind()')
        self.frame.start_btn.config(command=self.start)
        self.frame.signup_btn.config(command=self.signup)

    def signup(self) -> None:
        print(f'SignInController: signup()')
        self.view.switch("signup")

    def signin(self) -> None:
        print(f'SignInController: signin() przekazywanie atrybutów')
        username = self.frame.username_input.get()
        pasword = self.frame.password_input.get()
        data = {"username": username, "password": pasword}
        print(data)
        self.frame.password_input.delete(0, last=len(pasword))
        user: Report = {"username": data["username"]}
        self.model.auth.login(user)

    def start(self) -> None:
        print(f'SignInController: start()')
        self.view.switch('stage')
