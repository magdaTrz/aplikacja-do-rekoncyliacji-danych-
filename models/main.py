from .support_files import SupportFiles
from .report_model import ReportModel
from .report_model import BaseDataFrameModel
from .dict_update import DictUpdate


class Model:
    def __init__(self):
        self.support_files = SupportFiles()
        self.dict_update = DictUpdate()
        self.report_model = ReportModel()
        self.base_data_frame_model = BaseDataFrameModel()
