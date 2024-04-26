import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk

import paths
from controllers.progress_bar import ProgresBarStatus


class ReportView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_image = PhotoImage(file=paths.path_background_start)
        resized_image = Image.open(paths.path_background_start)

        self.background_image = ImageTk.PhotoImage(resized_image)
        self.background_label = tk.Label(self, image=self.background_image)

        self.background_label.place(relwidth=1, relheight=1)
        self.back_btn = Button(self, text="<-Cofnij")

        self.back_btn.place(x=20, y=20, width=100, height=30)
        ProgresBarStatus.progressbar_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=312,
                                            mode="determinate",
                                            variable=ProgresBarStatus.progressbar_var,
                                            style="TProgressbar")
        self.progress_bar.place(x=60, y=65)
        ProgresBarStatus.progressbar_var.trace_add("write", ProgresBarStatus.update_progress_info)

        self.progress_bar_info = Label(self, text='')

        self.progress_bar_info.place(x=32, y=65, width=25, height=22)

        self.loading_label = ttk.Progressbar(self, orient="horizontal", length=50, mode='indeterminate')
        self.loading_label.place(x=394, y=65)

        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=40, y=100, width=640, height=260)
        font_spec = "Courier New", 8

        self.info_label.configure(font=font_spec)
