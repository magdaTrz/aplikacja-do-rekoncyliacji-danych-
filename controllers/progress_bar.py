class ProgresBarStatus:
    progressbar_var = None

    @classmethod
    def increase(cls):
        new_value = cls.progressbar_var.get() + 1
        cls.progressbar_var.set(new_value)

    @classmethod
    def clear(cls):
        cls.progressbar_var = 0

    @classmethod
    def update_progress_info(cls, *args):
        cls.progressbar_var.get()
