from adafruit_ble.services import Service


def abstractmethod(method):
    def inner(*args, **kwargs):
        raise NotImplementedError(f"Method '{method.__name__}' is abstract and must be implemented by subclasses.")

    return inner


class AbstractService(Service):
    def __init__(self, service=None):
        super().__init__(service=service)

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self):
        pass
