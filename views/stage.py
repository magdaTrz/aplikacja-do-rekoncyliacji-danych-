from tkinter import Frame, Label, Button, PhotoImage
# import customtkinter


class StageView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f'StageView: __init__()')

        self.grid_columnconfigure(0, weight=0)

        self.header = Label(self, text="Stage")
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.back_btn = Button(self, text="Cofnij")
        self.back_btn.grid(row=1, column=0, padx=10, pady=10)

        self.greeting = Label(self, text="")
        self.greeting.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.reportload_btn = Button(self, text="Raporty Go4Load")
        self.reportload_btn.grid(row=3, column=0, padx=10, pady=10)

        self.reportend_btn = Button(self, text="Raporty Go4EndOfDay")
        self.reportend_btn.grid(row=4, column=0, padx=10, pady=10)