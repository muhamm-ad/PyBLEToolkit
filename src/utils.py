import customtkinter as ctk
from adafruit_ble import Advertisement

STD_PADDING = 5
TAB_Y_PADDING = STD_PADDING
TAB_X_PADDING = STD_PADDING

BLUE_COLOR = "#3B8ED0"
TRANSPARENT_COLOR = "transparent"


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
