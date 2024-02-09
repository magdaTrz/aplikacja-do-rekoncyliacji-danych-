import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk

import paths


class FlowEndView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=0)

        self.back_btn = Button(self, text="Cofnij")
        self.back_btn.grid(row=1, column=0, padx=10, pady=10)

        self.greeting = Label(self, text="Raport EndOfDay")
        self.greeting.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.header = Label(self, text="Wybierz przepływ:")
        self.header.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.filedialog_ext_btn = Button(self, text='')
        self.filedialog_ext_btn.grid(row=4, column=1, padx=1, pady=1, sticky="ew")
        self.filedialog_tgt_btn = Button(self, text='')
        self.filedialog_tgt_btn.grid(row=5, column=1, padx=1, pady=1, sticky="ew")

        # for i, data in enumerate(button_data):
        #     button = Button(self, text=data["text"])
        #     setattr(self, data["name"], button)
        #     button.grid(row=i + 4, column=0, padx=10, pady=10)