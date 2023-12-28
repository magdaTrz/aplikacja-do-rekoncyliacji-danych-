from .auth import Auth
from .support_files import SupportFiles


class Model:
    def __init__(self):
        print(f'Model: __init__()')
        self.auth = Auth()
        self.support_files = SupportFiles()
