import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk
from PIL import Image, ImageTk

import paths


class StageView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background_image = PhotoImage(file=paths.path_background)
        resized_image = Image.open(paths.path_background)
        self.background_image = ImageTk.PhotoImage(resized_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        self.back_btn = Button(self, text="<-Cofnij")
        self.back_btn.place(x=20, y=20, width=100, height=30)

        self.icon = tk.PhotoImage(file=paths.path_folder_icon)

        self.supportfile_btn = Button(self, text="Wygeneruj pliki pomocnicze")
        self.supportfile_btn.place(x=60, y=105, width=165, height=40)

        self.supportfile_filedialog_btn = Button(self, image=self.icon)
        self.supportfile_filedialog_btn.place(x=230, y=105, width=40, height=40)

        self.supportfile_filedialog_label = Label(self, text="", anchor='nw', padx=10, pady=10)
        self.supportfile_filedialog_label.place(x=275, y=105, width=385, height=90)

        self.dict_btn = Button(self, text="Aktualizuj słowniki")
        self.dict_btn.place(x=60, y=155, width=165, height=40)

        self.dict_filedialog_btn = Button(self, image=self.icon)
        self.dict_filedialog_btn.place(x=230, y=155, width=40, height=40)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=385, mode="determinate")

        self.header = Label(self, text="Wybierz etap:")
        self.header.place(x=250, y=255, width=200, height=40)

        self.reportload_btn = Button(self, text="Raporty Go4Load")
        self.reportload_btn.place(x=267, y=326, width=165, height=40)

        self.reportend_btn = Button(self, text="Raporty Go4EndOfDay")
        self.reportend_btn.place(x=267, y=372, width=165, height=40)
