from src.utils import TAB_X_PADDING, TAB_Y_PADDING, TRANSPARENT_COLOR
from src.connection_tab import ConnectionTab
import customtkinter as ctk

BASE_WINDOW_WIDTH = 2560
BASE_WINDOW_HEIGHT = 1440
DEFAULT_APPEARANCE_MODE = "Dark"
DEFAULT_COLOR_THEME = "blue"
DEFAULT_APP_SCALING = 1.3


class BLEToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.set_layout()

        self.data_tab = None
        self.connection_tab = None
        self.initialize_tabs()

    def set_layout(self):
        self.title("BLEToolkit")
        self.geometry(f"{BASE_WINDOW_WIDTH}x{BASE_WINDOW_HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.closing_handler)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

    def make_data_tab(self):
        data_tab = ctk.CTkFrame(master=self, bg_color=TRANSPARENT_COLOR)
        data_tab.grid_columnconfigure(0, weight=1)
        data_tab.grid_rowconfigure(0, weight=1)
        return data_tab

    def make_connection_tab(self):
        connection_tab = ConnectionTab(master=self, master_srv_tab=self.data_tab)
        connection_tab.grid_columnconfigure(0, weight=1)
        connection_tab.grid_rowconfigure(0, weight=1)
        return connection_tab

    def initialize_tabs(self):
        self.data_tab = self.make_data_tab()
        self.data_tab.grid(row=0, column=1, padx=TAB_X_PADDING, pady=TAB_Y_PADDING, sticky="nsew")

        self.connection_tab = self.make_connection_tab()
        self.connection_tab.grid(row=0, column=0, padx=TAB_X_PADDING, pady=TAB_Y_PADDING, sticky="nsew")

    def closing_handler(self):
        self.connection_tab.quit()
        self.quit()


def initialize_app_settings():
    ctk.set_appearance_mode(DEFAULT_APPEARANCE_MODE)
    ctk.set_default_color_theme(DEFAULT_COLOR_THEME)
    ctk.set_widget_scaling(DEFAULT_APP_SCALING)


if __name__ == '__main__':
    initialize_app_settings()
    app = BLEToolkitApp()
    app.mainloop()
