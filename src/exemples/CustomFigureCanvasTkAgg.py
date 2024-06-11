from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CustomFigureCanvasTkAgg(FigureCanvasTkAgg):
    def winfo_exists(self):
        # This method should return whether the Tkinter widget exists.
        try:
            return bool(self.tk)
        except AttributeError:
            return False
