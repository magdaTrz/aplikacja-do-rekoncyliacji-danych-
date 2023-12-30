from .auth import Auth
from .support_files import SupportFiles


class Model:
    def __init__(self):
        self.auth = Auth()
        self.support_files = SupportFiles()
