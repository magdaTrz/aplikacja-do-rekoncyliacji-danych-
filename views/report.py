import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk

import paths
from controllers.progress_bar import ProgresBarStatus


class ReportView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # image background photo
        self.background_image = PhotoImage(file=paths.path_background_report)
        resized_background_image = Image.open(paths.path_background_report)
        self.background_image = ImageTk.PhotoImage(resized_background_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # btn back
        self.back_icon = PhotoImage(file=paths.path_back_icon)
        resized_back_icon = Image.open(paths.path_back_icon)
        self.back_icon = ImageTk.PhotoImage(resized_back_icon)

        self.back_btn = ttk.Button(self, image=self.back_icon)
        self.back_btn.place(x=30, y=15)

        # progresbar
        ProgresBarStatus.progressbar_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self, orient="horizontal",
                                            length=312,
                                            mode="determinate",
                                            variable=ProgresBarStatus.progressbar_var,
                                            style="TProgressbar")
        self.progress_bar.place(x=70, y=72)
        ProgresBarStatus.progressbar_var.trace_add("write", ProgresBarStatus.update_progress_info)

        # label x/x
        self.progress_bar_info = Label(self, text='')
        self.progress_bar_info.place(x=40, y=72, width=24, height=21)

        # self.loading_label = ttk.Progressbar(self, orient="horizontal", length=50, mode='indeterminate')
        # self.loading_label.place(x=394, y=65)

        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=40, y=100, width=640, height=260)
        font_spec = "Courier New", 8
        self.info_label.configure(font=font_spec)

        # icons
        self.loupe_icon = tk.PhotoImage(file=paths.path_loupe_icon)
        self.statistic_icon = tk.PhotoImage(file=paths.path_statistic_icon)
        self.open_folder_icon = tk.PhotoImage(file=paths.path_open_folder_icon)

        # btn open folder
        self.open_folder_btn = ttk.Button(self, text="   Otwórz", image=self.open_folder_icon, compound="left")

        # btn view summary
        self.summary_btn = ttk.Button(self, text="   Podsumowanie", image=self.statistic_icon, compound="left")

        # btn view details
        self.details_btn = ttk.Button(self, text="   Szczegóły", image=self.loupe_icon, compound="left")
