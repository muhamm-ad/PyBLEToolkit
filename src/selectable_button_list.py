import customtkinter as ctk

from src.utils import STD_PADDING

BUTTON_GRID_CONFIG = {
    "padx": STD_PADDING,
    "pady": (0, STD_PADDING),
    "sticky": "nsew"
}


class SelectableButtonList(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._configure_grid_layout()
        self.list = []

    def _configure_grid_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def add_item(self, display_text=None, command=None, button_layout=None):
        if button_layout is None:
            button_layout = {}
        fg_color = button_layout.get("fg_color", None)
        hover_color = button_layout.get("hover_color", None)
        button = ctk.CTkButton(master=self,
                               text=display_text,
                               command=command,
                               fg_color=fg_color,
                               hover_color=hover_color)
        button.grid(row=len(self.list), column=0, **BUTTON_GRID_CONFIG)
        self.list.append(button)

    def remove_item(self, display_text):
        for button in self.list:
            if display_text == button.cget("text"):
                button.destroy()
                self.list.remove(button)
                self.rearrange_buttons()
                return

    def rearrange_buttons(self):
        """Rearrange buttons after removal to maintain order."""
        for index, button in enumerate(self.list):
            button.grid(row=index, column=0, **BUTTON_GRID_CONFIG)

    def sort_items(self, key=None, reverse=False):
        """
        Sort the items based on a sorting key and optional reverse order.
        The default sorting key is the button text.
        """
        if key is None:
            self.list.sort(key=lambda button: button.cget("text"), reverse=reverse)
        else:
            self.list.sort(key=key, reverse=reverse)
        self.rearrange_buttons()

    def clear(self):
        """Remove all items from the frame."""
        for button in self.list:
            button.destroy()
        self.list.clear()
