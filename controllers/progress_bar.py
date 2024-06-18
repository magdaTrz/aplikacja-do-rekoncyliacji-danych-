class ProgresBarStatus:
    progressbar_var = None

    @classmethod
    def increase(cls):
        try:
            new_value = cls.progressbar_var.get() + 1
            cls.progressbar_var.set(new_value)
        except Exception as e:
            print(f'Error ProgresBarStatus: {e}')

    @classmethod
    def clear(cls):
        cls.progressbar_var = 0

    @classmethod
    def update_progress_info(cls, *args):
        cls.progressbar_var.get()

    @classmethod
    def set_80_percent(cls):
        cls.progressbar_var.set(80)

    @classmethod
    def set_1_percent(cls):
        cls.progressbar_var.set(1)

    @classmethod
    def set_100_percent(cls):
        cls.progressbar_var.set(100)
