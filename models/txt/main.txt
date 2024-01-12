from .support_files import SupportFiles
from .report_model import ReportModel
from .report_model import BaseDataFrameModel


class Model:
    def __init__(self):
        self.support_files = SupportFiles()
        self.report_model = ReportModel()
        self.base_data_frame_model = BaseDataFrameModel()
