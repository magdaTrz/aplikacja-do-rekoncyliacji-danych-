from tkinter import Frame, Label, Button
# import customtkinter

# Lista nazw i tekstów przycisków
button_data = [
    {"name": "koi_btn", "text": "Klienci i Instytucje"},
    {"name": "umo_btn", "text": "Umowy"},
    {"name": "ksgpw_btn", "text": "Księgowania PW"},
    {"name": "ksgfin_btn", "text": "Ksiegowania Fin"},
    {"name": "umo_btn", "text": "Umowy"},
]


class FlowView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f'FlowView: __init__()')

        self.grid_columnconfigure(0, weight=0)

        self.header = Label(self, text="Flow")
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.back_btn = Button(self, text="Cofnij")
        self.back_btn.grid(row=1, column=0, padx=10, pady=10)

        self.greeting = Label(self, text="")
        self.greeting.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        for data in button_data:
            button = Button(self, text=data["text"])
            setattr(self, data["name"], button)
            button.grid(row=len(button_data) + 2, column=0, padx=10, pady=10)

