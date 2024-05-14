import abc
from adafruit_ble.services import Service
import customtkinter as ctk


class ServiceTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    @abc.abstractmethod
    def update_data(self, data):
        pass


class AbstractService(Service, abc.ABC):
    def __init__(self, service=None):
        super().__init__(service=service)

    @abc.abstractmethod
    def read(self):
        pass

    @abc.abstractmethod
    def write(self):
        pass
