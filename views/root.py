from tkinter import Tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import customtkinter


class Root(Tk):
    def __init__(self):
        super().__init__()

        start_width = 720
        min_width = start_width - 10
        start_height = 480
        min_height = start_height - 10

        customtkinter.set_appearance_mode('dark')
        customtkinter.set_default_color_theme('dark-blue')
        self.geometry(f"{start_width}x{start_height}")
        self.minsize(width=min_width, height=min_height)
        self.title("Konsola Rekoncyliacji")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        style = ttk.Style()

        font_name = "Bahnschrift"
        font_size = 12
        style.configure("TButton", font=(font_name, font_size))
        style.map("TButton",
                  foreground=[('active', 'red'), ('!active', 'black')])
