from tkinter import Frame, Label, Button, PhotoImage, ttk


class StageView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=0)

        self.back_btn = Button(self, text="Cofnij")
        self.back_btn.grid(row=0, column=0, padx=10, pady=10)

        self.greeting = Label(self, text="")
        self.greeting.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.supportfile_btn = Button(self, text="Wygeneruj pliki pomocnicze")
        self.supportfile_btn.grid(row=2, column=0, padx=10, pady=10)

        self.supportfile_filedialog_btn = Button(self, text="fileDialog")
        self.supportfile_filedialog_btn.grid(row=2, column=1, padx=10, pady=10)

        self.supportfile_filedialog_label = Label(self, text="")
        self.supportfile_filedialog_label.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")

        self.header = Label(self, text="Wybierz etap:")
        self.header.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.reportload_btn = Button(self, text="Raporty Go4Load")
        self.reportload_btn.grid(row=5, column=0, padx=10, pady=10)

        self.reportend_btn = Button(self, text="Raporty Go4EndOfDay")
        self.reportend_btn.grid(row=6, column=0, padx=10, pady=10)