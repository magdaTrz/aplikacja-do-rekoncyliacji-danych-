from .base import ObservableModel
from paths import path_dict_folder


class DictUpdate(ObservableModel):
    def __init__(self):
        super().__init__()
        self._path_dict_folder = path_dict_folder
        self.file_paths_list = []
        self.progress_value = 0

    def set_path(self, path: str) -> None:
        self._path_dict_folder = path
        return

    def update_KSGPW_dict(self) -> None:
        print('Dzieje się PW')
        return

    def update_KSFIN_dict(self) -> None:
        print('Dzieje się FIN')
        print(self._path_dict_folder)
        return

    def update_TRANS_dict(self) -> None:
        print('Dzieje się TRANS')
        return