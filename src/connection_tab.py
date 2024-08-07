import threading
import time
from collections import defaultdict

import customtkinter as ctk
from CTkListbox import CTkListbox
from adafruit_ble import BLERadio, BLEConnection
from adafruit_ble.advertising.standard import Advertisement

from src.utils import TRANSPARENT_COLOR, STD_PADDING

BLE = BLERadio()
STOP_SCAN_SLEEP_TIME = 1.5
DEVICE_TIMEOUT = 5
SCAN_TIMEOUT = 2
MESSAGE_TIMEOUT = 2


class DevicesBox(CTkListbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.selected = None

    def add_item(self, display_text):
        self.insert("end", display_text)

    def remove_item(self, display_text):
        for index in range(self.size()):
            if self.get(index) == display_text:
                self.delete(index)
                return

    def clear(self):
        self.clear_selection()
        while self.size() > 0:
            self.delete(0)

    def sort_items(self, reverse=False):
        items = [self.get(i) for i in range(self.size())]
        items.sort(reverse=reverse)
        self.clear()
        for item in items:
            self.add_item(item)

    def update_item(self, old_display_text, new_display_text=None):
        for index in range(self.size()):
            if self.get(index) == old_display_text and new_display_text:
                self.delete(index)
                self.insert(index, new_display_text)

    def update_items(self, items_to_add, items_to_remove):
        for item in items_to_add:
            self.add_item(item)
        for item in items_to_remove:
            self.remove_item(item)

    def get_all_items(self):
        return [self.get(i) for i in range(self.size())]

    def select(self, index):  # Override
        """select the option"""
        for options in self.buttons.values():
            options.configure(fg_color=self.button_fg_color)

        if isinstance(index, int):
            if index in self.buttons:
                selected_button = self.buttons[index]
            else:
                selected_button = list(self.buttons.values())[index]
        else:
            selected_button = self.buttons[index]

        self.selected = selected_button
        selected_button.configure(fg_color=self.select_color, hover=False)
        self.after(0, lambda: selected_button.configure(hover=self.hover))

        if self.command:
            self.command(self.selected.cget("text"))

        self.event_generate("<<ListboxSelect>>")

    def clear_selection(self):
        """Clear the current selection"""
        if self.selected:
            self.selected.configure(fg_color=self.button_fg_color)
            self.selected = None


class MessageLabel(ctk.CTkLabel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._message_clear_id = None
        self._current_message = ""
        self._current_message_color = "white"

    def update_message(self, message: str, color: str = "white", timeout: int = None, clear_after: bool = False):
        if clear_after:
            self._current_message = ""

        if self._message_clear_id is not None:
            self.after_cancel(self._message_clear_id)  # Cancel any existing scheduled clear

        self.configure(text=message, text_color=color)

        if timeout is not None:
            # Schedule to clear the message and revert to the continuous message
            self._message_clear_id = self.after(timeout * 1000, self._clear_message, self._current_message,
                                                self._current_message_color)
        else:
            self._current_message = message  # Keep track of the current continuous message
            self._current_message_color = color  # Keep track of the current continuous message color
            self._message_clear_id = None

    def _clear_message(self, message, color):
        self.configure(text=message, text_color=color)  # Revert to the continuous message and color
        self._message_clear_id = None


class InfoFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=2)
        self.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._address_entry = self._create_label_entry(0, "Address")
        self._connectable_entry = self._create_label_entry(1, "Connectable")
        self._rssi_entry = self._create_label_entry(2, "RSSI")
        self._tx_power_entry = self._create_label_entry(3, "Tx Power")
        self._complete_name_entry = self._create_label_entry(4, "Name")
        self._short_name_entry = self._create_label_entry(5, "Short Name")

    def _create_label_entry(self, row, text, entry_width=300, state="readonly"):
        label = ctk.CTkLabel(master=self, text=text, anchor="w")
        label.grid(row=row, column=0, sticky="w")
        entry = ctk.CTkEntry(master=self, width=entry_width, state=state, justify='center', fg_color=TRANSPARENT_COLOR)
        entry.grid(row=row, column=1, padx=(STD_PADDING, 0), pady=STD_PADDING, sticky="nsew")
        return entry

    def update_entries(self, advertisement: Advertisement):
        self._update_entry(self._address_entry, advertisement.address.string)
        self._update_entry(self._connectable_entry, str(advertisement.connectable))
        self._update_entry(self._rssi_entry, str(advertisement.rssi))
        tx_power_value = advertisement.tx_power
        self._update_entry(self._tx_power_entry, str(tx_power_value if tx_power_value is not None else "N/A"))
        self._update_entry(self._complete_name_entry, advertisement.complete_name or "")
        self._update_entry(self._short_name_entry, advertisement.short_name or "")

    def _update_entry(self, entry, value):
        entry.configure(state=ctk.NORMAL)
        entry.delete(0, ctk.END)
        entry.insert(0, value)
        entry.configure(state=ctk.DISABLED)

    def clear_entries(self):
        self._clear_entry(self._address_entry)
        self._clear_entry(self._connectable_entry)
        self._clear_entry(self._rssi_entry)
        self._clear_entry(self._tx_power_entry)
        self._clear_entry(self._complete_name_entry)
        self._clear_entry(self._short_name_entry)

    def _clear_entry(self, entry):
        entry.configure(state=ctk.NORMAL)
        entry.delete(0, ctk.END)
        entry.configure(state=ctk.DISABLED)


class ConnectionTab(ctk.CTkFrame):
    def __init__(self, master, service_connect_command, service_disconnect_command, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 2, 3, 4), weight=0)
        self.grid_rowconfigure(1, weight=4)
        self._srv_connect_cmd = service_connect_command
        self._srv_disconnect_cmd = service_disconnect_command

        self._devices = defaultdict(lambda: {'last_seen': 0.0, 'advertisements': Advertisement})
        self._scanning: bool = False
        self._scanning_thread = None
        self._thread_lock = threading.Lock()
        self._current_connection: BLEConnection = None
        self._selected_advert: Advertisement = None

        scanning_frame = self._create_scanning_frame()
        connecting_frame = self._create_connecting_frame()
        self._progressbar = ctk.CTkProgressBar(master=self, mode="indeterminate", determinate_speed=1)
        self._message_label = MessageLabel(master=self, text="", anchor="center")
        self._devices_box: DevicesBox = DevicesBox(master=self, justify="center", label_text="Discovered Devices",
                                                   command=self._select_device_cmd)

        scanning_frame.pack(pady=STD_PADDING, padx=STD_PADDING)
        self._devices_box.pack(padx=STD_PADDING, pady=STD_PADDING, fill=ctk.BOTH, expand=True)
        self._progressbar.pack(fill=ctk.BOTH, padx=STD_PADDING, pady=(0, 20))
        connecting_frame.pack(pady=STD_PADDING, padx=STD_PADDING, fill=ctk.BOTH)
        self._message_label.pack(padx=STD_PADDING, pady=(0, STD_PADDING), fill=ctk.BOTH)

    def _create_scanning_frame(self):
        buttons_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        self._scan_button = ctk.CTkButton(master=buttons_frame, text="Scan for Devices",
                                          command=self._start_scanning_cmd)
        self._stop_button = ctk.CTkButton(master=buttons_frame, text="Stop Scanning",
                                          command=self._stop_scanning_cmd, state=ctk.DISABLED)
        self._scan_button.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        self._stop_button.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        return buttons_frame

    def _start_scanning_cmd(self):
        if not self._scanning:
            self._scanning = True
            if self._scanning_thread is None:
                self._scanning_thread = threading.Thread(target=self._scan_for_devices_background, daemon=True)
                self._scanning_thread.start()
        self._progressbar.start()
        self._scan_button.configure(state=ctk.DISABLED)
        self._stop_button.configure(state=ctk.NORMAL)

    def _stop_scanning_cmd(self):
        if self._scanning:
            self._scanning = False
            time.sleep(STOP_SCAN_SLEEP_TIME)
            self._scanning_thread = None
        self._progressbar.stop()
        self._scan_button.configure(state=ctk.NORMAL)
        self._stop_button.configure(state=ctk.DISABLED)

    def _create_connecting_frame(self):
        connect_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)

        self._info_frame = InfoFrame(master=connect_frame, fg_color=TRANSPARENT_COLOR)

        buttons_frame = ctk.CTkFrame(master=connect_frame, fg_color=TRANSPARENT_COLOR)
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        self._connect_button = ctk.CTkButton(master=buttons_frame, text="Connect",
                                             command=self._connect_cmd, state=ctk.DISABLED)
        self._disconnect_button = ctk.CTkButton(master=buttons_frame, text="Disconnect",
                                                command=self._disconnect_cmd, state=ctk.DISABLED)
        self._connect_button.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
        self._disconnect_button.grid(column=1, row=0, padx=10, pady=10, sticky="ew")

        self._info_frame.pack()
        buttons_frame.pack()

        return connect_frame

    def _connect_cmd(self):
        self._stop_scanning_cmd()
        self._connect_button.configure(state=ctk.DISABLED)

        if self._selected_advert.connectable:
            if BLE.connected:
                self._disconnect_cmd()

            self._message_label.update_message(message="Connecting ...", color="white")

            if self._handle_connection():
                self._message_label.update_message(message="Connected", color="green")
                self._srv_connect_cmd(self._selected_advert, self._current_connection)
                self._disconnect_button.configure(state=ctk.NORMAL)
                self._scan_button.configure(state=ctk.DISABLED)
            else:
                # self._message_label.update_message(message="Not Connected", color="red", timeout=MESSAGE_TIMEOUT)
                self._disconnect_button.configure(state=ctk.DISABLED)
                self._release_selected_device()
        else:
            self._message_label.update_message(message="Not connectable", color="red", timeout=MESSAGE_TIMEOUT)
            self._disconnect_button.configure(state=ctk.DISABLED)
            self._release_selected_device()

    def _handle_connection(self):
        def handle_error(err):
            print(f"Connection failed due to unexpected error: {err}")
            self._message_label.update_message(message="Connection failed", color="red",
                                               timeout=MESSAGE_TIMEOUT, clear_after=True)
            return False

        try:
            self._current_connection = BLE.connect(self._selected_advert, timeout=3)
        except Exception as e:
            if "org.bluez.Error.InProgress" in str(e):
                time.sleep(0.5)  # Wait before retrying
                try:
                    self._current_connection = BLE.connect(self._selected_advert, timeout=3)
                except Exception as e:
                    return handle_error(e)
            else:
                return handle_error(e)

        return self._current_connection and self._current_connection.connected

    def _disconnect_cmd(self):
        self._message_label.update_message(message="Disconnecting ...", color="white")
        self._disconnect_button.configure(state=ctk.DISABLED)

        if self._handle_disconnection():
            self._message_label.update_message(message="Disconnected", color="white",
                                               timeout=MESSAGE_TIMEOUT * 2, clear_after=True)
            self._release_selected_device()
            self._start_scanning_cmd()
        else:
            self._message_label.update_message(message="Disconnection failed", color="red",
                                               timeout=MESSAGE_TIMEOUT, clear_after=True)

    def _handle_disconnection(self):
        try:
            self._srv_disconnect_cmd()
            if self._current_connection is not None:
                self._current_connection.disconnect()
            self._current_connection = None
        except Exception as e:
            print(f"Disconnection failed due to unexpected error: {e}")
            raise e

        return self._current_connection is None or not self._current_connection.connected

    def _scan_for_devices_background(self):
        while True:
            try:
                self._scan_for_devices_background_handler()
                self.after(0, self._update_devices_list)
            except Exception as e:
                print(f"Error during continuous scan: {e}")
                self._message_label.update_message(message="Error during scan", color="red",
                                                   timeout=MESSAGE_TIMEOUT, clear_after=True)
            finally:
                BLE.stop_scan()
                if not self._scanning:
                    break

    def _scan_for_devices_background_handler(self):
        for adv in BLE.start_scan(Advertisement, timeout=SCAN_TIMEOUT):
            address = adv.address.string
            with self._thread_lock:
                if address not in self._devices:
                    self._devices[address] = dict(last_seen=time.time(), advertisements=adv)
                else:
                    self._devices[address]['last_seen'] = time.time()

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

    def _update_devices_list(self):
        for address in list(self._devices.keys()):
            if time.time() - self._devices[address]['last_seen'] > DEVICE_TIMEOUT:
                del self._devices[address]
        with self._thread_lock:
            current_displayed_devices = set(self._devices_box.get_all_items())
            detected_devices = self._get_detected_devices()

            devices_to_add = detected_devices - current_displayed_devices
            devices_to_remove = current_displayed_devices - detected_devices

            self._devices_box.update_items(devices_to_add, devices_to_remove)

    def quit_(self):
        self._stop_scanning_cmd()
        self._disconnect_cmd()

    def _select_device_cmd(self, selected_device: str):
        address = selected_device.split("(")[0]
        self._selected_advert = self._devices[address.strip()]['advertisements']
        self._update_connection_button()
        self._info_frame.update_entries(self._selected_advert)

    def _update_connection_button(self):
        if self._selected_advert and self._selected_advert.connectable:
            self._connect_button.configure(state=ctk.NORMAL)
        else:
            self._connect_button.configure(state=ctk.DISABLED)

    def _release_selected_device(self):
        self._selected_advert = None
        self._devices_box.clear_selection()
        self._info_frame.clear_entries()
        self._connect_button.configure(state=ctk.DISABLED)
        self._disconnect_button.configure(state=ctk.DISABLED)
