import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk
from PIL import Image, ImageTk

import paths


class StageView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # image background photo
        self.background_image = PhotoImage(file=paths.path_background_stage)
        resized_background_image = Image.open(paths.path_background_stage)
        self.background_image = ImageTk.PhotoImage(resized_background_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # image background plain color
        self.background_transparent_image = PhotoImage(file=paths.path_background_stage_settings)
        resized_background_transparent_image = Image.open(paths.path_background_stage_settings)
        self.background_transparent_image = ImageTk.PhotoImage(resized_background_transparent_image)
        self.background_image_label = ttk.Label(self, image=self.background_transparent_image)

        # btn back
        self.back_icon = PhotoImage(file=paths.path_back_icon)
        resized_back_icon = Image.open(paths.path_back_icon)
        self.back_icon = ImageTk.PhotoImage(resized_back_icon)

        self.back_btn = ttk.Button(self, image=self.back_icon)
        self.back_btn.place(x=30, y=15)

        # icons
        self.folder_icon = tk.PhotoImage(file=paths.path_folder_icon)
        self.add_folder_icon = tk.PhotoImage(file=paths.path_add_folder_icon)
        self.excel_icon = tk.PhotoImage(file=paths.path_excel_icon)
        self.gear_icon = tk.PhotoImage(file=paths.path_gear_icon)
        self.save_icon = tk.PhotoImage(file=paths.path_save_icon)
        self.popup_window = None

        # btn expand
        self.buttons_expanded = False
        self.expand_button = ttk.Button(self, text="   Ustawienia", command=self.toggle_buttons, image=self.gear_icon,
                                        compound="left")
        self.expand_button.place(x=450, y=60, width=140, height=40)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=210, mode="determinate")

        # btn generate support files and filedialog
        self.generate_support_files_btn = ttk.Button(self, text="Wygeneruj pliki pomocnicze")
        self.generate_support_files_btn.place(x=60, y=105, width=170, height=40)

        self.support_file_filedialog_btn = ttk.Button(self, image=self.folder_icon)
        self.support_file_filedialog_btn.place(x=235, y=105, width=40, height=40)

        # btn update dictionaries and filedialog
        self.update_dictionaries_btn = ttk.Button(self, text="Aktualizuj słowniki")
        self.update_dictionaries_btn.place(x=60, y=155, width=170, height=40)

        self.dictionaries_filedialog_btn = ttk.Button(self, image=self.folder_icon)
        self.dictionaries_filedialog_btn.place(x=235, y=155, width=40, height=40)

        # btn change save dictionaries filedialog
        self.save_dictionaries_btn = ttk.Button(self, text="   Zmień miejsce zapisu raportów", image=self.save_icon,
                                                compound="left")

        # btn choose folder filedialog
        self.choose_folder_btn = ttk.Button(self, text="   Wybierz pliki do raportów          ",
                                            image=self.add_folder_icon,
                                            compound="left")

        # btn summary report filedialog
        self.summary_report_btn = ttk.Button(self, text="   Podsumuj raport                            ",
                                             image=self.excel_icon, compound="left")

        self.report_load_btn = ttk.Button(self, text="Raporty Go4Load")
        self.report_load_btn.place(x=60, y=279, width=165, height=40)

        self.report_end_btn = ttk.Button(self, text="Raporty Go4EndOfDay")
        self.report_end_btn.place(x=60, y=329, width=165, height=40)

    def toggle_buttons(self):
        if not self.buttons_expanded:
            self.background_image_label.place(relwidth=1, relheight=1)
            self.save_dictionaries_btn.place(x=450, y=105, width=230, height=40)
            self.choose_folder_btn.place(x=450, y=155, width=230, height=40)
            self.summary_report_btn.place(x=450, y=205, width=230, height=40)

            self.expand_button.config(text="   Zwiń")
            self.buttons_expanded = True
        else:
            self.save_dictionaries_btn.place_forget()
            self.choose_folder_btn.place_forget()
            self.summary_report_btn.place_forget()
            self.background_image_label.place_forget()

            self.expand_button.config(text="   Ustawienia")
            self.buttons_expanded = False

    def show_popup_window(self, title: str, text: str) -> None:

        def on_close():
            nonlocal self
            self.popup_window.destroy()
            self.progress_bar.place_forget()

        self.popup_window = tk.Toplevel(self)
        self.popup_window.title(title)

        # Ustawienie wielkości okna
        width = 400
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
