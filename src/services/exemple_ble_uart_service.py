from src.services.service import AbstractService, ServiceTab
from adafruit_ble.services.nordic import UARTService
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UARTServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._title = 'Inclination Data (IncZ)'
        self._fig = Figure(figsize=(10, 10), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._setup_axis()
        self._canvas = FigureCanvasTkAgg(self._fig, master=master)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._xs = []
        self._ys_Inc_z = []
        self._data_count = 0

    def _setup_axis(self):
        """ Setup and update axis properties based on current title and limits. """
        self._ax.set_title(self._title)
        self._ax.set_xlabel('Time')
        self._ax.set_ylabel('Values')
        self._ax.set_ylim(0, 90)
        self._ax.grid(True)

    def update_data(self, data):
        # Split the incoming data into lines and convert each to float
        values = str(data.decode('utf-8')).strip().split('\n')
        new_values = [float(value) for value in values if value]

        # Update the xs and ys_Inc_z lists with new data
        self._xs.extend(range(len(self._xs), len(self._xs) + len(new_values)))
        self._ys_Inc_z.extend(new_values)

        # Adjust x-axis to show the latest 100 data points
        min_x = max(0, self._xs[-1] - 100) if len(self._xs) > 100 else 0
        max_x = self._xs[-1] + 1 if len(self._xs) > 100 else 100

        # Efficiently update the plot
        self._ax.clear()
        self._setup_axis()  # Reapply axis settings
        self._ax.plot(self._xs, self._ys_Inc_z, 'o-', label='Inclination Z', color='red')
        self._ax.legend()
        self._ax.set_xlim(left=min_x, right=max_x)

        self._canvas.draw()


class UartService(UARTService, AbstractService):
    def __init__(self, service=None):
        UARTService.__init__(self, service=service)
        AbstractService.__init__(self, service=service)

    def read(self):
        return UARTService.read(self)

    def write(self):
        return UARTService.write(self)

    def get_service_tab(self, master) -> ServiceTab:
        return UARTServiceTab(master=master)
