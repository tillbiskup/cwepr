import numpy as np
import matplotlib.pyplot as ppl

import aspecd


class BaselineControlPlotter(aspecd.plotting.SinglePlotter):
    """Plotter to visualize the spectrum and a number of possible
    baseline correction polynomes.

    Attributes
    ----------
    coeffs_list: 'list'
    List containing any number of other lists each containing
    a set of polynomial coefficients for a polynomial that might
    be used for the baseline correction. The order of the coefficients
    is considered to highest to lowest as returned by numpy.polyfit.

    data: 'numpy.array'
    Array containing the x (field) and y (intensity) values of the
    spectrum that shall be visualized with the polynomials
    """
    def __init__(self, data, coeffs):
        super().__init__()
        self.parameters["coeffs_list"] = coeffs
        self.parameters["data"] = data

    def _create_plot(self):
        """Plots the spectrum as well as one curve for
        each set of polynomial coefficients provided.

        The polynomial are indicated in the legend by their order.

        The final diagram is displayed.
        """
        data = self.parameters["data"]
        coeffs_list = self.parameters["coeffs_list"]
        x = data[0, :]
        y = data[1, :]

        ppl.plot(x, y, label="Spectrum")
        for coeffs in coeffs_list:
            ppl.plot(x, np.polyval(np.poly1d(coeffs), x), label=str(len(coeffs)-1))

        ppl.legend()
        ppl.show()


class SimpleSpectrumPlotter(aspecd.plotting.SinglePlotter):
    def __init__(self, data):
        super().__init__()
        self.parameters["data"] = data
        self.settings = dict()
        self._set_defaults()

    def _set_defaults(self):
        self.set_color("tab:blue")
        self.set_title("Spectrum")
        self.set_x_axis_name("Field")
        self.set_y_axis_name("Intensity Change")
        self.set_curve_name("Spectrum Curve")

    def set_color(self, color):
        self.settings["color"] = color

    def set_title(self, title):
        self.settings["title"] = title

    def set_x_axis_name(self, name):
        self.settings["x_name"] = name

    def set_y_axis_name(self, name):
        self.settings["y_name"] = name

    def set_curve_name(self, name):
        self.settings["curve_name"] = name

    def _create_plot(self):
        data = self.parameters["data"]
        x = data[0, :]
        y = data[1, :]

        ppl.title(self.settings["title"])
        ppl.xlabel(self.settings["x_name"])
        ppl.ylabel(self.settings["y_name"])

        ppl.plot(x, y, label=self.settings["curve_name"], color=self.settings["color"])
        ppl.legend()
        ppl.show()
