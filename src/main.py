import customtkinter as ctk
from src.connection_tab import ConnectionTab
from src.service_tabs import ServiceTabs

BASE_WINDOW_WIDTH = 2560
BASE_WINDOW_HEIGHT = 1440
DEFAULT_APPEARANCE_MODE = "Dark"
DEFAULT_COLOR_THEME = "blue"
DEFAULT_APP_SCALING = 1.4
STD_PADDING = 5


class BLEToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BLEToolkit")
        self.geometry(f"{BASE_WINDOW_WIDTH}x{BASE_WINDOW_HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.closing_handler)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=10)
        self.grid_rowconfigure(0, weight=1)

        self.service_tabs = ServiceTabs(master=self)
        self.service_tabs.grid_columnconfigure(0, weight=1)
        self.service_tabs.grid_rowconfigure(0, weight=1)
        self.service_tabs.grid(row=0, column=1, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

        self.connection_tab = ConnectionTab(master=self,
                                            service_connect_command=self.service_tabs.connect,
                                            service_disconnect_command=self.service_tabs.disconnect)
        self.connection_tab.grid_columnconfigure(0, weight=1)
        self.connection_tab.grid_rowconfigure(0, weight=1)
        self.connection_tab.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

    def closing_handler(self):
        self.service_tabs.disconnect()
        self.connection_tab.quit_()
        self.quit()


def initialize_app_settings():
    ctk.set_appearance_mode(DEFAULT_APPEARANCE_MODE)
    ctk.set_default_color_theme(DEFAULT_COLOR_THEME)
    ctk.set_widget_scaling(DEFAULT_APP_SCALING)


if __name__ == '__main__':
    initialize_app_settings()
    app = BLEToolkitApp()
    app.mainloop()
