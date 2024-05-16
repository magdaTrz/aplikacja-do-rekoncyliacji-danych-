import tkinter as tk
import tkinter.messagebox
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext

import pandas
from PIL import Image, ImageTk

import paths
from controllers.progress_bar import ProgresBarStatus


class SummaryView(Frame):
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

        self.treeview_frame = tk.LabelFrame(self, text="Podsumowanie")
        self.treeview_frame.place(x=70, y=75, height=280, width=570)

        self.treeview_widget = ttk.Treeview(self.treeview_frame)
        self.treeview_widget.place(relheight=1, relwidth=1)

        treescrolly = tk.Scrollbar(self.treeview_frame, orient="vertical", command=self.treeview_widget.yview)
        treescrollx = tk.Scrollbar(self.treeview_frame, orient="horizontal", command=self.treeview_widget.xview)
        self.treeview_widget.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")

    def display_dataframe(self, dataframe):
        def clear_data():
            self.treeview_widget.delete(*self.treeview_widget.get_children())
            return None

        if not dataframe.empty:
            clear_data()
            self.treeview_widget["column"] = list(dataframe.columns)
            self.treeview_widget["show"] = "headings"

            for column in self.treeview_widget["columns"]:
                self.treeview_widget.heading(column, text=column)
            df_rows = dataframe.to_numpy().tolist()
            for row in df_rows:
                self.treeview_widget.insert("", "end", values=row)
            return None
        else:
            tkinter.messagebox.showerror("Informacja","Brak danych do wyświetlenia.")
            print(f'ERROR: Brak danych do wyświetlenia')
            return None

    def show_popup_window(self, title: str, text: str) -> None:

        def on_close():
            nonlocal self
            self.popup_window.destroy()

        self.popup_window = tk.Toplevel(self)
        self.popup_window.title(title)

        # Ustawienie wielkości okna
        width = 200
        height = 200
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.popup_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        # Ustawienie okna na środku okna rodzica
        self.update_idletasks()
        window_x = self.winfo_rootx() + (self.winfo_width() - width) // 2
        window_y = self.winfo_rooty() + (self.winfo_height() - height) // 2
        self.popup_window.geometry('+{}+{}'.format(window_x, window_y))

        # Dodanie etykiety z komunikatem
        label = ttk.Label(self.popup_window, text=text, wraplength=350)
        label.pack(pady=20, padx=20)

        self.popup_window.protocol("WM_DELETE_WINDOW", on_close)