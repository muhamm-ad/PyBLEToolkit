from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.json import JSONCharacteristic
from src.services.service import AbstractService, ServiceTab
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class JSONServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def update_data(self, data):
        # TODO
        pass


class JSONService(AbstractService):
    uuid = VendorUUID("51ad213f-e568-4e35-84e4-67af89c79ef0")
    settings = JSONCharacteristic(
        uuid=VendorUUID("e077bdec-f18b-4944-9e9e-8b3a815162b4"),
        properties=Characteristic.READ | Characteristic.WRITE,
        initial_value={},
    )

    value = 0.0
    segment_inc_z = "( 0, 0)"
    data = JSONCharacteristic(
        uuid=VendorUUID("528ff74b-fdb8-444c-9c64-3dd5da4135ae"),
        properties=Characteristic.READ,
        initial_value={
            "Sensor": {
                "Proximity": f"{value:.2f}",
                "Color": {
                    "Red": f"{value:.2f}",
                    "Green": f"{value:.2f}",
                    "Blue": f"{value:.2f}",
                    "Clear": f"{value:.2f}"
                },
                "Temperature": f"{value:.2f} C",
                "Barometric pressure": f"{value:.2f}",
                "Altitude": f"{value:.2f} m",
                "Magnetic": {
                    "x": f"{value:.2f}",
                    "y": f"{value:.2f}",
                    "z": f"{value:.2f}"
                },
                "Acceleration": {
                    "x": f"{value:.2f}",
                    "y": f"{value:.2f}",
                    "z": f"{value:.2f}"
                },
                "Gyro": {
                    "x": f"{value:.2f}",
                    "y": f"{value:.2f}",
                    "z": f"{value:.2f}"
                },
                "Humidity": f"{value:.2f} %",
                "Sound level": f"{value:.2f}"
            }
        }
    )

    def __init__(self, service=None):
        super().__init__(service=service)
        self.connectable = True

    def read(self):
        return self.data
