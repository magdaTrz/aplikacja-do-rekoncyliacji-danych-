import os.path
import tkinter as tk

from models.main import Model
from tkinter import filedialog, ttk
from views.main import View
from paths import flow_paths
from text_variables import TextEnum


class FlowLoadController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.frame = self.view.frames["flow_load"]
        self._bind()

    def _bind(self) -> None:
        """Binds controller functions with respective buttons in the view"""
        self.frame.back_btn.config(command=self.handle_back)
        self.frame.KOI_btn.config(command=lambda: self.handle_selected_flow(flow=TextEnum.KOI))
        self.frame.UMO_btn.config(command=lambda: self.handle_selected_flow(flow=TextEnum.UMO))
        self.frame.KSGPW_btn.config(command=lambda: self.handle_selected_flow(flow=TextEnum.KSGPW))
        self.frame.KSGFIN_btn.config(command=lambda: self.handle_selected_flow(flow=TextEnum.KSGFIN))
        self.frame.MATE_btn.config(command=lambda: self.handle_selected_flow(flow=TextEnum.MATE))

        self.frame.data_folder_path_label.bind('<Button-1>', self.set_data_folder_path_controller())
        self.frame.choose_dir_fromwhere_data_filedialog_btn.config(
            command=lambda: self.choose_folder(folder='data_folder_report_path'))

        self.frame.where_save_reports_label.bind('<Button-1>', self.set_save_reports_folder_path_controller())
        self.frame.choose_dir_to_save_filedialog_btn.config(
            command=lambda: self.choose_folder(folder='save_report_folder_path'))

        self.password = self.frame.set_password_btn.config(command=self.set_password_to_report)
        self.migration_date = self.frame.set_migration_date_btn.config(command=self.set_migration_date)
        self.frame.start_btn.config(command=self.switch_to_report)
        self.frame.check_btn.config(command=self.switch_to_report)
        self.frame.xmark_btn.config(command=self.xmark_do_report)

    def handle_back(self) -> None:
        self.update_to_clear_view()
        current_report = self.model.report_stage_flow_model.current_report
        print(f"FlowLoadController: handle_back(){current_report=} \
              {self.model.base_data_frame_model.save_report_folder_path} \
              {self.model.base_data_frame_model.data_folder_report_path}")
        if current_report:
            current_report['stage_str'] = None
            current_report['flow_str'] = None
        self.view.switch('stage')

    def handle_selected_flow(self, flow: TextEnum) -> None:
        report = {"stage_str": TextEnum.LOAD, "flow_str": flow}
        self.update_to_clear_view()
        self.model.report_stage_flow_model.report_save(report)
        for child in self.frame.winfo_children():
            if child.winfo_class() == "Button":
                child.config(fg_color="black")
        name_btn = str(flow) + '_btn'
        if hasattr(self.frame, name_btn):
            style = ttk.Style()
            style.configure("Red.TButton", background="red", foreground="red")
            style.map("Red.TButton",
                      background=[("pressed", "red")],
                      foreground=[("pressed", "red")])
            getattr(self.frame, name_btn).config(style="Red.TButton")
        else:
            self.add_text_to_info_label('Naciśnięto niepoprawny przycisk.')

    def update_view(self):
        current_report = self.model.report_stage_flow_model.current_report
        print(f'FlowLoadController: update_view() {current_report=}')
        if current_report:
            flow = current_report["flow_str"]

            self.add_text_to_info_label(f'Sprawdzam czy dla raportu GoForLoad {flow} są wszystkie potrzebne pliki.')
            missing_files = self.check_folder_for_files(flow_paths.get(str(flow) + '_paths', []))
            if missing_files is None:
                self.frame.check_btn.place_forget()
                self.frame.xmark_btn.place_forget()
                self.add_text_to_info_label('Wszytkie potrzebne pliki znajdują się w folderze.')
                self.frame.start_btn.place(x=390, y=430, width=165, height=40)
            else:
                self.frame.start_btn.place_forget()
                self.add_text_to_info_label(f'Brak następujących plików w folderze: {missing_files}')
                self.add_text_to_info_label(f'Czy chcesz kontynuować \nbez tych plików?')
                self.frame.check_btn.place(x=330, y=430, width=35, height=35)
                self.frame.xmark_btn.place(x=375, y=430, width=35, height=35)
        else:
            print(f"ERROR: 'FlowLoadController: update_view() {current_report=}'")

    def update_to_clear_view(self):
        current_report = self.model.report_stage_flow_model.current_report
        self.frame.info_label.delete('1.0', tk.END)
        self.add_text_to_info_label(f'Wybierz dla którego przepływu chcecsz wykonać raport Go4Load.')
        self.frame.check_btn.place_forget()
        self.frame.xmark_btn.place_forget()
        try:
            for child in self.frame.winfo_children():
                if child.winfo_class() == "Button":
                    child.config(bg="SystemButtonFace", activebackground="SystemButtonFace", fg='green',
                                 activeforeground="blue", highlightbackground="SystemButtonFace",
                                 highlightcolor="SystemButtonFace")

            name_btn = str(current_report['flow_str']) + '_btn'
            if hasattr(self.frame, name_btn):
                style = ttk.Style()
                style.configure("Black.TButton", background="white", foreground="black")
                style.map("Black.TButton",
                          background=[("pressed", "orange")],
                          foreground=[("pressed", "purple")])
                getattr(self.frame, name_btn).config(style="Black.TButton")
        except Exception as e:
            pass

    def set_data_folder_path_controller(self, path: str = '') -> None:
        print(f'set_data_folder_path_controller(): {path}')
        if path != '':
            self.model.base_data_frame_model.set_data_folder_path(path)
            self.frame.data_folder_path_label.config(text=f'{path}')
        elif path == '':
            path = os.path.join(os.getcwd(), 'dane')
            self.model.base_data_frame_model.set_data_folder_path(path)
            self.frame.data_folder_path_label.config(text=f'{path}')
        else:
            path = self.model.base_data_frame_model.data_folder_report_path
            self.frame.data_folder_path_label.config(text='')
            self.frame.data_folder_path_label.config(text=f'{path}')

    def set_save_reports_folder_path_controller(self, path='') -> None:
        print(f'set_save_reports_folder_path_controller(): {path}')
        if path != '':
            self.model.base_data_frame_model.set_save_report_folder_path(path)
            self.frame.where_save_reports_label.config(text=f'{path}')
        elif path == '':
            path = os.path.join(os.getcwd(), 'raporty')
            self.model.base_data_frame_model.set_save_report_folder_path(path)
            self.frame.where_save_reports_label.config(text=f'{path}')
        else:
            path = self.model.base_data_frame_model.save_report_folder_path
            self.frame.where_save_reports_label.config(text='')
            self.frame.where_save_reports_label.config(text=f'{path}')
            self.frame.update_idletasks()

    def save_report_folder_path_update_view(self):
        path = self.model.base_data_frame_model.save_report_folder_path
        self.frame.where_save_reports_label.config(text=f'{path}')

    def data_folder_report_path_update_view(self):
        path = self.model.base_data_frame_model.data_folder_report_path
        self.frame.data_folder_path_label.config(text=f'{path}')

    def choose_folder(self, folder: str) -> None:
        print(f'FlowLoadController: choose_folder( )')
        folder_path = filedialog.askdirectory()
        if folder_path:
            if folder == 'data_folder_report_path':
                self.set_data_folder_path_controller(folder_path)
                self.add_text_to_info_label('Zmieniono folder z którego pobiane są dane do raportów.')
            if folder == 'save_report_folder_path':
                self.set_save_reports_folder_path_controller(folder_path)
                self.add_text_to_info_label('Zmieniono folder w którym zostaną zapisane raporty.')

    def switch_to_report(self) -> None:
        print(f'FlowLoadController: switch_to_report()')
        self.model.report_stage_flow_model.call_the_report_generation_function()

    def check_folder_for_files(self, paths_: list[dict]) -> list[str] | None:
        print(f'FlowLoadController: check_folder_for_files()')

        directory_path = self.model.base_data_frame_model.data_folder_report_path
        missing_files = []

        for path_info in paths_:
            src_path = os.path.join(directory_path, path_info['src'])
            ext_path = os.path.join(directory_path, path_info['ext'])

            if not os.path.isfile(src_path):
                missing_files.append(path_info['src'])
            if not os.path.isfile(ext_path):
                missing_files.append(path_info['ext'])

        if missing_files:
            return missing_files  # Returns a list of missing files
        else:
            return None  # All files for this flow have been found

    def xmark_do_report(self) -> None:
        self.add_text_to_info_label(f'\nDodaj pliki do folderu '
                                    f'{self.model.base_data_frame_model.data_folder_report_path}')
        self.frame.check_btn.place_forget()
        self.frame.xmark_btn.place_forget()

    def set_password_to_report(self):
        self.frame.show_set_password_window(self.password_received_callback)

    def password_received_callback(self, password):
        print(f"password_received_callback(): {password}")
        self.model.base_data_frame_model.set_password_to_report(password)
        self.add_text_to_info_label(f'\nNadano hasło: '
                                    f'{self.model.base_data_frame_model.password_report}')

    def set_migration_date(self):
        self.frame.show_calendar_window(self.calendar_received_callback)

    def calendar_received_callback(self, date):
        print(f"calendar_received_callback(): {date}")
        self.model.base_data_frame_model.set_migration_date(date)
        self.add_text_to_info_label(f"\nUstawiono datę migracji na: {self.model.base_data_frame_model.migration_date}")

    def add_text_to_info_label(self, new_text: str) -> None:
        print(f'FlowLoadController: add_text_to_info_label()')
        self.frame.info_label.insert(tk.END, f'{new_text}\n\n')
        self.frame.info_label.see(tk.END)
