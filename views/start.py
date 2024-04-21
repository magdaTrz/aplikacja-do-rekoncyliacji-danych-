import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, font, ttk
from PIL import Image, ImageTk

import paths


class StartView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # image background plain color
        self.background_color_image = PhotoImage(file=paths.path_background_color)
        resized_background_color_image = Image.open(paths.path_background_color)
        self.background_color_image = ImageTk.PhotoImage(resized_background_color_image)

        self.background_image_label = tk.Label(self, image=self.background_color_image)
        self.background_image_label.place(x=0, y=0, width=345, height=480)

        # image right background photo
        self.background_image = PhotoImage(file=paths.path_background)
        resized_background_image = Image.open(paths.path_background)
        self.background_image = ImageTk.PhotoImage(resized_background_image)

        self.background_image_label = tk.Label(self, image=self.background_image)
        self.background_image_label.place(x=345, y=0, width=375, height=480)

        # image welcome text
        self.background_text_image = PhotoImage(file=paths.path_start_text)
        resized_background_text_image = Image.open(paths.path_start_text)
        self.background_text_image = ImageTk.PhotoImage(resized_background_text_image)

        self.background_label = tk.Label(self, image=self.background_text_image)
        self.background_label.place(x=0, y=70, width=346, height=100)

        # btn Start
        self.start_btn = ttk.Button(self, text="Zaczynamy ->", style='Custom.TButton')
        self.start_btn.place(x=70, y=190, width=140, height=50)

        # image company
        photo_acn = ImageTk.PhotoImage(Image.open(paths.path_acn))
        photo_sbm = ImageTk.PhotoImage(Image.open(paths.path_sbm))

        self.label_acn = ttk.Label(self, image=photo_acn)
        self.label_acn.image = photo_acn
        self.label_sbm = ttk.Label(self, image=photo_sbm)
        self.label_sbm.image = photo_sbm
        self.label_acn.place(x=30, y=330, width=130, height=105)
        self.label_sbm.place(x=170, y=330, width=130, height=105)

        # btn help
        self.help_image = PhotoImage(file=paths.path_help_icon)
        resized_help_icon = Image.open(paths.path_help_icon)
        self.help_image = ImageTk.PhotoImage(resized_help_icon)

        self.help_btn = ttk.Button(self, image=self.help_image, command=self.show_instructions)
        self.help_btn.place(x=300, y=440, width=40, height=40)
        self.instruction_window_open = False
        self.window_instructions = None

        # top window instructions
    def show_instructions(self):
        if not self.instruction_window_open:
            self.instruction_window_open = True
            self.window_instructions = tk.Toplevel(self)
            self.window_instructions.title("Instrukcja")

            def on_close():
                nonlocal self
                self.instruction_window_open = False
                self.window_instructions.destroy()

            instructions_text = """
            Tutaj wpisz instrukcję, która ma się pojawić.
            Możesz dostosować jej wygląd i zawartość do własnych potrzeb.
            """
            label_instructions = Label(self.window_instructions, text=instructions_text)
            label_instructions.pack(padx=10, pady=10)

            self.window_instructions.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.window_instructions.focus()
