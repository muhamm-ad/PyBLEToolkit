import json

from src.service import AbstractService
from src.service_tab import ServiceTab
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.json import JSONCharacteristic

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class JSONServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._fig = Figure(figsize=(20, 20), dpi=100)

        # Create subplots for each sensor type according to the desired layout
        self._prox_ax = self._fig.add_subplot(5, 2, 1)
        self._temp_ax = self._fig.add_subplot(5, 2, 2)
        self._barom_ax = self._fig.add_subplot(5, 2, 3)
        self._altitude_ax = self._fig.add_subplot(5, 2, 4)
        self._color_ax = self._fig.add_subplot(5, 2, 5)
        self._sound_ax = self._fig.add_subplot(5, 2, 6)
        self._magnetic_ax = self._fig.add_subplot(5, 2, 7)
        self._acce_ax = self._fig.add_subplot(5, 2, 8)
        self._gyro_ax = self._fig.add_subplot(5, 2, 9)
        self._humidity_ax = self._fig.add_subplot(5, 2, 10)

        # Initialize data storage for plotting
        self._prox_data = []
        self._temp_data = []
        self._barom_data = []
        self._altitude_data = []
        self._color_data = {'Red': [], 'Green': [], 'Blue': [], 'Clear': []}
        self._sound_data = []
        self._magnetic_data = {'x': [], 'y': [], 'z': []}
        self._acce_data = {'x': [], 'y': [], 'z': []}
        self._gyro_data = {'x': [], 'y': [], 'z': []}
        self._humidity_data = []

        # Initial setup for axes
        self._setup_axes(self._prox_ax, title="Proximity")
        self._setup_axes(self._temp_ax, title="Temperature", ylabel="C")
        self._setup_axes(self._barom_ax, title="Barometric Pressure")
        self._setup_axes(self._altitude_ax, title="Altitude", ylabel="m")
        self._setup_axes(self._color_ax, title="Color", ylabel="Intensity")
        self._setup_axes(self._sound_ax, title="Sound Level")
        self._setup_axes(self._magnetic_ax, title="Magnetic")
        self._setup_axes(self._acce_ax, title="Acceleration")
        self._setup_axes(self._gyro_ax, title="Gyro")
        self._setup_axes(self._humidity_ax, title="Humidity", ylabel="%")

        # Add the canvas to Tkinter
        self._canvas = FigureCanvasTkAgg(self._fig, master=master)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(**kwargs)

        # Start the update loop
        self._update_plot()

    def _setup_axes(self, ax, title=None, ylabel='Values'):
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel(ylabel)
        ax.grid(True)
        ax.set_autoscale_on(True)

    def update_data(self, new_data):
        new_data = json.loads(new_data)
        # This method should be called with the new sensor data
        self._prox_data.append(float(new_data['Sensors']['Proximity']))
        self._temp_data.append(float(new_data['Sensors']['Temperature'].replace(" C", "")))
        self._barom_data.append(float(new_data['Sensors']['Barometric_pressure']))
        self._altitude_data.append(float(new_data['Sensors']['Altitude'].replace(" m", "")))

        for color in self._color_data.keys():
            self._color_data[color].append(float(new_data['Sensors']['Color'][color]))

        self._sound_data.append(float(new_data['Sensors']['Sound_level']))

        for axis in self._magnetic_data.keys():
            self._magnetic_data[axis].append(float(new_data['Sensors']['Magnetic'][axis]))

        for axis in self._acce_data.keys():
            self._acce_data[axis].append(float(new_data['Sensors']['Acceleration'][axis]))

        for axis in self._gyro_data.keys():
            self._gyro_data[axis].append(float(new_data['Sensors']['Gyro'][axis]))

        self._humidity_data.append(float(new_data['Sensors']['Humidity'].replace(" %", "")))

        self._update_plot()

    def _update_plot(self):
        # Clear previous data
        self._prox_ax.cla()
        self._temp_ax.cla()
        self._barom_ax.cla()
        self._altitude_ax.cla()
        self._color_ax.cla()
        self._sound_ax.cla()
        self._magnetic_ax.cla()
        self._acce_ax.cla()
        self._gyro_ax.cla()
        self._humidity_ax.cla()

        # Re-setup axes
        self._setup_axes(self._prox_ax, title="Proximity")
        self._setup_axes(self._temp_ax, title="Temperature", ylabel="C")
        self._setup_axes(self._barom_ax, title="Barometric Pressure")
        self._setup_axes(self._altitude_ax, title="Altitude", ylabel="m")
        self._setup_axes(self._color_ax, title="Color", ylabel="Intensity")
        self._setup_axes(self._sound_ax, title="Sound Level")
        self._setup_axes(self._magnetic_ax, title="Magnetic")
        self._setup_axes(self._acce_ax, title="Acceleration")
        self._setup_axes(self._gyro_ax, title="Gyro")
        self._setup_axes(self._humidity_ax, title="Humidity", ylabel="%")

        # Plot new data
        self._prox_ax.plot(self._prox_data)
        self._temp_ax.plot(self._temp_data)
        self._barom_ax.plot(self._barom_data)
        self._altitude_ax.plot(self._altitude_data)

        for color in self._color_data.keys():
            self._color_ax.plot(self._color_data[color], label=color)
        self._color_ax.legend()

        self._sound_ax.plot(self._sound_data)

        for axis in self._magnetic_data.keys():
            self._magnetic_ax.plot(self._magnetic_data[axis], label=axis)
        self._magnetic_ax.legend()

        for axis in self._acce_data.keys():
            self._acce_ax.plot(self._acce_data[axis], label=axis)
        self._acce_ax.legend()

        for axis in self._gyro_data.keys():
            self._gyro_ax.plot(self._gyro_data[axis], label=axis)
        self._gyro_ax.legend()

        self._humidity_ax.plot(self._humidity_data)

        # Auto scale the axes
        self._prox_ax.relim()
        self._prox_ax.autoscale_view()

        self._temp_ax.relim()
        self._temp_ax.autoscale_view()

        self._barom_ax.relim()
        self._barom_ax.autoscale_view()

        self._altitude_ax.relim()
        self._altitude_ax.autoscale_view()

        self._color_ax.relim()
        self._color_ax.autoscale_view()

        self._sound_ax.relim()
        self._sound_ax.autoscale_view()

        self._magnetic_ax.relim()
        self._magnetic_ax.autoscale_view()

        self._acce_ax.relim()
        self._acce_ax.autoscale_view()

        self._gyro_ax.relim()
        self._gyro_ax.autoscale_view()

        self._humidity_ax.relim()
        self._humidity_ax.autoscale_view()

        # Redraw canvas
        self._canvas.draw()



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
            "Sensors": {
                "Proximity": f"{value:.2f}",
                "Temperature": f"{value:.2f} C",
                "Barometric_pressure": f"{value:.2f}",
                "Altitude": f"{value:.2f} m",
                "Color": {
                    "Red": f"{value:.2f}",
                    "Green": f"{value:.2f}",
                    "Blue": f"{value:.2f}",
                    "Clear": f"{value:.2f}"
                },
                "Sound_level": f"{value:.2f}",
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
            }
        }
    )

    def __init__(self, service=None):
        super().__init__(service=service)
        self.connectable = True

    def read(self):
        return self.data

    def write(self):
        pass
