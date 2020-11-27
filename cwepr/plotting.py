"""Module containing data plotters for different applications."""

import numpy as np
import matplotlib.pyplot as plt

import aspecd.plotting


class Error(Exception):
    """Base class for exceptions in this module."""


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


class MissingInformationError(Error):
    """Exception raised when not enough information is provided."""

    def __init__(self, message=''):
        super().__init__()
        self.message = message



class BaselineControlPlotter(aspecd.plotting.SinglePlotter):
    """Plotter to visualize possible baseline fits.

    Visualise the spectrum and a number of possible baseline correction
    polynomials.

    .. warning::
        This should be written as a recipe rather than as a plotter.

    Attributes
    ----------
    self.parameters['coefficients']: :class:`list`
        List containing any number of other lists each containing a set of
        polynomial coefficients for a polynomial that might be used for the
        baseline correction. The order of the coefficients is considered to
        highest to lowest as returned by :meth:`numpy.polyfit`.

    self.parameters['data']: :class:`numpy.array`
        Array containing the x (field) and y (intensity) values of the
        spectrum that shall be visualized with the polynomials

    """

    def __init__(self):
        super().__init__()
        self.parameters["coefficients"] = None
        self.parameters["data"] = None

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
        self.style = ''
        self._set_defaults()
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _set_defaults(self):
        """Create default values for all settings of the plot."""
        self.parameters["color"] = "tab:blue"
        self.parameters["title"] = ""
        self.parameters["draw_zero"] = True
        self.parameters["xlim"] = None

    def _create_plot(self):
        """Draw and display the plot.

        The plot settings are put into the parameter attribute.
        """
        self._set_style()
        self._make_title()
        self._plot_data()
        self._set_extent()

    def _make_title(self):
        """Set title."""
        plt.title(self.parameters["title"])

    def _plot_data(self):
        """Draw the spectrum and the zero line (if desired)."""
        if self.parameters["draw_zero"]:
            plt.axhline(**self._zero_line_style)

        plt.plot(self.dataset.data.axes[0].values, self.dataset.data.data,
                 color=self.parameters["color"])

    def _set_extent(self):
        """Set the limits of the x axis.

        The limits are first fitted to the width of the spectrum (if
        necessary),then overridden with user specified values (if applicable).

        Parameters
        ----------
        self.dataset.data.axes[0].values: :class:`list`
            x values to plot. These are necessary for determining the correct
            limits.

        """
        if self.parameters["xlim"]:
            self.axes.set_xlim(self.parameters["xlim"])
        else:
            self.axes.set_xlim(self.dataset.data.axes[0].values[0],
                               self.dataset.data.axes[0].values[-1])

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()


class MultiPlotter(aspecd.plotting.MultiPlotter):
    """Plotter used for plotting multiple spectra at the same time."""

    def __init__(self):
        super().__init__()
        # multiple datasets in self.datasets
        self.description = "1D plotter for multiple datasets."
        self._zero_line_style = {'y': 0,
                                 'color': '#999999'}
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

        self.parameters["title"] = ''
        self.parameters["draw_zero"] = True
        self.parameters["fit_axis"] = True
        self.parameters["color"] = None
        self.parameters["xlim"] = None
        self.parameters['text'] = {
            'position': [],
            'text': str()
        }

    def _create_plot(self):
        """Draw and display the plot."""
        for i, dataset_ in enumerate(self.datasets):
            if self.parameters['color']:
                self.axes.plot(dataset_.data.axes[0].values,
                               dataset_.data.data,
                               color=self.parameters['color'][i])
            else:
                self.axes.plot(dataset_.data.axes[0].values, dataset_.data.data)
        if self.parameters["draw_zero"]:
            self._display_zero_line()
        self._set_axes()
        self._set_title()
        self._set_text()

    def _display_zero_line(self):
        """Create a horizontal line at zero."""
        plt.axhline(**self._zero_line_style)

    def _set_title(self):
        """Set title."""
        plt.title(self.parameters["title"])

    def _set_axes(self):
        if self.parameters['xlim']:
            self.axes.set_xlim(self.parameters['xlim'])
        else:
            self.axes.set_xlim([self.datasets[0].data.axes[0].values[0],
                                self.datasets[0].data.axes[0].values[-1]])
        plt.ticklabel_format(**self._ticklabel_format)

    def _set_text(self):
        if self.parameters['text']['position'] and \
                self.parameters['text']['text']:
            plt.text(self.parameters['text']['position'][0], self.parameters[
                'text']['position'][1], self.parameters['text']['text'])


class Saver(aspecd.plotting.Saver):
    """Saver used to save an image of a given plot."""


class GoniometerSweepPlotter(aspecd.plotting.SinglePlotter):
    """Plotter for overviewing angle dependent data.

    .. important::
        As aspecd developed further, there is the composite plotter to
        inherit from. This plotter should thus get reworked."""

    def __init__(self):
        super().__init__()
        self.axes = None
        self.style = ''
        self.description = 'Plot for one goniometric dataset in different ' \
                           'representations.'
        self.parameters['color'] = None
        self.parameters['xlim'] = tuple()
        self.parameters["title"] = ''
        self.subs = []
        self._ticklabel_format = {'style': 'sci',
                                  'scilimits': (-2, 4),
                                  'useMathText': True}

    def _create_plot(self):
        """Plot the given dataset in three different representations."""
        self._set_xlims()
        self._set_style()  # xkcd
        self._create_figure_and_axes()
        self._make_stacked_plot(axis=self.subs[2])
        self._make_contour_plot(axis=self.subs[0])
        self._make_second_contour_plot(axis=self.subs[1])
        self._adjust_spacing()
        self._set_title()

    def _set_xlims(self):
        if not self.parameters['xlim']:
            self.parameters['xlim'] = \
                tuple([self.dataset.data.axes[0].values[0],
                       self.dataset.data.axes[0].values[-1]])
            assert len(self.parameters['xlim']) == 2

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()

    def _create_figure_and_axes(self):
        """Overrides method in Aspecd to create figure with 3 axes.

        .. todo:: Add condition in Aspecd to check if there is already a
                figure element. If not, create a new one.
        """
        self.figure = plt.figure(figsize=(16 / 2.54, 16 / 2.54))

        subplots = [(2, 2, 1), (2, 2, 3), (1, 2, 2)]
        self.subs = [1, 2, 3]
        number = 0
        for nrows, ncols, plot_number in subplots:
            self.subs[number] = self.figure.add_subplot(nrows, ncols,
                                                        plot_number)
            number += 1
        self.axes = self.subs[2]

    def _make_stacked_plot(self, axis=None):
        if not axis:
            raise MissingInformationError(message='No axis provided fpr '
                                                  'plotting.')

        b_field = self.dataset.data.axes[0].values
        angles = self.dataset.data.axes[1].values

        stack_offset = 0.5 * max(self.dataset.data.data[0, :])
        offset = 0
        offsets = []

        for idx, _ in enumerate(angles):
            axis.plot(b_field, self.dataset.data.data[idx, :] + offset, 'k',
                      linewidth=0.7)
            offsets.append(offset)
            offset += stack_offset

        axis.grid(axis='x')
        axis.set(xlim=self.parameters['xlim'],
                 yticks=offsets,
                 yticklabels=self.dataset.data.axes[1].values)

    def _make_contour_plot(self, axis=None):
        self.axes = axis

        b_field = self.dataset.data.axes[0].values
        angles = self.dataset.data.axes[1].values

        axis.contourf(b_field, angles, self.dataset.data.data, 30, )
        axis.contour(b_field, angles, self.dataset.data.data, 15,
                     colors='black', linewidths=0.5)

        axis.set(xlim=self.parameters['xlim'])

    def _make_second_contour_plot(self, axis):
        b_field = self.dataset.data.axes[0].values
        angles = self.dataset.data.axes[1].values

        axis.contourf(b_field, angles, self.dataset.data.data, 30, )
        axis.set(xlim=self.parameters['xlim'])

    def _adjust_spacing(self):
        # left, bottom, width, height
        l, b, w, h = self.subs[2].get_position().bounds
        self.subs[2].set_position([l + 0.15 * w, b, w, 1.05 * h])
        l, b, w, h = self.subs[1].get_position().bounds
        self.subs[1].set_position([l, b, w, 1.05 * h])
        l, b, w, h = self.subs[0].get_position().bounds
        self.subs[0].set_position([l, b + 0.05 * h, w, 1.05 * h])

    def _set_title(self):
        self.figure.suptitle(self.parameters["title"])


class StackedPlotter(aspecd.plotting.SinglePlotter):
    """Make stacked plot of data in a 2D dataset.

    ..note::
        not tested

    """
    def __init__(self):
        super().__init__()
        self.description = 'Stack 2D plots of a 3D dataset.'
        self.parameters['xlim'] = tuple()
        self.style = ''

    def _create_plot(self):
        """Plot the given dataset in three different representations."""
        self._set_xlims()
        self._set_style()  # xkcd
        self._make_stacked_plot()

    def _set_xlims(self):
        if not self.parameters['xlim']:
            self.parameters['xlim'] = \
                tuple([self.dataset.data.axes[0].values[0],
                       self.dataset.data.axes[0].values[-1]])
            assert len(self.parameters['xlim']) == 2

    def _set_style(self):
        """Set the style to xkcd if indicated."""
        if self.style == 'xkcd':
            plt.xkcd()

    def _make_stacked_plot(self, axis=None):
        if not axis:
            raise MissingInformationError(message='No axis provided for '
                                                  'plotting.')

        b_field = self.dataset.data.axes[0].values
        variable_parameter = self.dataset.data.axes[1].values

        stack_offset = 0.5 * max(self.dataset.data.data[0, :])
        offset = 0
        offsets = []

        for idx, _ in enumerate(variable_parameter):
            axis.plot(b_field, self.dataset.data.data[idx, :] + offset, 'k',
                      linewidth=0.7)
            offsets.append(offset)
            offset += stack_offset

        axis.grid(axis='x')
        axis.set(xlim=self.parameters['xlim'],
                 yticks=offsets,
                 yticklabels=self.dataset.data.axes[1].values)

