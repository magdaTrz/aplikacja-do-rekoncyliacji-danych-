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


class FlowEndView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # icons
        self.folder_icon = tk.PhotoImage(file=paths.path_folder_icon)
        self.add_folder_icon = tk.PhotoImage(file=paths.path_add_folder_icon)
        self.save_icon = tk.PhotoImage(file=paths.path_save_icon)
        self.gear_icon = tk.PhotoImage(file=paths.path_gear_icon)
        self.lock_icon = tk.PhotoImage(file=paths.path_lock_icon)
        self.calendar_icon = tk.PhotoImage(file=paths.path_calendar_icon)

        # image background photo
        self.background_flow_image = PhotoImage(file=paths.path_background_flow)
        resized_background_flow_image = Image.open(paths.path_background_flow)
        self.background_flow_image = ImageTk.PhotoImage(resized_background_flow_image)

        self.background_label = tk.Label(self, image=self.background_flow_image)
        self.background_label.place(relwidth=1, relheight=1)

        # btn back
        self.back_icon = PhotoImage(file=paths.path_back_icon)
        resized_back_icon = Image.open(paths.path_back_icon)
        self.back_icon = ImageTk.PhotoImage(resized_back_icon)

        self.back_btn = ttk.Button(self, image=self.back_icon)
        self.back_btn.place(x=30, y=15)

        # btn where_save_reports_label
        self.where_save_reports_label = ttk.Label(self,
                                                  text=fr"C:\Users\48505\AppData\Local\Programs\Python\Python310\python.exe C:\Users\48505\PycharmProjects\tkinter-multiframe-mvc\main.py",
                                                  anchor='nw',
                                                  justify="left", wraplength=280)
        self.where_save_reports_label.place(x=360, y=50, width=300, height=30)

        self.choose_dir_to_save_filedialog_btn = ttk.Button(self, image=self.save_icon)
        self.choose_dir_to_save_filedialog_btn.place(x=330, y=50, width=30, height=30)

        # btn from where files are
        self.header_filedialog = ttk.Label(self, text="Wybrano raport GoForLoad.\nWybierz przepływ.", anchor='nw',
                                           justify="left", wraplength=280)
        self.header_filedialog.place(x=360, y=90, width=300, height=30)

        self.filedialog_btn = ttk.Button(self, image=self.folder_icon)
        self.filedialog_btn.place(x=330, y=90, width=30, height=30)

        # btn set password
        self.set_password_btn = ttk.Button(self, image=self.lock_icon)
        self.set_password_btn.place(x=627, y=140, width=40, height=40)

        # btn set migration date
        self.set_migration_date_btn = ttk.Button(self, image=self.calendar_icon)
        self.set_migration_date_btn.place(x=627, y=188, width=40, height=40)

        # ScrolledText
        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=330, y=140, width=280, height=280)
        font_spec = "Courier New", 8
        self.info_label.configure(font=font_spec)
        self.info_label.insert(tk.END, "Wybierz dla którego przepływu chcecsz wykonać raport Go4EndOfDay.\n")

        for i, data in enumerate(button_data):
            button = ttk.Button(self, text=data["text"])
            setattr(self, data["name"], button)
            button.place(x=60, y=data["y"], width=165, height=30)

        self.start_btn = ttk.Button(self, text="  Rekoncyliuj ", image=self.gear_icon,
                                    compound="left")