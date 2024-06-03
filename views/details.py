import tkinter as tk
import tkinter.messagebox
from tkinter import Frame, Label, Button, PhotoImage, ttk, scrolledtext

import pandas
from PIL import Image, ImageTk

import paths
from controllers.progress_bar import ProgresBarStatus


class DetailsView(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        style_btn = ttk.Style()
        style_btn.configure("Red.TButton", background="#9E3B28", foreground="#9E3B28")
        style_btn.map("Red.TButton", background=[("pressed", "#9E3B28")], foreground=[("pressed", "#9E3B28")])

        style = ttk.Style()
        style.configure("Treeview", foreground="black", rowheight=25, font=("Courier New", 8))
        # style heading
        style.configure("Treeview.Heading", font=("Courier New", 8, 'bold'))
        style.map("Treeview", background=[('selected', '#9E3B28')], foreground=[('selected', 'white')])

        # image background photo
        self.background_image = PhotoImage(file=paths.path_background_details)
        resized_background_image = Image.open(paths.path_background_details)
        self.background_image = ImageTk.PhotoImage(resized_background_image)

        self.background_label = tk.Label(self, image=self.background_image)
        self.background_label.place(relwidth=1, relheight=1)

        # btn back
        self.back_icon = PhotoImage(file=paths.path_back_icon)
        resized_back_icon = Image.open(paths.path_back_icon)
        self.back_icon = ImageTk.PhotoImage(resized_back_icon)

        self.back_btn = ttk.Button(self, image=self.back_icon)
        self.back_btn.place(x=30, y=15)

        # icons
        self.chart_icon = tk.PhotoImage(file=paths.path_chart_icon)
        self.group_icon = tk.PhotoImage(file=paths.path_group_icon)
        self.table_icon = tk.PhotoImage(file=paths.path_table_icon)
        self.open_folder_icon = tk.PhotoImage(file=paths.path_open_folder_icon)

        # btn show true false statistic
        self.show_true_false_statistic_btn = ttk.Button(self, image=self.chart_icon, text='true_false')
        self.show_true_false_statistic_btn.place(x=200, y=95, width=40, height=40)

        # btn show merge statistic
        self.show_merge_statistic_btn = ttk.Button(self, image=self.group_icon, text='merge')
        self.show_merge_statistic_btn.place(x=200, y=141, width=40, height=40)

        # btn show data
        self.show_data_btn = ttk.Button(self, image=self.table_icon, text='data')
        self.show_data_btn.place(x=200, y=187, width=40, height=40)

        # display data widget
        self.treeview_frame = tk.LabelFrame(self, text="Podsumowanie")
        self.treeview_frame.place(x=270, y=64, width=435, height=353)

        self.treeview_widget = ttk.Treeview(self.treeview_frame)
        self.treeview_widget.place(relheight=1, relwidth=1)

        treescrolly = tk.Scrollbar(self.treeview_frame, orient="vertical", command=self.treeview_widget.yview)
        treescrollx = tk.Scrollbar(self.treeview_frame, orient="horizontal", command=self.treeview_widget.xview)
        self.treeview_widget.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrollx.pack(side="bottom", fill="x")
        treescrolly.pack(side="right", fill="y")

        self.open_file_btn = ttk.Button(self, text="    Otwórz cały raport", image=self.open_folder_icon,
                                        compound="left")

        self.selected_btn = None
        self.selected_right_btn = None
        self.buttons = []
        self.right_buttons = [self.show_true_false_statistic_btn, self.show_merge_statistic_btn, self.show_data_btn]

    def create_buttons(self, name_dict):
        print('DetailsView: create_buttons()')
        self.buttons = []
        x = 50
        y = 95
        button_width = 140
        button_height = 30
        button_spacing = 8

        for name in name_dict:
            button = ttk.Button(self, text=name, command=lambda n=name: self.set_btn_name(n))
            button.place(x=x, y=y, width=button_width, height=button_height)
            self.buttons.append(button)
            y += button_height + button_spacing

    def display_dataframe(self, dataframe: pandas.DataFrame) -> None:
        print(f'DetailsView: display_dataframe({dataframe})')
        if not dataframe.empty:
            self.clear_data()
            self.treeview_widget["column"] = list(dataframe.columns)
            self.treeview_widget["show"] = "headings"

            for column in self.treeview_widget["columns"]:
                self.treeview_widget.heading(column, text=column)
                max_len = max(dataframe[column].astype(str).apply(len).max(), len(column))
                width = max_len * 10
                max_width = 500
                if width > max_width:
                    width = max_width
                self.treeview_widget.column(column, width=width)
            df_rows = dataframe.to_numpy().tolist()
            for row in df_rows:
                self.treeview_widget.insert("", "end", values=row)
            return None
        else:
            tkinter.messagebox.showerror("Informacja", "Brak danych do wyświetlenia.")
            print(f'ERROR: Brak danych do wyświetlenia')
            return None

    def clear_data(self):
        self.treeview_widget.delete(*self.treeview_widget.get_children())
        return None

    def set_btn_name(self, name: str) -> None:
        print(f'DetailsView: set_btn_name({name})')
        self.selected_btn = name
        self.reset_button_styles()
        self.highlight_selected_button(name)

    def reset_button_styles(self):
        for button in self.buttons:
            button.config(style='TButton')  # Reset to default style
        for button in self.right_buttons:
            button.config(style='TButton')
        self.open_file_btn.place_forget()
        self.clear_data()

    def highlight_selected_button(self, name):
        for button in self.buttons:
            if button.cget('text') == name:
                button.config(style='Red.TButton')

    def select_right_button(self, button_type):
        self.selected_right_btn = button_type
        self.reset_right_button_styles()
        self.highlight_selected_right_button(button_type)
        print(f"Right button clicked: {button_type}")

    def reset_right_button_styles(self):
        for button in self.right_buttons:
            button.config(style='TButton')  # Reset to default style
        self.open_file_btn.place_forget()
        self.clear_data()

    def highlight_selected_right_button(self, button_type):
        for button in self.right_buttons:
            if button.cget('text').lower() == button_type:
                button.config(style='Red.TButton')  # Set selected style
