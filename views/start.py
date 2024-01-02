import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, font, ttk
from PIL import Image, ImageTk

import paths

# import customtkinter


class StartView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.background_image = PhotoImage(file=paths.path_background)
        resized_image = Image.open(paths.path_background)
        self.background_image = ImageTk.PhotoImage(resized_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        start_font = font.Font(family='Bahnschrift SemiBold', size=16)
        self.start_btn = ttk.Button(self, text="Start")
        self.start_btn.place(x=80, y=100, width=150, height=40)

        photo_acn = ImageTk.PhotoImage(Image.open(paths.path_acn))
        photo_sbm = ImageTk.PhotoImage(Image.open(paths.path_sbm))

        self.label_acn = ttk.Label(self, image=photo_acn)
        self.label_acn.image = photo_acn
        self.label_sbm = ttk.Label(self, image=photo_sbm)
        self.label_sbm.image = photo_sbm
        self.label_acn.place(x=20, y=260, width=210, height=180)
        self.label_sbm.place(x=240, y=260, width=210, height=180)
