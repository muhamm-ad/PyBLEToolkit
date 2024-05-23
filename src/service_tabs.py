import customtkinter as ctk
from src.utils import TRANSPARENT_COLOR, STD_PADDING
from src.service_tabs_manager import ServiceTabsManager
from typing import Dict
from src.abstract_service import AbstractService


class ServicesBox(ctk.CTkFrame):
    def __init__(self, master, select_service_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self._select_srv_cmd = select_service_cmd
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._service_list: Dict[str, AbstractService] = {}

        select_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        select_frame.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING)
        service_select_label = ctk.CTkLabel(master=select_frame, text="Select Service", anchor="center")
        service_select_label.grid(row=0, column=0, padx=STD_PADDING, sticky="w")
        self._service_options = ctk.CTkOptionMenu(master=select_frame, anchor="center", command=self.select_opt_cmd)
        self._service_options.set(value="")
        self.update_services()
        self._service_options.grid(row=0, column=1, padx=STD_PADDING, sticky="w")

        uuid_label = ctk.CTkLabel(master=self, text="UUID:", anchor="w")
        uuid_label.grid(row=0, column=1, padx=(STD_PADDING * 2, 0), pady=STD_PADDING, sticky="w")

        uuid_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        uuid_frame.grid(row=0, column=2, padx=STD_PADDING, pady=STD_PADDING)
        self._uuid_entry = ctk.CTkEntry(master=uuid_frame, width=380, state="readonly",
                                        fg_color=TRANSPARENT_COLOR, justify='center')
        self._uuid_entry.grid(padx=1, pady=1, sticky="nsew")

    def update_services(self, services_dict: Dict[str, AbstractService] = None):
        if services_dict is None:
            services_dict = {}

        self._service_list = services_dict
        self._service_options.configure(values=self._service_list.keys())

    def select_opt_cmd(self, selected_option: str):
        if selected_option in self._service_list:
            srv = self._service_list[selected_option]
            self._update_entry(self._uuid_entry, srv.get_uuid().upper())
            self._select_srv_cmd(srv)

    def _update_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, ctk.END)
        entry.insert(0, text)
        entry.configure(state="readonly")


class ServiceTabs(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=10)

        self._services_box = ServicesBox(master=self, select_service_cmd=self._select_service_cmd,
                                         fg_color=TRANSPARENT_COLOR)
        self._services_box.pack(padx=STD_PADDING, pady=STD_PADDING)

        service_tab = ctk.CTkFrame(master=self)
        service_tab.grid_columnconfigure(0, weight=1)
        service_tab.grid_rowconfigure(0, weight=1)
        service_tab.pack(fill=ctk.BOTH, expand=True)
        self._service_tabs_manager = ServiceTabsManager(master=service_tab)

    def update_services(self, services_dict: Dict[str, AbstractService] = None):
        self._services_box.update_services(services_dict)

    def _select_service_cmd(self, service: AbstractService):
        if not isinstance(service, AbstractService):
            print("Error: Provided service is not an instance of AbstractService")
            # TODO: Add popup message
        else:
            self._service_tabs_manager.select_service(service)

    def quit_(self):
        self._service_tabs_manager.quit()
