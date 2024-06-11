import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from CTkToolTip import CTkToolTip
from src import SERVICE_REGISTER
from src.utils import TRANSPARENT_COLOR, STD_PADDING
from src.service_tabs_manager import ServiceTabsManager
from src.abstract_service import AbstractService
from adafruit_ble import BLEConnection, Advertisement
from typing import Dict


class ServicesBox(ctk.CTkFrame):
    def __init__(self, master, select_service_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self._select_srv_cmd = select_service_cmd
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._service_dict: Dict[str, AbstractService] = {}
        self._current_advertisement: Advertisement = None

        # Device frame
        self.device_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        self.device_frame.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="w")
        self.device_label = ctk.CTkLabel(master=self.device_frame, text="No Device Connected", anchor="w")
        self.device_label.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="w")
        self.info_button = ctk.CTkButton(master=self.device_frame, width=20, height=20,
                                         text="i", state=ctk.DISABLED)
        self.info_button.grid(row=0, column=1, padx=(STD_PADDING, 50), pady=STD_PADDING, sticky="e")

        self.tooltip = CTkToolTip(self.info_button, message="No device information available",
                                  justify="left", padding=(STD_PADDING, STD_PADDING))

        # Select frame
        select_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        select_frame.grid(row=0, column=1, padx=STD_PADDING, pady=STD_PADDING)
        service_select_label = ctk.CTkLabel(master=select_frame, text="Select Service", anchor="center")
        service_select_label.grid(row=0, column=0, padx=STD_PADDING, sticky="w")
        self._service_options = ctk.CTkOptionMenu(master=select_frame, anchor="center", command=self.select_opt_cmd)
        self._service_options.set(value="")
        self._service_options.grid(row=0, column=1, padx=STD_PADDING, sticky="w")

        uuid_label = ctk.CTkLabel(master=self, text="UUID:", anchor="w")
        uuid_label.grid(row=0, column=2, padx=(STD_PADDING * 2, 0), pady=STD_PADDING, sticky="w")

        uuid_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        uuid_frame.grid(row=0, column=3, padx=STD_PADDING, pady=STD_PADDING)
        self._uuid_entry = ctk.CTkEntry(master=uuid_frame, width=380, state="readonly",
                                        fg_color=TRANSPARENT_COLOR, justify='center')
        self._uuid_entry.grid(padx=1, pady=1, sticky="nsew")

        self.update_services()

    def update_services(self, advert: Advertisement = None, services_dict: Dict[str, AbstractService] = None):
        if services_dict is None:
            services_dict = {}
        self._service_dict = services_dict
        self._service_options.configure(values=list(self._service_dict.keys()))

        if advert:
            self._current_advertisement = advert
            self.device_label.configure(text=advert.address.string)
            self._update_tooltip(advert)
        else:
            self.device_label.configure(text="No Device Connected")
            self._update_tooltip()

        if self._service_dict:
            default_value = list(self._service_dict.keys())[0]
            self._service_options.set(value=default_value)
            self.select_opt_cmd(default_value)
        else:
            self._service_options.set(value="")
            self._update_entry(self._uuid_entry)

    def select_opt_cmd(self, selected_option: str):
        if selected_option in self._service_dict.keys():
            srv = self._service_dict[selected_option]
            self._select_srv_cmd(srv)
            uuid = srv.get_uuid().upper()
            self._update_entry(self._uuid_entry, uuid)

    def _update_entry(self, entry, text=""):
        entry.configure(state="normal")
        entry.delete(0, ctk.END)
        entry.insert(0, text)
        entry.configure(state="readonly")

    def _update_tooltip(self, advert: Advertisement = None):
        if advert:
            message = (  # TODO : continuous update
                f"RSSI: {advert.rssi}\n"
                f"Tx Power: {advert.tx_power if advert.tx_power is not None else 'N/A'}\n"
                f"Complete Name: {advert.complete_name or ''}\n"
                f"Short Name: {advert.short_name or ''}"
            )
        else:
            message = "No device information available"

        self.tooltip.configure(message=message)


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

    def _select_service_cmd(self, service: AbstractService):
        if not isinstance(service, AbstractService):
            err_msg = "Error: Provided service is not an instance of AbstractService"
            print(err_msg)
            CTkMessagebox(title="Error", message=err_msg, icon="cancel")
        else:
            self._service_tabs_manager.select_service(service)

    def connect(self, advert: Advertisement, connection: BLEConnection):
        services_dict: Dict[str, AbstractService] = {}
        for srv in SERVICE_REGISTER.keys():
            if srv in connection:
                print("Service found: " + str(srv))
                services_dict[srv.__name__] = connection[srv]
        self._services_box.update_services(advert, services_dict)

    def disconnect(self):
        self._services_box.update_services()
        self._service_tabs_manager.disconnect()
