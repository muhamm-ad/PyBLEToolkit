from src.service import AbstractService
from src.service_tab import ServiceTab
from adafruit_ble.services.nordic import UARTService as NordicUARTService
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class UARTServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._title = 'Temperature'
        self._fig = Figure(figsize=(20, 20), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._fig, master=master)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self._xs = []
        self._ys = []

    def _setup_axis(self):
        self._ax.set_title(self._title)
        self._ax.set_xlabel('Time')
        self._ax.set_ylabel('Values')
        self._ax.set_ylim(0, 90)
        self._ax.grid(True)

    def update_data(self, data):
        # Split the incoming data into lines and convert each to float
        values = str(data.decode('utf-8')).strip().split('\n')
        new_values = [float(value) for value in values if value]

        # Update the xs and ys lists with new data
        self._xs.extend(range(len(self._xs), len(self._xs) + len(new_values)))
        self._ys.extend(new_values)

        # Adjust x-axis to show the latest 30 data points
        min_x = max(0, self._xs[-1] - 30) if len(self._xs) > 30 else 0
        max_x = self._xs[-1] + 1 if len(self._xs) > 30 else 30

        # Efficiently update the plot
        self._ax.clear()
        self._setup_axis()  # Reapply axis settings
        self._ax.plot(self._xs, self._ys, 'o-', label='Temperature', color='red')
        self._ax.legend()
        self._ax.set_xlim(left=min_x, right=max_x)

        self._canvas.draw()


class UARTService(NordicUARTService, AbstractService):
    def __init__(self, service=None):
        NordicUARTService.__init__(self, service=service)
        AbstractService.__init__(self, service=service)
