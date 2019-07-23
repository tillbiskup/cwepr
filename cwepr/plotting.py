"""Module containing data plotters for different applications."""


import matplotlib.pyplot as plt
import numpy as np

import aspecd.plotting


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class NoIntegralDataProvidedError(Error):
    """Exception raised when integral data is missing.

    This happens when a spectrum with integration should be plotted but no data
    for the integral is provided.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class BaselineControlPlotter(aspecd.plotting.SinglePlotter):
    """Plotter to visualize possible baseline fits.

    Visualize the spectrum and a number of possible baseline correction
    polynomials.

    Attributes
    ----------
    coefficients: :class:`list`
        List containing any number of other lists each containing a set of
        polynomial coefficients for a polynomial that might be used for the
        baseline correction. The order of the coefficients is considered to
        highest to lowest as returned by :meth:`numpy.polyfit`.

    data: :class:`numpy.array`
        Array containing the x (field) and y (intensity) values of the
        spectrum that shall be visualized with the polynomials

    """

    def __init__(self, data, coefficients):
        super().__init__()
        self.parameters["coefficients"] = coefficients
        self.parameters["data"] = data

    def _create_plot(self):
        """Plot the spectrum and one or more baselines.

        Plots the spectrum as well as one curve for each set of polynomial
        coefficients provided. The polynomial are indicated in the legend by
        their order. The final diagram is displayed.
        """
        data = self.parameters["data"]
        coefficients_list = self.parameters["coefficients"]
        x_coordinates = data.axes[0].values
        y_coordinates = data.data

        plt.title("Baseline Comparison")
        plt.xlabel("$B_0$ / mT")
        plt.ylabel("$Intensity\\ Change and possible baselines$")

        plt.plot(x_coordinates, y_coordinates, label="Spectrum")
        for coefficients in coefficients_list:
            plt.plot(x_coordinates,
                     np.polyval(np.poly1d(coefficients), x_coordinates),
                     label=str(len(coefficients) - 1))

        plt.legend()
        plt.show()


class SimpleSpectrumPlotter(aspecd.plotting.SinglePlotter):
    """Simple but highly customizable plotter for a single spectrum."""

    def __init__(self):
        super().__init__()
        self._set_defaults()

    def _set_defaults(self):
        """Create default values for all settings of the plot."""
        self.parameters["color"] = "tab:blue"
        self.parameters["title"] = ""
        self.parameters["x_name"] = "Field"
        self.parameters["y_name"] = "Intensity"
        self.parameters["curve_name"] = "Derivative Spectrum"
        self.parameters["draw_zero"] = True
        self.parameters["zero_thickness"] = 0.5
        self.parameters["zero_color"] = "black"
        self.parameters["fit_axis"] = True
        # noinspection PyTypeChecker
        self.set_x_axis_limits(None, None)

    def set_x_axis_limits(self, left, right):
        """Sets the limits of the x axis.

        .. note::
            Using None as a limit will leave the respective limit unchanged.

        Parameters
        ----------
        left: :class:`float`
            Left limit in units of the x axis.

        right: :class:'float'
            Right limit in units of the x axis.

        """
        self.parameters["limit_left"] = left
        self.parameters["limit_right"] = right

    def _create_plot(self):
        """Draw and display the plot.

        The plot settings are put into the parameter attribute.
        """
        x_coordinates = self.dataset.data.axes[0].values
        y_coordinates = self.dataset.data.data
        self._make_labels_and_title()
        self._plot_lines(x_coordinates, y_coordinates)
        self._make_axis_limits(x_coordinates)
        plt.legend()

    def _make_labels_and_title(self):
        """Create the title as well as the labels for the axes."""
        plt.title(self.parameters["title"])

    def _plot_lines(self, x_coordinates, y_coordinates):
        """Draw the spectrum curve and the zero line (if necessary).

        Parameters
        ----------
        x_coordinates: :class:`list`
            x values for plotting

        y_coordinates: :class:`list`
            y values for plotting

        """
        if self.parameters["draw_zero"]:
            plt.plot(x_coordinates, 0 * x_coordinates,
                     lw=self.parameters["zero_thickness"],
                     color=self.parameters["zero_color"])
        plt.plot(x_coordinates, y_coordinates,
                 label=self.parameters["curve_name"],
                 color=self.parameters["color"])

    def _make_axis_limits(self, x_coordinates):
        """Set the limits of the x axis.

        The limits are first fitted to the width of the spectrum (if
        necessary),then overridden with user specified values (if applicable).

        Parameters
        ----------
        x_coordinates: :class:`list`
            x values to plot. These are necessary for determining the correct
            limits.

        """
        if self.parameters["fit_axis"]:
            self.axes.set_xlim(x_coordinates[0], x_coordinates[-1])
        self.axes.set_xlim(self.parameters["limit_left"],
                           self.parameters["limit_right"])


class SpectrumAndIntegralPlotter(SimpleSpectrumPlotter):
    """Plotter for a derivative spectrum including integrations.

    Plot derivative spectrum as well as the first and / or second integral
    curve. Either integral curve can be omitted but NOT BOTH.

    Attributes
    ----------
    integral_1: :class:`list`
        y values of the first integration

    integral_2: :class:`list`
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
        """Set default settingsl.

        Settings are applied as in the super class, plus additional settings
        for colors and names of the integral curves.
        """
        super()._set_defaults()
        self.parameters["integral1_name"] = "First Integration"
        self.parameters["integral1_color"] = "tab:red"
        self.parameters["integral2_name"] = "Second Integration"
        self.parameters["integral2_color"] = "tab:green"

    def _plot_lines(self, x_coordinates, y_coordinates):
        """Perform the actual plot for spectrum and integral(s).

        Draw the spectrum curve and the zero line (if necessary). Additionally
        draw one or both integral curves. Either one of the integral curves can
        be omitted but NOT BOTH.

        Parameters
        ----------
        x_coordinates: :class:`list`
            x values for plotting

        y_coordinates: :class:`list`
            y values for plotting

        Raises
        ------
        NoIntegralDataProvidedError
            Raised when data for both integrations is omitted.

        """
        if self.parameters["draw_zero"]:
            plt.plot(x_coordinates, 0 * x_coordinates,
                     lw=self.parameters["zero_thickness"],
                     color=self.parameters["zero_color"])
        plt.plot(x_coordinates, y_coordinates,
                 label=self.parameters["curve_name"],
                 color=self.parameters["color"])
        if (self.parameters["integral_1"] is None and
                self.parameters["integral_2"] is None):
            message = """Neither first nor second integration data points have 
            been provided for integral plotting."""
            raise NoIntegralDataProvidedError(message)
        if self.parameters["integral_1"] is not None:
            plt.plot(x_coordinates, self.parameters["integral_1"],
                     label=self.parameters["integral1_name"],
                     color=self.parameters["integral1_color"])
        if self.parameters["integral_2"] is not None:
            plt.plot(x_coordinates, self.parameters["integral_2"],
                     label=self.parameters["integral2_name"],
                     color=self.parameters["integral2_color"])


class MultiPlotter(aspecd.plotting.MultiPlotter):
    """Plotter used for plotting multiple spectra at the same time.

    Attributes
    ----------
    datasets: :class:`list`
        List of datasets to plot.

    integrals: :class:`list`
        List of the numeric of the integrals to be indicated in the legend.
        Can be omitted.

    """

    def __init__(self, datasets, integrals=None):
        super().__init__()
        self.description = "Plotter for multiple cwepr datasets."
        self.parameters["datasets"] = datasets
        self.integrals = integrals
        if self.integrals is None:
            self.integrals = list()
        self._set_defaults()

    def _set_defaults(self):
        """Create default values for all settings of the plot."""
        self.parameters["title"] = "Spectrum"
        self.parameters["x_name"] = "Field"
        self.parameters["y_name"] = "Intensity Change"
        self.parameters["draw_zero"] = True
        self.parameters["zero_thickness"] = 0.5
        self.parameters["zero_color"] = "black"
        self.parameters["fit_axis"] = True
        color_library = ["tab:blue", "tab:red", "tab:green", "tab:cyan",
                         "tab:magenta", "tab:yellow"]
        self.parameters["colors"] = \
            color_library[:len(self.parameters["datasets"])]
        curve_names = list()
        for curve_index in range(len(self.parameters["datasets"])):
            name = "Curve " + str(curve_index)
            curve_names.append(name)
        self.parameters["names"] = curve_names
        self.parameters["show_integrals"] = True

    def _create_plot(self):
        """Draw and display the plot."""
        x_axes = list()
        self._make_labels()
        for curve_index in range(len(self.parameters["datasets"])):
            x_coordinates = \
                self.parameters["datasets"][curve_index].data.axes[0].values
            y_coordinates = self.parameters["datasets"][curve_index].data.data
            x_axes.append(x_coordinates)
            self._plot_lines(x_coordinates, y_coordinates, curve_index)
        x_axis_limits = self._get_x_axis_limits(x_axes)
        if self.parameters["draw_zero"]:
            zeroline_values = np.linspace(x_axis_limits[0],
                                          x_axis_limits[1], num=1500)
            plt.plot(zeroline_values, 0 * zeroline_values,
                     lw=self.parameters["zero_thickness"],
                     color=self.parameters["zero_color"])
        self._make_axis_limits(x_axis_limits)
        plt.legend()
        plt.show()

    @staticmethod
    def _get_x_axis_limits(x_axes):
        """Get reasonable limits for the x axis.

        Determined the x axis limits using the lowest starting point and
        highest end point.
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
        plt.title(self.parameters["title"])
        plt.xlabel(self.parameters["x_name"])
        plt.ylabel(self.parameters["y_name"])

    def _plot_lines(self, x_coordinates, y_coordinates, curve_index):
        """Draw the spectrum curve.

        Parameters
        ----------
        x_coordinates: :class:`list`
            x values for plotting

        y_coordinates: :class:`list`
            y values for plotting

        """
        curve_name = self.parameters["names"][curve_index]
        if self.integrals and self.parameters["show_integrals"]:
            curve_name += "; Integral: "
            curve_name += str(round(self.integrals[curve_index], 6))
        plt.plot(x_coordinates, y_coordinates, label=curve_name,
                 color=self.parameters["colors"][curve_index])

    def _make_axis_limits(self, x_coordinates):
        """Set the limits of the x axis.

        Parameters
        ----------
        x_coordinates: :class:`list`
            x values to plot. These are necessary for determining the correct
            limits.

        """
        if self.parameters["fit_axis"]:
            self.axes.set_xlim(x_coordinates[0], x_coordinates[1])


class Saver(aspecd.plotting.Saver):
    """Saver used to save an image of a given plot."""

    def __init__(self, filename=None):
        super().__init__(filename=filename)
        self._set_defaults()

    def _set_defaults(self):
        """Sets the default values for data format and resolution."""
        self.parameters["format"] = ".png"
        self.parameters["res"] = 300

    def _save_plot(self):
        """Perform the actual saving of the plot.

        Uses the resolution (in dpi) specified in parameters/size.
        """
        self._add_file_extension()
        self.plotter.figure.savefig(self.filename, dpi=self.parameters["res"])
