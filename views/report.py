import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk

import paths


class ReportView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_image = PhotoImage(file=paths.path_background)
        resized_image = Image.open(paths.path_background)
        self.background_image = ImageTk.PhotoImage(resized_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        self.back_btn = Button(self, text="<-Cofnij")
        self.back_btn.place(x=20, y=20, width=100, height=30)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=312, mode="determinate")

        self.progress_bar_info = Label(self, text='')

        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=40, y=100, width=640, height=260)
        font_spec = "Courier New", 8
        self.info_label.configure(font=font_spec)
