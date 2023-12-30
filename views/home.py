from tkinter import Frame, Label, Button, PhotoImage


class HomeView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load the background image
        # self.background_image = PhotoImage(file=r"C:\Users\48505\PycharmProjects\tkinter-multiframe-mvc\red2.png")

        # Create a label to display the background image
        # self.background_label = Label(self, image=self.background_image)
        # self.background_label.place(relwidth=1, relheight=1)

        self.grid_columnconfigure(0, weight=1)

        self.header = Label(self, text="Home")
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.greeting = Label(self, text="")
        self.greeting.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.reportload_btn = Button(self, text="Raporty Go4Load")
        self.reportload_btn.grid(row=2, column=0, padx=10, pady=10)

        self.reportend_btn = Button(self, text="Raporty Go4EndOfDay")
        self.reportend_btn.grid(row=3, column=0, padx=10, pady=10)
