from tkinter import Frame, Label, Button, PhotoImage
from tkinter import ttk

# import customtkinter


class StartView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        # Load the background image
        self.background_image = PhotoImage(file=r"C:\Users\48505\PycharmProjects\tkinter-multiframe-mvc\red3.png")
        self.background_image = self.background_image.subsample(int(self.background_image.width() / 720),
                                                                int(self.background_image.height() / 480))

        # Create a label to display the background image
        self.background_label = Label(self, image=self.background_image)
        # self.background_label = customtkinter.CTkLabel(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        self.start_btn = Button(self, text="Start")
        self.start_btn.grid(row=3, column=1, padx=0, pady=10, sticky="w")

        self.signup_option_label = Label(self, text="Don't have an account?")
        self.signup_btn = Button(self, text="Sign Up")
        self.signup_option_label.grid(row=4, column=1, sticky="w")
        self.signup_btn.grid(row=5, column=1, sticky="w")
