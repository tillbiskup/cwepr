"""Module containing data plotters for different applications.
"""

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
    message : :class:`str`
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
    coeffs: :class:'list'
    List containing any number of other lists each containing
    a set of polynomial coefficients for a polynomial that might
    be used for the baseline correction. The order of the coefficients
    is considered to highest to lowest as returned by :meth: numpy.polyfit.

    data: :class:'numpy.array'
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
            ppl.plot(x, np.polyval(np.poly1d(coeffs), x),
                     label=str(len(coeffs)-1))

        ppl.legend()
        ppl.show()


class SimpleSpectrumPlotter(aspecd.plotting.SinglePlotter):
    """Simple but highly customizable plotter for a single spectrum.

    Attributes
    ----------
    settings: :class:'dict'
        Values used for customization.
    """
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
        color: :class:'str' or RGBA tuple
            The color to use.
        """
        self.settings["color"] = color

    def set_title(self, title):
        """Sets the title of the plot.

        Parameters
        ----------
        title: :class:'str'
            The title to use.
        """
        self.settings["title"] = title

    def set_x_axis_name(self, name):
        """Sets the label of the x axis.

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["x_name"] = name

    def set_y_axis_name(self, name):
        """Sets the label of the y axis.

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["y_name"] = name

    def set_curve_name(self, name):
        """Sets the label of the main (derivative) curve
        in the legend..

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["curve_name"] = name

    def set_draw_zeroline(self, do_draw):
        """Set whether the zero line should be drawn.

        Parameters
        ----------
        do_draw: :class:'bool'
            Should the zero line be drawn?
        """
        self.settings["draw_zero"] = do_draw

    def set_zeroline_thickness(self, thickness):
        """Sets thickness of the zero line.

        Parameters
        ----------
        thickness: :class:'float'
            Thickness of the zero line; default: 0.5
        """
        self.settings["zero_thickness"] = thickness

    def set_zeroline_color(self, color):
        """Sets the color of the zero line.

        Parameters
        ----------
        color: :class:'str' or RGBA tuple
            The color to use.
        """
        self.settings["zero_color"] = color

    def set_fit_axis_to_spectrum(self, do_fit):
        """Whether the x axis limits should be fitted to width of the spectrum.

        Parameters
        ----------
        do_fit: :class:'bool'
            Should the width of the plot fit the width of the curve?
        """
        self.settings["fit_axis"] = do_fit

    def set_x_axis_limits(self, left, right):
        """Sets the limits of the x axis.

        Note: Using None as a limit will leave the respective limit unchanged.

        Parameters
        ----------
        left: :class:'float'
            Left limit in units of the x axis.
        right: :class:'float'
            Right limit in units of the x axis.
        """
        self.settings["limit_left"] = left
        self.settings["limit_right"] = right

    def _create_plot(self):
        """Draw and display the plot.

        The plot settings are put into the parameter attribute.
        """
        x = self.dataset.data.data[0, :]
        y = self.dataset.data.data[1, :]
        self._make_labels()
        self._plot_lines(x, y)
        self._make_axis_limits(x)
        ppl.legend()
        self.parameters["settings"] = self.settings
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
        x: :class:'list'
            x values for plotting
        y: :class:'list'
            y values for plotting
        """
        if self.settings["draw_zero"]:
            ppl.plot(x, 0*x, lw=self.settings["zero_thickness"],
                     color=self.settings["zero_color"])
        ppl.plot(x, y, label=self.settings["curve_name"],
                 color=self.settings["color"])

    def _make_axis_limits(self, x):
        """Set the limits of the x axis.

        The limits are first fitted to the width of the spectrum
        (if necessary),then overridden with user specified values
        (if applicable).

        Parameters
        ----------
        x: :class:'list'
            x values to plot. These are necessary for determining the
            correct limits.
        """
        if self.settings["fit_axis"]:
            self.axes.set_xlim(x[0], x[-1])
        self.axes.set_xlim(self.settings["limit_left"],
                           self.settings["limit_right"])


class SpectrumAndIntegralPlotter(SimpleSpectrumPlotter):
    """Plotter used for plotting a derivative spectrum as well as
    the first and / or second integral curve.

    Either integral curve can be omitted but NOT BOTH.

    Attributes
    ----------
    integral_1: :class:'list'
        y values of the first integration
    integral_2: :class:'list'
        y values of the second integration

    Raises
    ------
    NoIntegralDataProvidedError
        Raised when data for both integration is omitted.
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
        color: :class:'str' or RGBA tuple
            The color to use.
        """
        self.settings["integral1_color"] = color

    def set_integral1_name(self, name):
        """Sets the label of the first integral curve
        in the legend.

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["integral1_name"] = name

    def set_integral2_color(self, color):
        """Sets the color of the second integral curve.

        Parameters
        ----------
        color: :class:'str' or RGBA tuple
            The color to use.
        """
        self.settings["integral2_color"] = color

    def set_integral2_name(self, name):
        """Sets the label of the second integral curve
        in the legend.

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["integral2_name"] = name

    def _plot_lines(self, x, y):
        """Draw the spectrum curve and the zero line (if necessary).
        Additionally draw one or both integral curves. Either one of the
        integral curves can be omitted but NOT BOTH.

        Parameters
        ----------
        x: :class:'list'
            x values for plotting
        y: :class:'list'
            y values for plotting

        Raises
        ------
        NoIntegralDataProvidedError
            Raised when data for both integrations is omitted.
        """
        if self.settings["draw_zero"]:
            ppl.plot(x, 0*x, lw=self.settings["zero_thickness"],
                     color=self.settings["zero_color"])
        ppl.plot(x, y, label=self.settings["curve_name"],
                 color=self.settings["color"])
        if (self.parameters["integral_1"] is None and
                self.parameters["integral_2"] is None):
            raise NoIntegralDataProvidedError(""""Neither first nor second 
integration data points have been provided for integral plotting.""")
        if self.parameters["integral_1"] is not None:
            ppl.plot(x, self.parameters["integral_1"],
                     label=self.settings["integral1_name"],
                     color=self.settings["integral1_color"])
        if self.parameters["integral_2"] is not None:
            ppl.plot(x, self.parameters["integral_2"],
                     label=self.settings["integral2_name"],
                     color=self.settings["integral2_color"])


class Multiplotter(aspecd.plotting.MultiPlotter):
    """Plotter used for plotting multiple spectra at the same time.

    Attributes
    ----------
    datasets: :class:'list'
        List of datasets to plot.
    integrals: :class:'list'
        List of the numeric of the integrals to be indicated in the legend.
        Can be omitted.
    """
    def __init__(self, datasets, integrals=None):
        super().__init__()
        self.description = "Plotter for multiple cwepr datasets."
        self.datasets = datasets
        self.integrals = integrals
        if self.integrals is None:
            self.integrals = list()
        self.settings = dict()
        self._set_defaults()

    def _set_defaults(self):
        """Create default values for all settings of the plot."""
        self.set_title("Spectrum")
        self.set_x_axis_name("Field")
        self.set_y_axis_name("Intensity Change")
        self.set_draw_zeroline(True)
        self.set_zeroline_thickness(0.5)
        self.set_zeroline_color("black")
        self.set_fit_axis_to_spectrum(True)
        color_library = ["tab:blue", "tab:red", "tab:green", "tab:cyan",
                         "tab:magenta", "tab:yellow"]
        self.set_curve_colors(color_library[:len(self.datasets)])
        curve_names = list()
        for n in range(len(self.datasets)):
            name = "Curve " + str(n)
            curve_names.append(name)
        self.set_curve_names(curve_names)
        self.set_show_integrals(True)

    def set_curve_names(self, names):
        """Sets the names for the different curves.

        Parameters
        ----------
        names: :class:'list'
            List of 'str' containing the names.
        """
        self.settings["names"] = names

    def set_curve_colors(self, colors):
        """Sets the colors for the different curves.

        Parameters
        ----------
        colors: :class:'list'
            List of 'str' and or RGBA containing the colors.
        """
        self.settings["colors"] = colors

    def set_title(self, title):
        """Sets the title of the plot.

        Parameters
        ----------
        title: :class:'str'
            The title to use.
        """
        self.settings["title"] = title

    def set_x_axis_name(self, name):
        """Sets the label of the x axis.

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["x_name"] = name

    def set_y_axis_name(self, name):
        """Sets the label of the y axis.

        Parameters
        ----------
        name: :class:'str'
            The name to use.
        """
        self.settings["y_name"] = name

    def set_draw_zeroline(self, do_draw):
        """Set whether the zero line should be drawn.

        Parameters
        ----------
        do_draw: :class:'bool'
            Should the zero line be drawn?
        """
        self.settings["draw_zero"] = do_draw

    def set_zeroline_thickness(self, thickness):
        """Sets thickness of the zero line.

        Parameters
        ----------
        thickness: :class:'float'
            Thickness of the zero line; default: 0.5
        """
        self.settings["zero_thickness"] = thickness

    def set_zeroline_color(self, color):
        """Sets the color of the zero line.

        Parameters
        ----------
        color: :class:'str' or RGBA tuple
            The color to use.
        """
        self.settings["zero_color"] = color

    def set_fit_axis_to_spectrum(self, do_fit):
        """Whether the x axis limits should be fitted to the width of the
        spectrum.

        Parameters
        ----------
        do_fit: :class:'bool'
            Should the width of the plot fit the width of the curve?
        """
        self.settings["fit_axis"] = do_fit

    def set_show_integrals(self, do_show):
        """Whether the integrals should be shown in the legend if provided.

        Parameters
        ----------
        do_show: :class:'bool'
            Should the integrals be indicated?
        """
        self.settings["show_integrals"] = do_show

    def _create_plot(self):
        """Draw and display the plot."""
        x_axes = list()
        self._make_labels()
        for n in range(len(self.datasets)):
            x = self.datasets[n].data.data[0, :]
            y = self.datasets[n].data.data[1, :]
            x_axes.append(x)
            self._plot_lines(x, y, n)
        x_axis_limits = self.get_x_axis_limits(x_axes)
        if self.settings["draw_zero"]:
            zeroline_values = np.linspace(x_axis_limits[0],
                                          x_axis_limits[1], num=1500)
            ppl.plot(zeroline_values, 0*zeroline_values,
                     lw=self.settings["zero_thickness"],
                     color=self.settings["zero_color"])
        self._make_axis_limits(x_axis_limits)
        ppl.legend()
        ppl.show()

    @staticmethod
    def get_x_axis_limits(x_axes):
        """Determined the x axis limits using the lowest starting point and
        hightest end point.
        """
        minimum = None
        maximum = None
        for axis in x_axes:
            if minimum is None or axis[0] < minimum:
                minimum = axis[0]
            if maximum is None or axis[-1] < maximum:
                maximum = axis[-1]
        return [minimum, maximum]

    def _make_labels(self):
        """Create the title as well as the labels for the axes."""
        ppl.title(self.settings["title"])
        ppl.xlabel(self.settings["x_name"])
        ppl.ylabel(self.settings["y_name"])

    def _plot_lines(self, x, y, n):
        """Draw the spectrum curve.

        Parameters
        ----------
        x: :class:'list'
            x values for plotting
        y: :class:'list'
            y values for plotting
        """
        curve_name = self.settings["names"][n]
        if len(self.integrals) > 0 and self.settings["show_integrals"]:
            curve_name += "; Integral: "
            curve_name += str(round(self.integrals[n], 6))
        ppl.plot(x, y, label=curve_name, color=self.settings["colors"][n])

    def _make_axis_limits(self, x):
        """Set the limits of the x axis.

        Parameters
        ----------
        x: :class:'list'
            x values to plot. These are necessary for determining the
            correct limits.
        """
        if self.settings["fit_axis"]:
            self.axes.set_xlim(x[0], x[1])
