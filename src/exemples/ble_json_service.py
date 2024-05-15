from src.service import AbstractService
from src.service_tab import ServiceTab
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.json import JSONCharacteristic
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from cairosvg import svg2png
from PIL import Image
import numpy as np
import io
import pygal
import json
from pygal.style import Style

SOUND_MAX = 100
HUMIDITY_MAX = 100

# Define your custom style
custom_style = Style(
    background='white',
    plot_background='white',
    foreground='black',
    foreground_strong='black',
    foreground_subtle='black',
    opacity='.6',
    opacity_hover='.9',
    transition='400ms ease-in',
    colors=('#E80080', '#404040', '#9BC850', '#FF8000')
)


class JSONServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._fig = Figure(dpi=100)

        self.initialize_data_storage()
        self.setup_subplots()
        self._setup_axes()

        # Add the canvas to Tkinter
        self._canvas = FigureCanvasTkAgg(self._fig, master=master)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(sticky="nsew", **kwargs)
        self._update_plot()

        # Reduce padding and adjust layout
        self._fig.set_tight_layout(True)

    def initialize_data_storage(self):
        self._prox_data = []
        self._temp_data = []
        self._barom_data = []
        self._altitude_data = []
        self._color_data = {'Red': 0.0, 'Green': 0.0, 'Blue': 0.0, 'Clear': 0.0}
        self._magnetic_data = {'x': [], 'y': [], 'z': []}
        self._acce_data = {'x': [], 'y': [], 'z': []}
        self._gyro_data = {'x': [], 'y': [], 'z': []}
        self._sound_data = 0
        self._humidity_data = 0

    def setup_subplots(self):
        self._prox_ax = self._fig.add_subplot(7, 2, 1)  # Row 1, Column 1
        self._temp_ax = self._fig.add_subplot(7, 2, 2)  # Row 1, Column 2
        self._barom_ax = self._fig.add_subplot(7, 2, 3)  # Row 2, Column 1
        self._altitude_ax = self._fig.add_subplot(7, 2, 4)  # Row 2, Column 2

        # Gauges subplot spans two rows in column 1, positioned at Rows 3 and 4
        self._gauges_ax = self._fig.add_subplot(7, 2, (5, 7))  # Rows 3 and 4, Column 1

        self._color_ax = self._fig.add_subplot(7, 2, (6, 8))  # Rows 3 and 4, Column 2

        self._magnetic_ax = self._fig.add_subplot(7, 1, 5)  # Entire Row 5
        self._acce_ax = self._fig.add_subplot(7, 1, 6)  # Entire Row 6
        self._gyro_ax = self._fig.add_subplot(7, 1, 7)  # Entire Row 7



    def _setup_axes(self):
        # Setup the axes with titles and grid configuration
        for ax, title, ylabel in [
            (self._prox_ax, "Proximity", "Distance"),
            (self._temp_ax, "Temperature", "Celsius"),
            (self._barom_ax, "Barometric Pressure", "hPa"),
            (self._altitude_ax, "Altitude", "Meters"),
            (self._magnetic_ax, "Magnetic", "Field Strength"),
            (self._acce_ax, "Acceleration", "m/s²"),
            (self._gyro_ax, "Gyro", "Radians/sec"),
        ]:
            ax.set_title(title)
            ax.set_ylabel(ylabel)
            ax.grid(True)

    def append_sensor_data(self, data):
        self._prox_data.append(float(data['Sensors']['Proximity']))
        self._temp_data.append(float(data['Sensors']['Temperature'].replace(" C", "")))
        self._barom_data.append(float(data['Sensors']['Barometric_pressure']))
        self._altitude_data.append(float(data['Sensors']['Altitude'].replace(" m", "")))

        self._magnetic_data['x'].append(float(data['Sensors']['Magnetic']['x']))
        self._magnetic_data['y'].append(float(data['Sensors']['Magnetic']['y']))
        self._magnetic_data['z'].append(float(data['Sensors']['Magnetic']['z']))
        self._acce_data['x'].append(float(data['Sensors']['Acceleration']['x']))
        self._acce_data['y'].append(float(data['Sensors']['Acceleration']['y']))
        self._acce_data['z'].append(float(data['Sensors']['Acceleration']['z']))
        self._gyro_data['x'].append(float(data['Sensors']['Gyro']['x']))
        self._gyro_data['y'].append(float(data['Sensors']['Gyro']['y']))
        self._gyro_data['z'].append(float(data['Sensors']['Gyro']['z']))

        self._sound_data = float(data['Sensors']['Sound_level'])
        self._humidity_data = float(data['Sensors']['Humidity'].replace(" %", ""))

        self._color_data['Red'] = float(data['Sensors']['Color']['Red'])
        self._color_data['Green'] = float(data['Sensors']['Color']['Green'])
        self._color_data['Blue'] = float(data['Sensors']['Color']['Blue'])
        self._color_data['Clear'] = float(data['Sensors']['Color']['Clear'])

    def _update_plot(self):
        self.clear_all()
        self.redraw_all()
        self._canvas.draw()  # Redraw canvas

    def clear_all(self):
        # Clear previous data
        for ax in [self._prox_ax, self._temp_ax, self._barom_ax, self._altitude_ax, self._gauges_ax,
                   self._magnetic_ax, self._acce_ax, self._gyro_ax, self._color_ax]:
            ax.cla()

    def redraw_all(self):
        self._redraw_axes()
        self._redraw_gauges()
        self._redraw_colors()

    def _redraw_axes(self):
        self._setup_axes()

        self._prox_ax.plot(self._prox_data)
        self._temp_ax.plot(self._temp_data)
        self._barom_ax.plot(self._barom_data)
        self._altitude_ax.plot(self._altitude_data)

        self._magnetic_ax.plot(self._magnetic_data['x'], label='x')
        self._magnetic_ax.plot(self._magnetic_data['y'], label='y')
        self._magnetic_ax.plot(self._magnetic_data['z'], label='z')
        self._magnetic_ax.legend()

        self._acce_ax.plot(self._acce_data['x'], label='x')
        self._acce_ax.plot(self._acce_data['y'], label='y')
        self._acce_ax.plot(self._acce_data['z'], label='z')
        self._acce_ax.legend()

        self._gyro_ax.plot(self._gyro_data['x'], label='x')
        self._gyro_ax.plot(self._gyro_data['y'], label='y')
        self._gyro_ax.plot(self._gyro_data['z'], label='z')
        self._gyro_ax.legend()

    def _redraw_gauges(self):
        gauge = pygal.SolidGauge(inner_radius=0.70, half_pie=True,  style=custom_style)
        gauge.add(title='Sound Level (dB)', values=[{'value': self._sound_data, 'max_value': SOUND_MAX}])
        gauge.add(title='Humidity', values=[{'value': self._humidity_data, 'max_value': HUMIDITY_MAX}],
                  formatter=lambda x: '{:.10g}%'.format(x))
        svg_data = gauge.render()
        png_image = svg2png(bytestring=svg_data)
        image = Image.open(io.BytesIO(png_image))
        self._gauges_ax.imshow(np.array(image), aspect='auto')
        self._gauges_ax.axis('off')  # Hide axis

    def _redraw_colors(self):
        # TODO
        self._color_ax.axis('off')

    def update_data(self, new_data):
        self.append_sensor_data(json.loads(new_data))
        self._update_plot()


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
