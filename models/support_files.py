from .base import ObservableModel
import pandas


class SupportFiles(ObservableModel):
    def __init__(self):
        super().__init__()
        self.data_koi = None

    def load_data_from_file(self, file_path):
        """Load data from the file and assign it to the data attribute."""
        print(f'SupportFiles: load_data_from_file({file_path})')
        try:
            self.data_koi = pandas.read_csv(file_path)
            return True  # True when the load is successful.
        except Exception as e:
            print(f'SupportFiles: load_data_from_file() {e}')
            return False

    def get_data(self):
        return self.data_koi

    def funkcja_tworzaca_pliki_pomocnicze(self):
        # self.data_koi z teg korzystac
        pass