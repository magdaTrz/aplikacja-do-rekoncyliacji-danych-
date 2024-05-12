import tkinter as tk
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext
from PIL import Image, ImageTk
from tkcalendar import Calendar
from text_variables import TextEnum

import paths

button_data = [
    {"name": f"{TextEnum.KOI}_btn", "text": "Klienci i Instytucje", "y": 165},
    {"name": f"{TextEnum.UMO}_btn", "text": "Umowy", "y": 200},
    {"name": f"{TextEnum.KSGPW}_btn", "text": "Księgowania PW", "y": 235},
    {"name": f"{TextEnum.KSGFIN}_btn", "text": "Ksiegowania Fin", "y": 270},
    {"name": f"{TextEnum.MATE}_btn", "text": "Baza Mate", "y": 305},
]


class FlowLoadView(Frame):
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
        self.where_save_reports_label = ttk.Label(self, text='', anchor='nw', justify="left", wraplength=280)
        self.where_save_reports_label.place(x=360, y=50, width=300, height=30)

        self.choose_dir_to_save_filedialog_btn = ttk.Button(self, image=self.save_icon)
        self.choose_dir_to_save_filedialog_btn.place(x=330, y=50, width=30, height=30)

        # btn from where files are
        self.data_folder_path_label = ttk.Label(self, text="", anchor='nw', justify="left", wraplength=280)
        self.data_folder_path_label.place(x=360, y=90, width=300, height=30)

        self.choose_dir_fromwhere_data_filedialog_btn = ttk.Button(self, image=self.folder_icon)
        self.choose_dir_fromwhere_data_filedialog_btn.place(x=330, y=90, width=30, height=30)

        # btn set password
        self.set_password_btn = ttk.Button(self, image=self.lock_icon)
        self.set_password_btn.place(x=627, y=140, width=40, height=40)
        self.password_window_open = False
        self.window_password = None
        self.password_received_callback = None

        # btn set migration date
        self.set_migration_date_btn = ttk.Button(self, image=self.calendar_icon)
        self.set_migration_date_btn.place(x=627, y=188, width=40, height=40)
        self.calendar_window_open = False
        self.window_calendar = None
        self.calendar_received_callback = None

        # ScrolledText
        self.info_label = scrolledtext.ScrolledText(self)
        self.info_label.place(x=330, y=140, width=280, height=280)
        font_spec = "Courier New", 8
        self.info_label.configure(font=font_spec)
        self.info_label.insert(tk.END, "Wybierz dla którego przepływu chcecsz wykonać raport Go4Load.\n")

        for i, data in enumerate(button_data):
            button = ttk.Button(self, text=data["text"])
            setattr(self, data["name"], button)
            button.place(x=60, y=data["y"], width=165, height=30)

        # btn reconcile
        self.start_btn = ttk.Button(self, text="  Rekoncyliuj ", image=self.gear_icon,
                                    compound="left")

        # insurance yes/no
        self.check_icon = tk.PhotoImage(file=paths.path_check_icon)
        self.xmark_icon = tk.PhotoImage(file=paths.path_xmark_icon)

        self.check_btn = ttk.Button(self, image=self.check_icon)
        self.xmark_btn = ttk.Button(self, image=self.xmark_icon)

    def show_set_password_window(self, callback):
        self.password_received_callback = callback

        def set_password():
            password = password_entry.get()
            on_close()
            self.password_received_callback(password)

        def on_close():
            nonlocal self
            self.password_window_open = False
            self.window_password.destroy()

        if not self.password_window_open:
            self.password_window_open = True
            self.window_password = tk.Toplevel(self)
            self.window_password.title("Ustaw hasło na raportach")

            # Ustawienie wielkości okna
            width = 400
            height = 250
            x = (self.winfo_screenwidth() - width) // 2
            y = (self.winfo_screenheight() - height) // 2
            self.window_password.geometry('{}x{}+{}+{}'.format(width, height, x, y))

            # Ustawienie okna na środku okna rodzica
            self.update_idletasks()
            window_password_x = self.winfo_rootx() + (self.winfo_width() - width) // 2
            window_password_y = self.winfo_rooty() + (self.winfo_height() - height) // 2
            self.window_password.geometry('+{}+{}'.format(window_password_x, window_password_y))

            label = ttk.Label(self.window_password, text='Podaj hasło którym chcesz zabezpieczyć raporty')
            label.place(x=65, y=20, width=270, height=30)

            password_entry = ttk.Entry(self.window_password, show='*')
            password_entry.place(x=65, y=47, width=270, height=30)

            accept_passwort_btn = ttk.Button(self.window_password, text="Zatwierdż", command=set_password,
                                             image=self.check_icon, compound="left")
            accept_passwort_btn.place(x=85, y=100, width=110, height=30)

            cancel_password_btn = ttk.Button(self.window_password, text="Anuluj", command=on_close,
                                             image=self.xmark_icon, compound="left")
            cancel_password_btn.place(x=204, y=100, width=110, height=30)

            self.window_password.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.window_password.focus()

    def show_calendar_window(self, callback):
        self.calendar_received_callback = callback

        def set_date():
            migration_date = calendar_widget.get_date()
            self.calendar_received_callback(migration_date)
            on_close()

        def on_close():
            nonlocal self
            self.calendar_window_open = False
            self.window_calendar.destroy()

        if not self.calendar_window_open:
            self.calendar_window_open = True
            self.window_calendar = tk.Toplevel(self)
            self.window_calendar.title("Ustaw datę migracji")

            # Ustawienie wielkości okna
            width = 500
            height = 480
            x = (self.winfo_screenwidth() - width) // 2
            y = (self.winfo_screenheight() - height) // 2
            self.window_calendar.geometry('{}x{}+{}+{}'.format(width, height, x, y))

            # Ustawienie okna na środku okna rodzica
            self.update_idletasks()
            window_calendar_x = self.winfo_rootx() + (self.winfo_width() - width) // 2
            window_calendar_y = self.winfo_rooty() + (self.winfo_height() - height) // 2
            self.window_calendar.geometry('+{}+{}'.format(window_calendar_x, window_calendar_y))

            label = ttk.Label(self.window_calendar, text='Wybierz datę migracji')
            label.place(x=100, y=20, width=300, height=30)

            calendar_widget = Calendar(self.window_calendar, selectmode='day')
            calendar_widget.place(x=100, y=60, width=300, height=300)

            accept_calendar_btn = ttk.Button(self.window_calendar, text="Zatwierdż", command=set_date,
                                             image=self.check_icon, compound="left")
            accept_calendar_btn.place(x=135, y=388, width=110, height=30)

            cancel_calendar_btn = ttk.Button(self.window_calendar, text="Anuluj", command=on_close,
                                             image=self.xmark_icon, compound="left")
            cancel_calendar_btn.place(x=255, y=388, width=110, height=30)

            self.window_calendar.protocol("WM_DELETE_WINDOW", on_close)
        else:
            self.window_calendar.focus()
