import numpy as np
import matplotlib.pyplot as ppl

import aspecd


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class NoIntegralDataProvidedError(Error):
    """Exception raised when a spectrum with integration should be
    plotted but no data for the integral is provided.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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
    """Simple but highly customizable plotter for a single spectrum.

    Attributes
    ----------
    Settings: 'dict'
    Values used for customization."""
    def __init__(self):
        super().__init__()
        self.settings = dict()
        self._set_defaults()

    def _set_defaults(self):
        """Create default values for all settings of the plot."""
        self.set_color("tab:blue")
        self.set_title("Spectrum")
        self.set_x_axis_name("Field")
        self.set_y_axis_name("Intensity Change")
        self.set_curve_name("Derivative Spectrum")
        self.set_draw_zeroline(True)
        self.set_zeroline_thickness(0.5)
        self.set_zeroline_color("black")
        self.set_fit_axis_to_spectrum(True)
        self.set_x_axis_limits(None, None)

    def set_color(self, color):
        """Sets the color of the main (derivative) curve.

        Parameters
        ----------
        color: 'str' or RGBA tuple
        The color to use.
        """
        self.settings["color"] = color

    def set_title(self, title):
        """Sets the title of the plot.

        Parameters
        ----------
        title: 'str'
        The title to use.
        """
        self.settings["title"] = title

    def set_x_axis_name(self, name):
        """Sets the label of the x axis.

        Parameters
        ----------
        name: 'str'
        The name to use.
        """
        self.settings["x_name"] = name

    def set_y_axis_name(self, name):
        """Sets the label of the y axis.

        Parameters
        ----------
        name: 'str'
        The name to use.
        """
        self.settings["y_name"] = name

    def set_curve_name(self, name):
        """Sets the label of the main (derivative) curve
        in the legend..

        Parameters
        ----------
        name: 'str'
        The name to use.
        """
        self.settings["curve_name"] = name

    def set_draw_zeroline(self, do_draw):
        """Set whether the zero line should be drawn.

        Parameters
        ----------
        name: 'bool'
        """
        self.settings["draw_zero"] = do_draw

    def set_zeroline_thickness(self, thickness):
        """Sets thickness of the zero line.

        Parameters
        ----------
        name: 'float'
        Thickness of the zero line; default: 0.5
        """
        self.settings["zero_thickness"] = thickness

    def set_zeroline_color(self, color):
        """Sets the color of the zero line.

        Parameters
        ----------
        color: 'str' or RGBA tuple
        The color to use.
        """
        self.settings["zero_color"] = color

    def set_fit_axis_to_spectrum(self, do_fit):
        """Whether the x axis limits should be fitted to width of the spectrum.

        Parameters
        ----------
        name: 'bool'
        """
        self.settings["fit_axis"] = do_fit

    def set_x_axis_limits(self, left, right):
        """Sets the limits of the x axis.

        Note: Using None as a limit will leave the respective limit unchanged.

        Parameters
        ----------
        left: 'float'
        Left limit in units of the x axis.
        right: 'float'
        Right limit in units of the x axis.
        """
        self.settings["limit_left"] = left
        self.settings["limit_right"] = right

    def _create_plot(self):
        """Draw and display the plot."""
        x = self.dataset.data.data[0, :]
        y = self.dataset.data.data[1, :]
        self._make_labels()
        self._plot_lines(x, y)
        self._make_axis_limits(x)
        ppl.legend()
        ppl.show()

    def _make_labels(self):
        """Create the title as well as the labels for the axes."""
        ppl.title(self.settings["title"])
        ppl.xlabel(self.settings["x_name"])
        ppl.ylabel(self.settings["y_name"])

    def _plot_lines(self, x, y):
        """Draw the spectrum curve and the zero line (if necessary).

        Parameters
        ----------
        x: 'list'
        x values for plotting
        y: 'list'
        y values for plotting
        """
        if self.settings["draw_zero"]:
            ppl.plot(x, 0*x, lw=self.settings["zero_thickness"], color=self.settings["zero_color"])
        ppl.plot(x, y, label=self.settings["curve_name"], color=self.settings["color"])

    def _make_axis_limits(self, x):
        """Set the limits of the x axis.

        The limits are first fitted to the width of the spectrum (if necessary),
        then override with user specified values if applicable.

        Parameters
        ----------
        x: 'list'
        x values to plot. These are necessary for determining the correct limits.
        """
        if self.settings["fit_axis"]:
            self.axes.set_xlim(x[0], x[-1])
        self.axes.set_xlim(self.settings["limit_left"], self.settings["limit_right"])


class SpectrumAndIntegralPlotter(SimpleSpectrumPlotter):
    """Plotter used for plotting a derivative spectrum as well as
    the first and / or second integral curve.

    Either integral curve can be omitted but not both.

    Attributes
    ----------
    integral_1: 'list'
    y values of the first integration
    intefral_2: 'list'
    y values of the second integration

    Raises
    ------
    NoIntegralDataProvidedError: Raised when data for both integrations
    is omitted.
    """
    def __init__(self, integral_1=None, integral_2=None):
        super().__init__()
        self.parameters["integral_1"] = integral_1
        self.parameters["integral_2"] = integral_2

    def _set_defaults(self):
        """Set default settings as in the super class,
        plus additional settings for colors and names
        of the integral curves."""
        super()._set_defaults()
        self.set_integral1_name("First Integration")
        self.set_integral1_color("tab:red")
        self.set_integral2_name("Second Integration")
        self.set_integral2_color("tab:green")

    def set_integral1_color(self, color):
        """Sets the color of the first integral curve.

        Parameters
        ----------
        color: 'str' or RGBA tuple
        The color to use.
        """
        self.settings["integral1_color"] = color

    def set_integral1_name(self, name):
        """Sets the label of the first integral curve
        in the legend.

        Parameters
        ----------
        name: 'str'
        The name to use.
        """
        self.settings["integral1_name"] = name

    def set_integral2_color(self, color):
        """Sets the color of the second integral curve.

        Parameters
        ----------
        color: 'str' or RGBA tuple
        The color to use.
        """
        self.settings["integral2_color"] = color

    def set_integral2_name(self, name):
        """Sets the label of the second integral curve
        in the legend.

        Parameters
        ----------
        name: 'str'
        The name to use.
        """
        self.settings["integral2_name"] = name

    def _plot_lines(self, x, y):
        """Draw the spectrum curve and the zero line (if necessary).
        Additionally draw one or both integral curves. Either one of the
        integral curves can be omitted but not both.

        Parameters
        ----------
        x: 'list'
        x values for plotting
        y: 'list'
        y values for plotting

        Raises
        ------
        NoIntegralDataProvidedError: Raised when data for both integrations
        is omitted.
        """
        if self.settings["draw_zero"]:
            ppl.plot(x, 0*x, lw=self.settings["zero_thickness"], color=self.settings["zero_color"])
        ppl.plot(x, y, label=self.settings["curve_name"], color=self.settings["color"])
        if self.parameters["integral_1"] is None and self.parameters["integral_2"] is None:
            raise NoIntegralDataProvidedError("Neither first nor second integration data points have been provided for integral plotting.")
        if self.parameters["integral_1"] is not None:
            ppl.plot(x, self.parameters["integral_1"], label=self.settings["integral1_name"], color=self.settings["integral1_color"])
        if self.parameters["integral_2"] is not None:
            ppl.plot(x, self.parameters["integral_2"], label=self.settings["integral2_name"], color=self.settings["integral2_color"])
