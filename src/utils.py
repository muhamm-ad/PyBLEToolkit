import customtkinter as ctk

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
