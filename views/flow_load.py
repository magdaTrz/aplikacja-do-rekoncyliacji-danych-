import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk

import paths

button_data = [
    {"name": "koi_btn", "text": "Klienci i Instytucje", "y": 165},
    {"name": "umo_btn", "text": "Umowy", "y": 200},
    {"name": "ksgpw_btn", "text": "Księgowania PW", "y": 235},
    {"name": "ksgfin_btn", "text": "Ksiegowania Fin", "y": 270},
    {"name": "mate_btn", "text": "Baza Mate", "y": 305},
]


class FlowLoadView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.style = ttk.Style()

        self.background_image = PhotoImage(file=paths.path_background)
        resized_image = Image.open(paths.path_background)
        self.background_image = ImageTk.PhotoImage(resized_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        self.back_btn = Button(self, text="<-Cofnij")
        self.back_btn.place(x=20, y=20, width=100, height=30)

        self.header = Label(self, text="Wybierz przepływ:")
        self.header.place(x=60, y=100, width=165, height=40)

        self.header_filedialog = Label(self, text="Wybrano raport GoForLoad.\nWybierz przepływ.", anchor='nw',
                                       justify="left", wraplength=280)
        self.header_filedialog.place(x=295, y=100, width=300, height=50)

        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=295, y=155, width=300, height=180)
        font_spec = "Courier New", 8
        self.info_label.configure(font=font_spec)

        self.icon = tk.PhotoImage(file=paths.path_folder_icon)
        self.filedialog_btn = Button(self, image=self.icon)
        self.filedialog_btn.place(x=600, y=100, width=40, height=40)

        for i, data in enumerate(button_data):
            button = Button(self, text=data["text"])
            setattr(self, data["name"], button)
            button.place(x=60, y=data["y"], width=165, height=30)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=312, mode="determinate")
        self.progress_bar_info = Label(self, text='')

        self.start_btn = ttk.Button(self, text="Rekoncyliuj")



