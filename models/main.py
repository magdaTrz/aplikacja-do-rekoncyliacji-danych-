from .auth import Auth


class Model:
    def __init__(self):
        print(f'Model: __init__()')
        self.auth = Auth()
