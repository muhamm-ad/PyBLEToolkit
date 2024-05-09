from adafruit_ble.uuid import VendorUUID
from adafruit_ble.characteristics import Characteristic
from adafruit_ble.characteristics.json import JSONCharacteristic
from src.services.service import AbstractService, ServiceTab
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class JSONServiceTab(ServiceTab):
    COLUMNS = 11

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._title1 = 'Rotation Data (Rx, Ry)'
        self._title2 = 'Inclination Data (IncZ)'
        self.segment_colors = {  # Colors mapping based on segment, can be customized further
            "( 0, 0)": "black",
            "( 0, Y)": "green",
            "( X, 0)": "blue",
            "(-X, Y)": "purple",
            "( X,-Y)": "yellow",
            "(-X,-Y)": "pink",
            "( X, Y)": "orange",
            "(-X, 0)": "cyan",
            "( 0,-Y)": "magenta"
        }

        # Setup the figure and subplots
        self._fig = Figure(figsize=(10, 10), dpi=100)
        self._ax1 = self._fig.add_subplot(211)  # First subplot for Rx and Ry
        self._ax2 = self._fig.add_subplot(212)  # Second subplot for IncZ

        # Initial setup for axes
        self._setup_axes(self._ax1, self._title1, -1, 362)
        self._setup_axes(self._ax2, self._title2, -1, 92)
        self._setup_static_legend()

        self._canvas = FigureCanvasTkAgg(self._fig, master=master)
        self._canvas.draw()

        self._xs = []
        self._ys_Rx = []
        self._ys_Ry = []
        self._ys_Inc_z = []

        self._ys_Inc_z_segments = []  # Setup additional properties to store segment data
        self._data_count = 0

        self._canvas.get_tk_widget().grid(**kwargs)

    def _setup_axes(self, ax, title, min_y, max_y):
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Values')
        ax.set_ylim(min_y, max_y)
        ax.grid(True)

    def _setup_static_legend(self):
        """ Setup a static legend for the IncZ plot with predefined colors for each segment. """
        for segment, color in self.segment_colors.items():
            self._ax2.plot([], [], 'o', label=segment,
                           color=color)  # Plot empty lists with the specified color and label
        self._ax2.legend()

    def _update_subplot(self, ax, xs, y_arrays, labels, colors, min_x, max_x, title):
        ax.clear()
        for y, label, color in zip(y_arrays, labels, colors):
            ax.plot(xs, y, 'o-', label=label, color=color)
        ax.legend()
        ax.grid(True)
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Values')
        ax.set_xlim(left=min_x, right=max_x)

    def _update_inc_z_subplot(self, ax, xs, ys, segments, min_x, max_x, title):
        ax.clear()
        self._setup_static_legend()  # Ensure the legend is always correct

        # Plot the line in black
        ax.plot(xs, ys, 'k-', label='Inclination Z')  # 'k-' for black line

        # Plot each point individually with its corresponding segment color
        for x, y, segment in zip(xs, ys, segments):
            color = self.segment_colors.get(segment, "gray")  # Default to 'gray' if segment not recognized
            ax.plot(x, y, 'o', color=color)  # Only the markers change color

        ax.grid(True)
        ax.set_title(title)
        ax.set_xlabel('Time')
        ax.set_ylabel('Values')
        ax.set_xlim(left=min_x, right=max_x)

    def update_data(self, data):
        self._data_count += 1

        val_Rx = float(data['Rotations']['values']['x'])
        val_Ry = float(data['Rotations']['values']['y'])
        val_inc_z = float(data['Inclination']['values']['Z']['inc'])
        str_inc_segment = data['Inclination']['values']['Z']['segment']

        # Append new data points and corresponding segment
        self._xs.append(self._data_count)
        self._ys_Rx.append(val_Rx)
        self._ys_Ry.append(val_Ry)
        self._ys_Inc_z.append(val_inc_z)
        self._ys_Inc_z_segments.append(str_inc_segment)

        # Adjust x-axis to show the latest 100 data points
        min_x = max(0, self._xs[-1] - 100) if len(self._xs) > 100 else 0
        max_x = self._xs[-1] + 1 if len(self._xs) > 100 else 100

        self._update_subplot(self._ax1, self._xs, [self._ys_Rx, self._ys_Ry], ['Rotation X', 'Rotation Y'],
                             ['blue', 'green'], min_x, max_x, self._title1)
        self._update_inc_z_subplot(self._ax2, self._xs, self._ys_Inc_z, self._ys_Inc_z_segments, min_x, max_x,
                                   self._title2)

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
            'Rotations': {
                'References': {
                    'x': f"{value:.2f}",
                    'y': f"{value:.2f}",
                },
                'values': {
                    'x': f"{value:.2f}",
                    'y': f"{value:.2f}"
                }
            },
            'Inclination': {
                'References': {
                    'z/xy': f"{value:.2f}"
                },
                'values': {
                    'Z': {
                        'inc': f"{value:.2f}",
                        'segment': segment_inc_z
                    }
                }
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

    def get_service_tab(self, master) -> ServiceTab:
        return JSONServiceTab(master=master)
