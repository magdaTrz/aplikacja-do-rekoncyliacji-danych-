from .auth import Auth
from .support_files import SupportFiles
from .auth import ReportModel


class Model:
    def __init__(self):
        self.auth = Auth()
        self.support_files = SupportFiles()
        self.report_model = ReportModel()
