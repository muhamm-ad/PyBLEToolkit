from src.service_tab import ServiceTab
from .ble_uart_service import UARTService
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

MAX_DATA_POINTS = 100


class PlotterServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self._fig = Figure(dpi=100)

        # Initialize data storage
        self._xs = []
        self._ys = []

        self._ax = self._fig.add_subplot(111)
        self._setup_axis()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create a canvas
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.draw()
        self._canvas.get_tk_widget().grid(row=0, column=0, columnspan=4, sticky="nsew")

        self._create_buttons()
        self._create_scale()

        self._fig.set_tight_layout(True)

        self._plot = True
        self.stop_plotting()

    def _create_buttons(self):
        button_frame = ctk.CTkFrame(master=self)
        button_frame.grid(row=1, column=0, columnspan=4, sticky="ew")

        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.start_button = ctk.CTkButton(master=button_frame, text="Start", command=self.start_plotting)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.stop_button = ctk.CTkButton(master=button_frame, text="Stop", command=self.stop_plotting)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.clear_button = ctk.CTkButton(master=button_frame, text="Clear", command=self.clear_plot)
        self.clear_button.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.exit_button = ctk.CTkButton(master=button_frame, text="Exit", command=self.exit_plot())
        self.exit_button.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

    def _create_scale(self):
        self.scale_frame = ctk.CTkFrame(master=self)
        self.scale_frame.grid_columnconfigure(0, weight=1)
        self.scale_frame.grid_rowconfigure(0, weight=1)

        self.range_label = ctk.CTkLabel(master=self.scale_frame, text="X-axis Range:")
        self.range_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.range_scale = ctk.CTkSlider(master=self.scale_frame, from_=10, to=MAX_DATA_POINTS)
        self.range_scale.set(MAX_DATA_POINTS)
        self.range_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.scale_frame.grid(row=2, column=0, columnspan=4, sticky="ew")

    def _setup_axis(self):
        self._ax.set_xlabel('Time')
        self._ax.set_ylabel('Values')
        self._ax.grid(True)

    def start_plotting(self):
        self._plot = True
        self.start_button.configure(state=ctk.DISABLED)
        self.stop_button.configure(state=ctk.NORMAL)

    def stop_plotting(self):
        self._plot = False
        self.start_button.configure(state=ctk.NORMAL)
        self.stop_button.configure(state=ctk.DISABLED)

    def exit_plot(self):
        # TODO
        pass

    def clear_plot(self):
        self._xs.clear()
        self._ys.clear()
        self._ax.clear()
        self._setup_axis()
        self._canvas.draw()

    def update_data(self, data):
        if self._plot:
            # Split the incoming data into lines and convert each to float
            values = str(data.decode('utf-8')).strip().split('\n')
            new_values = [float(value) for value in values if value]

            # Update the xs and ys lists with new data
            self._xs.extend(range(len(self._xs), len(self._xs) + len(new_values)))
            self._ys.extend(new_values)

            # Keep only the latest MAX_DATA_POINTS elements
            # self._xs = self._xs[-MAX_DATA_POINTS:]
            # self._ys = self._ys[-MAX_DATA_POINTS:]

            # Adjust x-axis range based on the scale value
            x_range = self.range_scale.get()
            min_x = max(0, self._xs[-1] - x_range) if len(self._xs) > x_range else 0
            max_x = self._xs[-1] + 1 if len(self._xs) > x_range else x_range

            # Efficiently update the plot
            self._ax.clear()
            self._setup_axis()
            self._ax.plot(self._xs, self._ys, color='red')
            self._ax.set_xlim(left=min_x, right=max_x)
            self._canvas.draw()


class PlotterService(UARTService):
    def __init__(self, service=None):
        super().__init__(service)
