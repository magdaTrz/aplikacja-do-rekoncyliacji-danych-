from .support_files import SupportFiles
from .report_model import ReportStageFlowModel
from .report_model import BaseDataFrameModel
from .report_model import ReportModel
from .dict_update import DictUpdate


class Model:
    def __init__(self):
        self.support_files = SupportFiles()
        self.dict_update = DictUpdate()
        self.report_stage_flow_model = ReportStageFlowModel()
        self.base_data_frame_model = BaseDataFrameModel()
        self.report_model = ReportModel()
