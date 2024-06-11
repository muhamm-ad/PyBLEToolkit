from src.abstract_service import AbstractService
from src.abstract_service_tab import AbstractServiceTab
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.json import JSONCharacteristic
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from src.exemples.CustomFigureCanvasTkAgg import CustomFigureCanvasTkAgg
from io import BytesIO
from cairosvg import svg2png
from PIL import Image
import numpy as np
import pygal
from pygal.style import Style
import json
import re


MAX_DATA_POINTS = 30
SOUND_MAX = 100
HUMIDITY_MAX = 100

CUSTOM_STYLE = Style(
    background='transparent',
    plot_background='transparent',
    font_family='googlefont:Raleway',
    title_font_size=24,
    label_font_size=16,
    major_label_font_size=18,
    value_label_font_size=18,
    tooltip_font_size=18,
    legend_font_size=18,
    transition='400ms ease-in',
    colors=('#F46A6A', '#34A853', '#FBBC04', '#4285F4', '#0F9D58')
)


class ExJSONServiceTab(AbstractServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._fig = Figure(dpi=100)
        self._fig.set_constrained_layout(True)  # Reduce padding and adjust layout

        self._initialize_data_storage()
        self._setup_subplots()
        self._setup_axes()

        # Add the canvas to Tkinter
        self._canvas = CustomFigureCanvasTkAgg(self._fig, master=self)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._update_plot()

    def _initialize_data_storage(self):
        self._xs = []
        self._data_count = 0

        self._sensor_data = {
            'Proximity': [],
            'Temperature': [],
            'Barometric Pressure': [],
            'Altitude': [],
            'Magnetic': {'x': [], 'y': [], 'z': []},
            'Acceleration': {'x': [], 'y': [], 'z': []},
            'Gyro': {'x': [], 'y': [], 'z': []},
        }
        self._color_data = {'Red': 0.0, 'Green': 0.0, 'Blue': 0.0, 'Clear': 0.0}
        self._sound_data = 0
        self._humidity_data = 0

    def _setup_subplots(self):
        self._prox_ax = self._fig.add_subplot(7, 2, 1)
        self._temp_ax = self._fig.add_subplot(7, 2, 2)
        self._barom_ax = self._fig.add_subplot(7, 2, 3)
        self._altitude_ax = self._fig.add_subplot(7, 2, 4)
        self._gauges_ax = self._fig.add_subplot(7, 2, (5, 7))
        self._color_ax = self._fig.add_subplot(7, 2, (6, 8))
        self._magnetic_ax = self._fig.add_subplot(7, 1, 5)
        self._acce_ax = self._fig.add_subplot(7, 1, 6)
        self._gyro_ax = self._fig.add_subplot(7, 1, 7)

    def _setup_axes(self):
        min_x, max_x = self._get_x_limits()

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
            ax.set_xlim(left=min_x, right=max_x)
            ax.set_ylabel(ylabel)
            ax.grid(True)

    def _get_x_limits(self):
        min_x = max(0, self._data_count - MAX_DATA_POINTS) if self._data_count > MAX_DATA_POINTS else 0
        max_x = self._data_count + 1 if self._data_count > MAX_DATA_POINTS else MAX_DATA_POINTS
        return min_x, max_x

    def _truncate_data(self):
        self._xs = self._xs[-MAX_DATA_POINTS:]
        for key in self._sensor_data:
            if isinstance(self._sensor_data[key], dict):
                for subkey in self._sensor_data[key]:
                    self._sensor_data[key][subkey] = self._sensor_data[key][subkey][-MAX_DATA_POINTS:]
            else:
                self._sensor_data[key] = self._sensor_data[key][-MAX_DATA_POINTS:]

    def append_sensor_data(self, data):
        self._data_count += 1
        self._xs.append(self._data_count)

        self._sensor_data['Proximity'].append(float(data['Sensors']['Proximity']))
        self._sensor_data['Temperature'].append(float(data['Sensors']['Temperature'].replace(" C", "")))
        self._sensor_data['Barometric Pressure'].append(float(data['Sensors']['Barometric_pressure']))
        self._sensor_data['Altitude'].append(float(data['Sensors']['Altitude'].replace(" m", "")))

        for axis in ['x', 'y', 'z']:
            self._sensor_data['Magnetic'][axis].append(float(data['Sensors']['Magnetic'][axis]))
            self._sensor_data['Acceleration'][axis].append(float(data['Sensors']['Acceleration'][axis]))
            self._sensor_data['Gyro'][axis].append(float(data['Sensors']['Gyro'][axis]))

        self._sound_data = float(data['Sensors']['Sound_level'])
        self._humidity_data = float(data['Sensors']['Humidity'].replace(" %", ""))

        for color in self._color_data:
            self._color_data[color] = float(data['Sensors']['Color'][color])

        self._truncate_data()

    def _update_plot(self):
        self._clear_all()
        self._redraw_all()
        self._canvas.draw()  # Redraw canvas

    def _clear_all(self):
        for ax in [self._prox_ax, self._temp_ax, self._barom_ax, self._altitude_ax, self._gauges_ax,
                   self._magnetic_ax, self._acce_ax, self._gyro_ax, self._color_ax]:
            ax.cla()

    def _redraw_all(self):
        self._redraw_axes()
        self._redraw_gauges()
        self._redraw_colors()

    def _redraw_axes(self):
        self._setup_axes()

        self._prox_ax.plot(self._xs, self._sensor_data['Proximity'], 'o-')
        self._temp_ax.plot(self._xs, self._sensor_data['Temperature'], 'o-')
        self._barom_ax.plot(self._xs, self._sensor_data['Barometric Pressure'], 'o-')
        self._altitude_ax.plot(self._xs, self._sensor_data['Altitude'], 'o-')

        for ax, key in [(self._magnetic_ax, 'Magnetic'), (self._acce_ax, 'Acceleration'), (self._gyro_ax, 'Gyro')]:
            for axis in ['x', 'y', 'z']:
                ax.plot(self._xs, self._sensor_data[key][axis], 'o-', label=axis)
            ax.legend()

    def _redraw_gauges(self):
        gauge = pygal.SolidGauge(inner_radius=0.70, half_pie=True, show_legend=True, style=CUSTOM_STYLE)

        gauge.add(title='Sound',
                  values=[{'label': 'Sound', 'value': self._sound_data, 'max_value': 100, 'color': 'pink'}],
                  formatter=lambda x: f'{x} dB')

        gauge.add(title='Humidity',
                  values=[{'label': 'Humidity', 'value': self._humidity_data, 'max_value': 100, 'color': 'green'}],
                  formatter=lambda x: '{:.10g}%'.format(x))

        svg_data = gauge.render()
        modified_svg = re.sub('font-size:\d+px', 'font-size:20px', svg_data.decode('utf-8'))

        # Convert modified SVG to PNG
        png_image = svg2png(bytestring=modified_svg)
        image = Image.open(BytesIO(png_image))
        self._gauges_ax.imshow(np.array(image), aspect='auto')
        self._gauges_ax.axis('off')  # Hide axis

    def _redraw_colors(self):
        self._color_ax.cla()
        self._color_ax.axis('off')

        max_intensity = max(self._color_data.values()) if max(self._color_data.values()) > 0 else 1
        normalized_color_data = {k: v / max_intensity for k, v in self._color_data.items()}

        positions = [(1, 1), (3, 1), (1, 3), (3, 3)]
        size = 2000

        def get_rgb_color(color_name):
            return {
                'Red': (1, 0, 0),
                'Green': (0, 1, 0),
                'Blue': (0, 0, 1),
                'Clear': (0.9, 0.9, 0.9)
            }.get(color_name, (0, 0, 0))

        for pos, (color, intensity) in zip(positions, normalized_color_data.items()):
            rgb_color = get_rgb_color(color)
            circle = plt.Circle(pos, 0.5, color=rgb_color, alpha=intensity)
            self._color_ax.add_patch(circle)
            self._color_ax.text(pos[0], pos[1], f'{color}\n{intensity:.2f}', horizontalalignment='center',
                                verticalalignment='center')

        self._color_ax.set_xlim(0, 4)
        self._color_ax.set_ylim(0, 4)
        self._color_ax.set_aspect('equal')
        self._color_ax.axis('off')

    def update_data(self, new_data):
        self.append_sensor_data(json.loads(new_data))
        self._update_plot()


class ExJSONService(AbstractService):
    uuid = VendorUUID("51ad213f-e568-4e35-84e4-67af89c79ef0")
    data = JSONCharacteristic(
        uuid=VendorUUID("528ff74b-fdb8-444c-9c64-3dd5da4135ae"),
        properties=Characteristic.READ,
        initial_value={
            "Sensors": {
                "Proximity": f"{0:.2f}",
                "Temperature": f"{0:.2f} C",
                "Barometric_pressure": f"{0:.2f}",
                "Altitude": f"{0:.2f} m",
                "Color": {
                    "Red": f"{0:.2f}",
                    "Green": f"{0:.2f}",
                    "Blue": f"{0:.2f}",
                    "Clear": f"{0:.2f}"
                },
                "Sound_level": f"{0:.2f}",
                "Magnetic": {
                    "x": f"{0:.2f}",
                    "y": f"{0:.2f}",
                    "z": f"{0:.2f}"
                },
                "Acceleration": {
                    "x": f"{0:.2f}",
                    "y": f"{0:.2f}",
                    "z": f"{0:.2f}"
                },
                "Gyro": {
                    "x": f"{0:.2f}",
                    "y": f"{0:.2f}",
                    "z": f"{0:.2f}"
                },
                "Humidity": f"{0:.2f} %",
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
