import time

from base import ObservableModel
import pandas


class SupportFiles(ObservableModel):
    def __init__(self):
        super().__init__()
        self.data_koi = None
        self.progress_value = 0

    def load_data_from_file(self, file_path):
        """Load data from the file and assign it to the data attribute."""
        print(f'SupportFiles: load_data_from_file({file_path})')
        try:
            self.data_koi = pandas.read_csv(file_path)
            self.progress_value = 50
            self.create_support_file()
            return True  # True when the load is successful.
        except Exception as e:
            print(f'SupportFiles: load_data_from_file() {e}')
            return False

    def get_data(self):
        return self.data_koi

    def create_support_file(self):
        # self.data_koi z teg korzystac
        print(f'SupportFiles: load_data_from_file({self.data_koi})')
        print(f'Tutaj bedzie logika stojąca za tworzeniem plików.')
        time.sleep(5)
        self.progress_value = 100


