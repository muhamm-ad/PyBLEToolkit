from src.service import AbstractService
from adafruit_ble.services.nordic import UARTService as NordicUARTService
from src.service_tab import ServiceTab
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

from src.utils import STD_PADDING

MAX_DATA_POINTS = 1000
TRANSPARENT_COLOR = "transparent"


class UARTPlotterTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=TRANSPARENT_COLOR, bg_color=TRANSPARENT_COLOR, **kwargs)

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

        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_button = ctk.CTkButton(master=button_frame, text="Start", command=self.start_plotting)
        self.start_button.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

        self.stop_button = ctk.CTkButton(master=button_frame, text="Stop", command=self.stop_plotting)
        self.stop_button.grid(row=0, column=1, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

        self.clear_button = ctk.CTkButton(master=button_frame, text="Clear", command=self.clear_plot)
        self.clear_button.grid(row=0, column=2, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

    def _create_scale(self):
        self.scale_frame = ctk.CTkFrame(master=self)
        self.scale_frame.grid_columnconfigure(0, weight=1)
        self.scale_frame.grid_columnconfigure(1, weight=2)
        self.scale_frame.grid_rowconfigure(0, weight=1)

        self.range_label = ctk.CTkLabel(master=self.scale_frame, text="X-axis Range:")
        self.range_label.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

        self.range_scale = ctk.CTkSlider(master=self.scale_frame, from_=10, to=MAX_DATA_POINTS)
        self.range_scale.set(100)
        self.range_scale.grid(row=0, column=1, columnspan=3, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

        self.scale_frame.grid(row=2, column=0, columnspan=5, sticky="nsew")

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


class UARTTerminalTab(ctk.CTkFrame):
    PLACE_HOLDER_MSG = "Type in a message to send"

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=TRANSPARENT_COLOR, bg_color=TRANSPARENT_COLOR, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self.view_mode = 'text'
        self.terminal_mode = False
        self.auto_scroll = True

        self._create_widgets()

    def _create_widgets(self):
        self._creat_option_widgets()
        self._create_rx_widgets()
        self._create_tx_widgets()

    def _creat_option_widgets(self):
        self.options_frame = ctk.CTkFrame(master=self)
        self.options_frame.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.options_frame.grid_rowconfigure(0, weight=1)
        self.clear_button = ctk.CTkButton(master=self.options_frame, text="Clear", command=self.clear_received)
        self.clear_button.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="nsw")
        self.view_mode_options = ctk.CTkOptionMenu(master=self.options_frame, values=["text", "hex"],
                                                   command=self.set_view_mode)
        self.view_mode_options.grid(row=0, column=1, padx=STD_PADDING, pady=STD_PADDING, sticky="nsw")
        self.terminal_mode_switch = ctk.CTkSwitch(master=self.options_frame, text="Terminal Mode",
                                                  command=self.toggle_terminal_mode)
        self.terminal_mode_switch.grid(row=0, column=2, padx=STD_PADDING, pady=STD_PADDING, sticky="nsw")
        self.auto_scroll_switch = ctk.CTkSwitch(master=self.options_frame, text="Auto Scroll",
                                                command=self.toggle_auto_scroll)
        self.auto_scroll_switch.grid(row=0, column=3, padx=STD_PADDING, pady=STD_PADDING, sticky="nsw")
        # Set initial state of switches
        if self.terminal_mode:
            self.terminal_mode_switch.select()
        else:
            self.terminal_mode_switch.deselect()
        if self.auto_scroll:
            self.auto_scroll_switch.select()
        else:
            self.auto_scroll_switch.deselect()

    def _create_rx_widgets(self):
        self.receiving_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        self.receiving_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        self.receiving_frame.grid_columnconfigure(0, weight=1)
        self.receiving_frame.grid_rowconfigure(0, weight=0)
        self.receiving_frame.grid_rowconfigure(1, weight=1)
        self.data_label = ctk.CTkLabel(master=self.receiving_frame, text="Received Data:")
        self.data_label.grid(row=0, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="w")
        self.data_display = ctk.CTkTextbox(master=self.receiving_frame, wrap="word", state="disabled")
        self.data_display.grid(row=1, column=0, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

    def _create_tx_widgets(self):
        self.sending_frame = ctk.CTkFrame(master=self, fg_color=TRANSPARENT_COLOR)
        self.sending_frame.grid(row=2, column=0, columnspan=4, sticky="nsew")
        self.sending_frame.grid_columnconfigure(0, weight=0)
        self.sending_frame.grid_columnconfigure(1, weight=1)
        self.sending_frame.grid_rowconfigure(0, weight=1)
        self.data_entry = ctk.CTkEntry(master=self.sending_frame, placeholder_text=self.PLACE_HOLDER_MSG)
        self.data_entry.grid(row=0, column=0, columnspan=3, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")
        self.send_button = ctk.CTkButton(master=self.sending_frame, text="Send", command=self.send_data)
        self.send_button.grid(row=0, column=3, padx=STD_PADDING, pady=STD_PADDING, sticky="nsew")

    def send_data(self):
        sending_msg = self.data_entry.get()
        # TODO: Implement sending data via UART
        self.data_display.configure(state="normal")
        self.data_display.insert(ctk.END, f"Sent: {sending_msg}\n")
        self.data_display.configure(state="disabled")
        self.data_entry.delete(0, ctk.END)
        self.data_entry.insert(0, self.PLACE_HOLDER_MSG)

    def clear_received(self):
        self.data_display.configure(state="normal")
        self.data_display.delete(1.0, ctk.END)
        self.data_display.configure(state="disabled")

    def set_view_mode(self, mode):
        self.view_mode = mode

    def toggle_terminal_mode(self):
        self.terminal_mode = self.terminal_mode_switch.get()
        # TODO: Implement terminal mode toggle logic

    def toggle_auto_scroll(self):
        self.auto_scroll = self.auto_scroll_switch.get()

    def update_data(self, data):
        if self.view_mode == 'hex':
            decoded_data = data.hex()
        else:
            decoded_data = data.decode('utf-8')

        self.data_display.configure(state="normal")
        self.data_display.insert(ctk.END, text=decoded_data)
        self.data_display.configure(state="disabled")

        if self.auto_scroll:
            self.data_display.see(ctk.END)


class UARTServiceTab(ServiceTab):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg_color="transparent", **kwargs)

        # create tabview
        self.tabview = ctk.CTkTabview(master=self, fg_color="transparent")
        self.tabview.add("Terminal")
        self.tabview.add("Plotter")
        self.tabview.tab("Terminal").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Terminal").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Plotter").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Plotter").grid_rowconfigure(0, weight=1)
        self.tabview.grid(row=0, column=0, sticky="nsew")

        self.terminal = UARTTerminalTab(master=self.tabview.tab("Terminal"))
        self.terminal.grid(row=0, column=0, sticky="nsew")
        self.plotter = UARTPlotterTab(master=self.tabview.tab("Plotter"))
        self.plotter.grid(row=0, column=0, sticky="nsew")

    def update_data(self, data):
        self.terminal.update_data(data)
        self.plotter.update_data(data)


class UARTService(NordicUARTService, AbstractService):
    def __init__(self, service=None):
        NordicUARTService.__init__(self, service=service)
        AbstractService.__init__(self, service=service)
