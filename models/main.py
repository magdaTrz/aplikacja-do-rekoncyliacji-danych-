from .support_files import SupportFiles
from .report_model import ReportModel


class Model:
    def __init__(self):
        self.support_files = SupportFiles()
        self.report_model = ReportModel()
