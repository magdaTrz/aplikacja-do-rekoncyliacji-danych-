from tkinter import Tk
# import customtkinter


class Root(Tk):
    def __init__(self):
        super().__init__()

        start_width = 720
        min_width = start_width - 10
        start_height = 480
        min_height = start_height - 10

        # customtkinter.set_appearance_mode('System')
        # customtkinter.set_default_color_theme('blue')
        self.geometry(f"{start_width}x{start_height}")
        self.minsize(width=min_width, height=min_height)
        self.title("Konsola Rekoncyliacji")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
