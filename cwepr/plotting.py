"""Module containing data plotters for different applications.
"""

import matplotlib.pyplot as plt
import numpy as np

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
    baseline correction polynomials.

    Attributes
    ----------
    coeffs: :class:`list`
        List containing any number of other lists each containing
        a set of polynomial coefficients for a polynomial that might
        be used for the baseline correction. The order of the coefficients
        is considered to highest to lowest as returned by
        :meth:`numpy.polyfit`.

    data: :class:`numpy.array`
        Array containing the x (field) and y (intensity) values of the
        spectrum that shall be visualized with the polynomials
    """
    def __init__(self, data, coeffs):
        super().__init__()
        self.parameters["coeffs"] = coeffs
        self.parameters["data"] = data

    def _create_plot(self):
        """Plot the spectrum and one or more baselines.

        Plots the spectrum as well as one curve for
        each set of polynomial coefficients provided.

        The polynomial are indicated in the legend by their order.

        The final diagram is displayed.
        """

        data = self.parameters["data"]
        coeffs_list = self.parameters["coeffs"]
        x = data.axes[0].values
        y = data.data

        plt.title("Baseline Comparison")
        plt.xlabel("$B_0$ / mT")
        plt.ylabel("$Intensity\\ Change and possible baselines$")

        plt.plot(x, y, label="Spectrum")
        for coeffs in coeffs_list:
            plt.plot(x, np.polyval(np.poly1d(coeffs), x),
                     label=str(len(coeffs)-1))

        plt.legend()
        plt.show()


class SimpleSpectrumPlotter(aspecd.plotting.SinglePlotter):
    """Simple but highly customizable plotter for a single spectrum.

    Attributes
    ----------
    settings: :class:`dict`
        Values used for customization.
    """
    def __init__(self):
        super().__init__()
        #self.settings = dict()
        self._set_defaults()

    def _set_defaults(self):
        """Create default values for all settings of the plot."""
        self.set_color("tab:blue")
        self.set_title("")
        #self.set_x_axis_name("Field")
        #self.set_y_axis_name("Intensity Change")
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
        color: :class:`str` or RGBA tuple
            The color to use.
        """
        self.parameters["color"] = color

    def set_title(self, title):
        """Sets the title of the plot.

        Parameters
        ----------
        title: :class:`str`
            The title to use.
        """
        self.parameters["title"] = title

    def set_x_axis_name(self, name):
        """Sets the label of the x axis.

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.parameters["x_name"] = name

    def set_y_axis_name(self, name):
        """Sets the label of the y axis.

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.parameters["y_name"] = name

    def set_curve_name(self, name):
        """Sets the label of the main (derivative) curve
        in the legend..

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.parameters["curve_name"] = name

    def set_draw_zeroline(self, do_draw):
        """Set whether the zero line should be drawn.

        Parameters
        ----------
        do_draw: :class:`bool`
            Should the zero line be drawn?
        """
        self.parameters["draw_zero"] = do_draw

    def set_zeroline_thickness(self, thickness):
        """Sets thickness of the zero line.

        Parameters
        ----------
        thickness: :class:`float`
            Thickness of the zero line; default: 0.5
        """
        self.parameters["zero_thickness"] = thickness

    def set_zeroline_color(self, color):
        """Sets the color of the zero line.

        Parameters
        ----------
        color: :class:`str` or RGBA tuple
            The color to use.
        """
        self.parameters["zero_color"] = color

    def set_fit_axis_to_spectrum(self, do_fit):
        """Whether the x axis limits should be fitted to width of the spectrum.

        Parameters
        ----------
        do_fit: :class:`bool`
            Should the width of the plot fit the width of the curve?
        """
        self.parameters["fit_axis"] = do_fit

    def set_x_axis_limits(self, left, right):
        """Sets the limits of the x axis.

        Note: Using None as a limit will leave the respective limit unchanged.

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
        x = self.dataset.data.axes[0].values
        y = self.dataset.data.data
        self._make_labels_and_title()
        self._plot_lines(x, y)
        self._make_axis_limits(x)
        plt.legend()
        plt.show()

    def _make_labels_and_title(self):
        """Create the title as well as the labels for the axes."""
        plt.title(self.parameters["title"])
        #plt.xlabel(self.parameters["x_name"])
        #plt.ylabel(self.parameters["y_name"])

    def _plot_lines(self, x, y):
        """Draw the spectrum curve and the zero line (if necessary).

        Parameters
        ----------
        x: :class:`list`
            x values for plotting
        y: :class:`list`
            y values for plotting
        """
        if self.parameters["draw_zero"]:
            plt.plot(x, 0 * x, lw=self.parameters["zero_thickness"],
                     color=self.parameters["zero_color"])
        plt.plot(x, y, label=self.parameters["curve_name"],
                 color=self.parameters["color"])

    def _make_axis_limits(self, x):
        """Set the limits of the x axis.

        The limits are first fitted to the width of the spectrum
        (if necessary),then overridden with user specified values
        (if applicable).

        Parameters
        ----------
        x: :class:`list`
            x values to plot. These are necessary for determining the
            correct limits.
        """
        if self.parameters["fit_axis"]:
            self.axes.set_xlim(x[0], x[-1])
        self.axes.set_xlim(self.parameters["limit_left"],
                           self.parameters["limit_right"])


class SpectrumAndIntegralPlotter(SimpleSpectrumPlotter):
    """Plotter used for plotting a derivative spectrum as well as
    the first and / or second integral curve.

    Either integral curve can be omitted but NOT BOTH.

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
        color: :class:`str` or RGBA tuple
            The color to use.
        """
        self.parameters["integral1_color"] = color

    def set_integral1_name(self, name):
        """Sets the label of the first integral curve
        in the legend.

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.parameters["integral1_name"] = name

    def set_integral2_color(self, color):
        """Sets the color of the second integral curve.

        Parameters
        ----------
        color: :class:`str` or RGBA tuple
            The color to use.
        """
        self.parameters["integral2_color"] = color

    def set_integral2_name(self, name):
        """Sets the label of the second integral curve
        in the legend.

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.parameters["integral2_name"] = name

    def _plot_lines(self, x, y):
        """Perform the actual plot for spectrum and integral(s)

        Draw the spectrum curve and the zero line (if necessary).
        Additionally draw one or both integral curves. Either one of the
        integral curves can be omitted but NOT BOTH.

        Parameters
        ----------
        x: :class:`list`
            x values for plotting
        y: :class:`list`
            y values for plotting

        Raises
        ------
        NoIntegralDataProvidedError
            Raised when data for both integrations is omitted.
        """
        if self.parameters["draw_zero"]:
            plt.plot(x, 0 * x, lw=self.parameters["zero_thickness"],
                     color=self.parameters["zero_color"])
        plt.plot(x, y, label=self.parameters["curve_name"],
                 color=self.parameters["color"])
        if (self.parameters["integral_1"] is None and
                self.parameters["integral_2"] is None):
            raise NoIntegralDataProvidedError(""""Neither first nor second 
integration data points have been provided for integral plotting.""")
        if self.parameters["integral_1"] is not None:
            plt.plot(x, self.parameters["integral_1"],
                     label=self.parameters["integral1_name"],
                     color=self.parameters["integral1_color"])
        if self.parameters["integral_2"] is not None:
            plt.plot(x, self.parameters["integral_2"],
                     label=self.parameters["integral2_name"],
                     color=self.parameters["integral2_color"])


class Multiplotter(aspecd.plotting.MultiPlotter):
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
        #self.settings = dict()
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
        self.set_curve_colors(color_library[:len(self.parameters["datasets"])])
        curve_names = list()
        for n in range(len(self.parameters["datasets"])):
            name = "Curve " + str(n)
            curve_names.append(name)
        self.set_curve_names(curve_names)
        self.set_show_integrals(True)

    def set_curve_names(self, names):
        """Sets the names for the different curves.

        Parameters
        ----------
        names: :class:`list`
            List of 'str' containing the names.
        """
        self.parameters["names"] = names

    def set_curve_colors(self, colors):
        """Sets the colors for the different curves.

        Parameters
        ----------
        colors: :class:`list`
            List of 'str' and or RGBA containing the colors.
        """
        self.parameters["colors"] = colors

    def set_title(self, title):
        """Sets the title of the plot.

        Parameters
        ----------
        title: :class:`str`
            The title to use.
        """
        self.parameters["title"] = title

    def set_x_axis_name(self, name):
        """Sets the label of the x axis.

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.parameters["x_name"] = name

    def set_y_axis_name(self, name):
        """Sets the label of the y axis.

        Parameters
        ----------
        name: :class:`str`
            The name to use.
        """
        self.settings["y_name"] = name

    def set_draw_zeroline(self, do_draw):
        """Set whether the zero line should be drawn.

        Parameters
        ----------
        do_draw: :class:`bool`
            Should the zero line be drawn?
        """
        self.parameters["draw_zero"] = do_draw

    def set_zeroline_thickness(self, thickness):
        """Sets thickness of the zero line.

        Parameters
        ----------
        thickness: :class:`float`
            Thickness of the zero line; default: 0.5
        """
        self.parameters["zero_thickness"] = thickness

    def set_zeroline_color(self, color):
        """Sets the color of the zero line.

        Parameters
        ----------
        color: :class:`str` or RGBA tuple
            The color to use.
        """
        self.parameters["zero_color"] = color

    def set_fit_axis_to_spectrum(self, do_fit):
        """Whether the x axis limits should be fitted to the width of the
        spectrum.

        Parameters
        ----------
        do_fit: :class:`bool`
            Should the width of the plot fit the width of the curve?
        """
        self.parameters["fit_axis"] = do_fit

    def set_show_integrals(self, do_show):
        """Whether the integrals should be shown in the legend if provided.

        Parameters
        ----------
        do_show: :class:`bool`
            Should the integrals be indicated?
        """
        self.parameters["show_integrals"] = do_show

    def _create_plot(self):
        """Draw and display the plot."""
        x_axes = list()
        self._make_labels()
        for n in range(len(self.parameters["datasets"])):
            x = self.parameters["datasets"][n].data.axes[0].values
            y = self.parameters["datasets"][n].data.data
            x_axes.append(x)
            self._plot_lines(x, y, n)
        x_axis_limits = self.get_x_axis_limits(x_axes)
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
    def get_x_axis_limits(x_axes):
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

    def _plot_lines(self, x, y, n):
        """Draw the spectrum curve.

        Parameters
        ----------
        x: :class:`list`
            x values for plotting
        y: :class:`list`
            y values for plotting
        """
        curve_name = self.parameters["names"][n]
        if len(self.integrals) > 0 and self.parameters["show_integrals"]:
            curve_name += "; Integral: "
            curve_name += str(round(self.integrals[n], 6))
        plt.plot(x, y, label=curve_name, color=self.parameters["colors"][n])

    def _make_axis_limits(self, x):
        """Set the limits of the x axis.

        Parameters
        ----------
        x: :class:`list`
            x values to plot. These are necessary for determining the
            correct limits.
        """
        if self.parameters["fit_axis"]:
            self.axes.set_xlim(x[0], x[1])


class PlotSaver(aspecd.plotting.Saver):
    """Saver used to save an image of a given plot.
    """
    def __init__(self, filename=None):
        super().__init__(filename=filename)
        self.set_defaults()

    def set_format(self, dataformat):
        """Sets the data format to save to (Default: .png).

        Parameters
        ----------
        dataformat: :class:`str`
            File extension
        """
        self.parameters["format"] = dataformat

    def set_res(self, res):
        """Sets the resolution for the saved image (Default: 300 dpi).

        Parameters
        ----------
        res: :class:`str`
            Resolution (dpi)
        """
        self.parameters["res"] = res

    def set_defaults(self):
        """Sets the default values for data format and resolution.
        """
        self.set_format(".png")
        self.set_res(300)

    def _save_plot(self):
        """Perform the actual saving of the plot.

        Uses the resolution (in dpi) specified in parameters/size.
        """
        self._add_file_extension()
        self.plotter.figure.savefig(self.filename, dpi=self.parameters["res"])
