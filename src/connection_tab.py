from adafruit_ble.advertising.standard import Advertisement
from src.utils import TRANSPARENT_COLOR, STD_PADDING
from src import SERVICE_REGISTER
from src.service import AbstractService
from src.service_tabs_manager import ServiceTabsManager
from src.selectable_button_list import SelectableButtonList
from adafruit_ble import BLERadio, BLEConnection
from collections import defaultdict
from functools import partial
import customtkinter as ctk
import threading
import time

BLE = BLERadio()
SLEEP_TIME = 2
DEVICE_TIMEOUT = 5
MESSAGE_TIMEOUT = 2


class ConnectionTab(ctk.CTkFrame):
    def __init__(self, master, master_srv_tab, **kwargs):
        super().__init__(master, **kwargs)
        self._service_tabs_manager = ServiceTabsManager(master=master_srv_tab)

        self._configure_grid_layout()

        self._scan_button = None
        self._stop_button = None
        self._devices_frame = None
        self._services_frame = None
        self._progressbar = None
        self._message_label = None
        self._message_clear_id = None
        self._current_message = ""
        self._create_widgets()

        self._devices = defaultdict(lambda: {'last_seen': 0.0, 'advertisements': Advertisement})
        self._scanning = False
        self._scanning_thread = None
        self._thread_lock = threading.Lock()

        self._current_connection = None

    def _configure_grid_layout(self):
        self.grid_columnconfigure(0, weight=1)

    def _create_scanning_frame(self):
        buttons_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        self._scan_button = ctk.CTkButton(master=buttons_frame, text="Scan for Devices",
                                          command=self._start_scanning_devices)
        self._stop_button = ctk.CTkButton(master=buttons_frame, text="Stop Scanning",
                                          command=self._stop_scanning_devices, state=ctk.DISABLED)
        self._scan_button.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        self._stop_button.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        return buttons_frame

    def _create_selectable_button_lists(self):
        self._devices_frame = SelectableButtonList(master=self, label_text="Discovered Devices")
        self._services_frame = SelectableButtonList(master=self, label_text="Services")

    def _create_widgets(self):
        scanning_frame = self._create_scanning_frame()
        self._create_selectable_button_lists()
        self._progressbar = ctk.CTkProgressBar(master=self, mode="indeterminate", determinate_speed=2)
        self._message_label = ctk.CTkLabel(master=self, text="", anchor="center")

        scanning_frame.pack(pady=STD_PADDING, padx=STD_PADDING)
        self._devices_frame.pack(padx=STD_PADDING, pady=STD_PADDING, fill=ctk.BOTH, expand=True)
        self._progressbar.pack(fill=ctk.BOTH, padx=STD_PADDING, pady=(0, 20))
        self._services_frame.pack(padx=STD_PADDING, pady=STD_PADDING, fill=ctk.BOTH, expand=True)
        self._message_label.pack(padx=STD_PADDING, pady=(0, STD_PADDING), fill=ctk.BOTH)

    def _stop_scanning_devices(self):
        if self._scanning:
            self._scanning = False
            time.sleep(SLEEP_TIME)
            self._scanning_thread = None
        self._progressbar.stop()
        self._scan_button.configure(state=ctk.NORMAL)
        self._stop_button.configure(state=ctk.DISABLED)
        self._update_message("Stopped scanning")

    def _start_scanning_devices(self):
        if not self._scanning:
            self._scanning = True
            if self._scanning_thread is None:
                self._scanning_thread = threading.Thread(target=self._scan_for_devices_background, daemon=True)
                self._scanning_thread.start()
        self._progressbar.start()
        self._scan_button.configure(state=ctk.DISABLED)
        self._stop_button.configure(state=ctk.NORMAL)
        self._update_message("Scanning for devices...")

    def _scan_for_devices_background(self):
        while True:
            try:
                self._scan_for_device_background_handler()
                self.after(0, self._update_devices_list)

            except Exception as e:
                print(f"Error during continuous scan: {e}")
                self._update_message(f"Error during scan", "red", timeout=MESSAGE_TIMEOUT)
            finally:
                BLE.stop_scan()
                if not self._scanning:
                    break

    def _scan_for_device_background_handler(self):
        for adv in BLE.start_scan(Advertisement, timeout=2):
            address = adv.address.string
            with self._thread_lock:
                if address not in self._devices:
                    self._devices[address] = dict(last_seen=time.time(), advertisements=adv)
                else:
                    self._devices[address]['last_seen'] = time.time()

    def _update_devices_list(self):
        for address in list(self._devices.keys()):
            if time.time() - self._devices[address]['last_seen'] > DEVICE_TIMEOUT:
                del self._devices[address]

        self._update_device_list_ui()

    def _get_detected_devices(self):
        detected_devices = set()
        for address, info in self._devices.items():
            adv = info['advertisements']
            if adv.complete_name:
                device_str = f"{address} ({adv.complete_name})"
            else:
                device_str = f"{address}"
            detected_devices.add(device_str)
        return detected_devices

    def _update_device_list_ui(self):
        with self._thread_lock:
            current_displayed_devices = set(button.cget("text") for button in self._devices_frame.list)
            detected_devices = self._get_detected_devices()

            devices_to_add = detected_devices - current_displayed_devices
            devices_to_remove = current_displayed_devices - detected_devices

            if devices_to_add or devices_to_remove:
                for disp_text in devices_to_add:
                    address = disp_text.split("(")[0]
                    advert = self._devices[address.strip()]['advertisements']
                    self._devices_frame.add_item(display_text=disp_text,
                                                 command=partial(self._select_device, advert))

                for device_info in devices_to_remove:
                    self._devices_frame.remove_item(display_text=device_info)

    def quit(self):
        self._stop_scanning_devices()
        self._disconnect_current_connection()

    def _disconnect_current_connection(self):
        if self._current_connection is not None:
            self._service_tabs_manager.quit()
            self._current_connection.disconnect()

    def _select_device(self, advert: Advertisement):
        if advert.connectable:
            if BLE.connected:
                self._disconnect_current_connection()

            self._update_message(f"Connecting to {advert.address.string}...")
            print(f"Connecting to {advert.address.string}...")

            connection = BLE.connect(advert, timeout=3)
            if connection and connection.connected:
                self._update_message("Connected")
                print("Connected")
                self._current_connection = connection
                self._update_services(advert, connection)
            else:
                self._update_message(f"{advert.address.string} not Connected !!!", "red", timeout=MESSAGE_TIMEOUT)
                print(f"{advert.address.string} not Connected !!!")
        else:
            self._update_message(f"{advert.address.string} not connectable.", "red", timeout=MESSAGE_TIMEOUT)
            print(f"{advert.address.string} not connectable.")

    def _update_services(self, advert, connection: BLEConnection):
        label = "Connected to " + f"{advert.complete_name}" if advert.complete_name else f"{advert.address.string}"
        self._services_frame.configure(label_text=label)

        for srv, tab_class in SERVICE_REGISTER.items():  # UPDATE
            if srv in connection:
                print("Service found: " + str(srv))
                self._services_frame.add_item(display_text=srv.__name__,
                                              command=partial(self._select_service, connection[srv]))

    def _select_service(self, service):
        if not isinstance(service, AbstractService):
            self._update_message("Not an instance of AbstractService", "red", timeout=MESSAGE_TIMEOUT)
            print("Error: Provided service is not an instance of AbstractService")
        else:
            self._service_tabs_manager.select_service(service)

    def _update_message(self, message: str, color: str = "white", timeout: int = None):
        if self._message_clear_id is not None:
            self.after_cancel(self._message_clear_id)  # Cancel any existing scheduled clear

        self._message_label.configure(text=message, text_color=color)

        if timeout is not None:
            # Schedule to clear the message and revert to the continuous message
            self._message_clear_id = self.after(timeout * 1000, self._clear_message, self._current_message,
                                                self._current_message_color)
        else:
            self._current_message = message  # Keep track of the current continuous message
            self._current_message_color = color  # Keep track of the current continuous message color
            self._message_clear_id = None

    def _clear_message(self, message, color):
        self._message_label.configure(text=message, text_color=color)  # Revert to the continuous message and color
        self._message_clear_id = None
