from models.support_files import SupportFiles
from models.report_model import ReportStageFlowModel
from models.report_model import BaseDataFrameModel
from models.report_model import ReportModel
from models.dict_update import DictUpdate


class Model:
    def __init__(self):
        self.support_files = SupportFiles()
        self.dict_update = DictUpdate()
        self.report_stage_flow_model = ReportStageFlowModel()
        self.base_data_frame_model = BaseDataFrameModel()
        self.report_model = ReportModel()
