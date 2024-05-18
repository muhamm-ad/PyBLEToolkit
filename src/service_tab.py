import customtkinter as ctk


def abstractmethod(method):
    method.is_abstract = True

    def inner(*args, **kwargs):
        raise NotImplementedError(f"Method '{method.__name__}' "
                                  f"is abstract and must be implemented by subclasses.")

    return inner


class ServiceTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    @abstractmethod
    def update_data(self, data):
        pass
