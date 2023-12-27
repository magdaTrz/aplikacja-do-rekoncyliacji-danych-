from tkinter import Frame, Label, Button, PhotoImage
from tkinter import ttk

# import customtkinter


class StartView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f'StartView: __init__()')

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

        # self.header = Label(self, text="Sign In with existing account")
        # self.header.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # self.username_label = Label(self, text="MAgdaUsername")
        # self.username_input = Entry(self)
        # self.username_label.grid(row=1, column=0, padx=10, sticky="w")
        # self.username_input.grid(row=1, column=1, padx=(0, 20), sticky="ew")
        #
        # self.password_label = Label(self, text="Password")
        # self.password_input = Entry(self, show="*")
        # self.password_label.grid(row=2, column=0, padx=10, sticky="w")
        # self.password_input.grid(row=2, column=1, padx=(0, 20), sticky="ew")

        self.start_btn = Button(self, text="Start")
        self.start_btn.grid(row=3, column=1, padx=0, pady=10, sticky="w")

        self.signup_option_label = Label(self, text="Don't have an account?")
        self.signup_btn = Button(self, text="Sign Up")
        self.signup_option_label.grid(row=4, column=1, sticky="w")
        self.signup_btn.grid(row=5, column=1, sticky="w")
