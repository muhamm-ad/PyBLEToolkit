from src.service import AbstractService
from src.service_tab import ServiceTab
from adafruit_ble.services.nordic import UARTService as NordicUARTService


class UartServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # TODO

    def update_data(self, data):
        pass


class UARTService(NordicUARTService, AbstractService):
    def __init__(self, service=None):
        NordicUARTService.__init__(self, service=service)
        AbstractService.__init__(self, service=service)
