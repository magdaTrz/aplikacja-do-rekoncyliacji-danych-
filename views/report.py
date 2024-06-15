import tkinter
from tkinter import Frame, Label, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk
from datetime import datetime
from pydispatch import dispatcher

import paths
from controllers.progress_bar import ProgresBarStatus


class ReportView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Connect the signal receiver
        dispatcher.connect(self.append_text, signal='update_text')

        # image background photo
        self.background_image = PhotoImage(file=paths.path_background_report)
        resized_background_image = Image.open(paths.path_background_report)
        self.background_image = ImageTk.PhotoImage(resized_background_image)

        self.background_label = tkinter.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # btn back
        self.back_icon = PhotoImage(file=paths.path_back_icon)
        resized_back_icon = Image.open(paths.path_back_icon)
        self.back_icon = ImageTk.PhotoImage(resized_back_icon)

        self.back_btn = ttk.Button(self, image=self.back_icon)
        self.back_btn.place(x=30, y=15)

        # progressbar
        ProgresBarStatus.progressbar_var = tkinter.DoubleVar()
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

        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=40, y=100, width=640, height=260)
        font_spec = "Courier New", 8
        self.info_label.configure(font=font_spec)

        # icons
        self.loupe_icon = tkinter.PhotoImage(file=paths.path_loupe_icon)
        self.statistic_icon = tkinter.PhotoImage(file=paths.path_statistic_icon)
        self.open_folder_icon = tkinter.PhotoImage(file=paths.path_open_folder_icon)

        # btn open folder
        self.open_folder_btn = ttk.Button(self, text="   Otwórz", image=self.open_folder_icon, compound="left")

        # btn view summary
        self.summary_btn = ttk.Button(self, text="   Podsumowanie", image=self.statistic_icon, compound="left")

        # btn view details
        self.details_btn = ttk.Button(self, text="   Szczegóły", image=self.loupe_icon, compound="left")

    def append_text(self, message: str, head: str) -> None:
        def get_timestamp():
            now = datetime.now()
            formatted_timestamp = now.strftime("%H:%M:%S")
            return formatted_timestamp

        timestamp = get_timestamp()
        formatted_message = f"{timestamp} - [{head.upper()}] {message}"
        self.info_label.insert(tkinter.END, formatted_message + '\n')
        self.info_label.see(tkinter.END)
