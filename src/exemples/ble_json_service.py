from src.service import AbstractService
from src.service_tab import ServiceTab
from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.json import JSONCharacteristic
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import numpy as np
from io import BytesIO
from PIL import Image
from cairosvg import svg2png
import re
import pygal
from pygal.style import Style

# Constants
MAX_DATA_POINTS = 10
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
        self._prox_data = {'xs': [], 'ys': []}
        self._temp_data = {'xs': [], 'ys': []}
        self._barom_data = {'xs': [], 'ys': []}
        self._altitude_data = {'xs': [], 'ys': []}
        self._color_data = {'Red': 0.0, 'Green': 0.0, 'Blue': 0.0, 'Clear': 0.0}
        self._magnetic_data = {'x': {'xs': [], 'ys': []}, 'y': {'xs': [], 'ys': []}, 'z': {'xs': [], 'ys': []}}
        self._acce_data = {'x': {'xs': [], 'ys': []}, 'y': {'xs': [], 'ys': []}, 'z': {'xs': [], 'ys': []}}
        self._gyro_data = {'x': {'xs': [], 'ys': []}, 'y': {'xs': [], 'ys': []}, 'z': {'xs': [], 'ys': []}}
        self._sound_data = 0
        self._humidity_data = 0
        self._data_count = 0

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
        self._data_count += 1

        self._append_data(self._prox_data, float(data['Sensors']['Proximity']))
        self._append_data(self._temp_data, float(data['Sensors']['Temperature'].replace(" C", "")))
        self._append_data(self._barom_data, float(data['Sensors']['Barometric_pressure']))
        self._append_data(self._altitude_data, float(data['Sensors']['Altitude'].replace(" m", "")))

        self._append_data(self._magnetic_data['x'], float(data['Sensors']['Magnetic']['x']))
        self._append_data(self._magnetic_data['y'], float(data['Sensors']['Magnetic']['y']))
        self._append_data(self._magnetic_data['z'], float(data['Sensors']['Magnetic']['z']))
        self._append_data(self._acce_data['x'], float(data['Sensors']['Acceleration']['x']))
        self._append_data(self._acce_data['y'], float(data['Sensors']['Acceleration']['y']))
        self._append_data(self._acce_data['z'], float(data['Sensors']['Acceleration']['z']))
        self._append_data(self._gyro_data['x'], float(data['Sensors']['Gyro']['x']))
        self._append_data(self._gyro_data['y'], float(data['Sensors']['Gyro']['y']))
        self._append_data(self._gyro_data['z'], float(data['Sensors']['Gyro']['z']))

        self._sound_data = float(data['Sensors']['Sound_level'])
        self._humidity_data = float(data['Sensors']['Humidity'].replace(" %", ""))

        self._color_data['Red'] = float(data['Sensors']['Color']['Red'])
        self._color_data['Green'] = float(data['Sensors']['Color']['Green'])
        self._color_data['Blue'] = float(data['Sensors']['Color']['Blue'])
        self._color_data['Clear'] = float(data['Sensors']['Color']['Clear'])

    def _append_data(self, data_dict, value):
        data_dict['ys'].append(value)
        data_dict['xs'].extend(range(self._data_count, self._data_count + 1))
        data_dict['xs'] = data_dict['xs'][-MAX_DATA_POINTS:]
        data_dict['ys'] = data_dict['ys'][-MAX_DATA_POINTS:]

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

        # Redraw each axis with new data
        self._redraw_axis(self._prox_ax, self._prox_data, "Proximity")
        self._redraw_axis(self._temp_ax, self._temp_data, "Temperature")
        self._redraw_axis(self._barom_ax, self._barom_data, "Barometric Pressure")
        self._redraw_axis(self._altitude_ax, self._altitude_data, "Altitude")

        self._redraw_multi_axis(self._magnetic_ax, self._magnetic_data, "Magnetic")
        self._redraw_multi_axis(self._acce_ax, self._acce_data, "Acceleration")
        self._redraw_multi_axis(self._gyro_ax, self._gyro_data, "Gyro")

    def _redraw_axis(self, ax, data, label):
        if data['ys']:
            ax.plot(data['xs'], data['ys'], 'o-', label=label)
            min_x = max(0, data['xs'][-1] - MAX_DATA_POINTS) if len(data['xs']) > MAX_DATA_POINTS else 0
            max_x = data['xs'][-1] + 1 if len(data['xs']) > MAX_DATA_POINTS else MAX_DATA_POINTS
            ax.set_xlim(left=min_x, right=max_x)
            ax.legend()

    def _redraw_multi_axis(self, ax, data, label):
        if data['x']['ys']:
            ax.plot(data['x']['xs'], data['x']['ys'], 'o-', label=f'{label} X')
            ax.plot(data['y']['xs'], data['y']['ys'], 'o-', label=f'{label} Y')
            ax.plot(data['z']['xs'], data['z']['ys'], 'o-', label=f'{label} Z')
            min_x = max(0, data['x']['xs'][-1] - MAX_DATA_POINTS) if len(data['x']['xs']) > MAX_DATA_POINTS else 0
            max_x = data['x']['xs'][-1] + 1 if len(data['x']['xs']) > MAX_DATA_POINTS else MAX_DATA_POINTS
            ax.set_xlim(left=min_x, right=max_x)
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
        # TODO: Implement color plot redraw logic
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
