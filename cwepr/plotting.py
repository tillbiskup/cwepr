"""Module containing data plotters for different applications."""
import copy

import matplotlib.pyplot as plt

import aspecd.plotting
import aspecd.processing


class Saver(aspecd.plotting.Saver):
    """Saver used to save an image of a given plot."""


class OldGoniometerSweepPlotter(aspecd.plotting.SinglePlotter):
    """Plotter for overviewing angle dependent data.

    .. important::
        As aspecd developed further, there is the composite plotter to
        inherit from. This plotter should thus get reworked.

    .. todo::
        Eventually delete this plotter
    """

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
        b_field = self.dataset.data.axes[0].values
        angles = self.dataset.data.axes[1].values

        stack_offset = 0.5 * max(self.dataset.data.data[0, :])
        offset = 0
        offsets = []

        for idx, _ in enumerate(angles):
            axis.plot(b_field, self.dataset.data.data[:, idx] + offset, 'k',
                      linewidth=0.7)
            offset += stack_offset
            offsets.append(offset)

        axis.grid(axis='x')
        axis.set(xlim=self.parameters['xlim'],
                 yticks=offsets,
                 yticklabels=self.dataset.data.axes[1].values)

    def _make_contour_plot(self, axis=None):
        self.axes = axis

        b_field = self.dataset.data.axes[0].values
        angles = self.dataset.data.axes[1].values

        axis.contourf(b_field, angles, self.dataset.data.data.T, 30, )
        axis.contour(b_field, angles, self.dataset.data.data.T, 15,
                     colors='black', linewidths=0.5)

        axis.set(xlim=self.parameters['xlim'])

    def _make_second_contour_plot(self, axis):
        b_field = self.dataset.data.axes[0].values
        angles = self.dataset.data.axes[1].values

        axis.contourf(b_field, angles, self.dataset.data.data.T, 30, )
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


class GoniometerSweepPlotter(aspecd.plotting.SingleCompositePlotter):
    """Goniometer plotter based on the composite plotter.
    """

    def __init__(self):
        super().__init__()
        self.grid_dimensions = [2, 2]
        self.subplot_locations = [[0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 2, 1]]
        self.plotter = [aspecd.plotting.SinglePlotter2D(),
                        aspecd.plotting.SinglePlotter2D(),
                        aspecd.plotting.SinglePlotter2DStacked()]
        self.axes_positions = [[0, 0.15, 1, 1], [0, 0, 1, 1],
                               [0.25, 0, 0.9, 1.07]]

    def set_properties(self):
        upper_contour = self.plotter[0]
        upper_contour.type = 'contourf'
        upper_contour.parameters['show_contour_lines'] = True

    def _create_plot(self):
        self.set_properties()
        super()._create_plot()


class GoniometerSweepControlPlotter(aspecd.plotting.SingleCompositePlotter):
    """Goniometer plotter based on the composite plotter.

        Besides the plots for the overview, it shows the overlay of the 90
        and 180 degree traces to check for consistency during the measurement
    """

    def __init__(self):
        super().__init__()
        self.grid_dimensions = [2, 2]
        self.subplot_locations = [[0, 0, 1, 1], [1, 0, 1, 1], [0, 1, 2, 1]]
        self.plotter = [aspecd.plotting.SinglePlotter2D(),
                        aspecd.plotting.MultiPlotter1D(),
                        aspecd.plotting.SinglePlotter2DStacked()]
        self.axes_positions = [[0, 0.15, 1, 1], [0, 0, 1, 1],
                               [0.25, 0, 0.9, 1.07]]
        self.zero_deg_slice = None
        self.hundredeighty_deg_slice = None

    def _set_properties(self):
        upper_contour = self.plotter[0]
        upper_contour.type = 'contourf'
        upper_contour.parameters['show_contour_lines'] = True

    def _create_plot(self):
        self.configure_contour_plotter()
        self._extract_traces()
        self._configure_comparison_plotter()
        self._set_properties()
        super()._create_plot()

    def _extract_traces(self):
        slicing = aspecd.processing.SliceExtraction()
        slicing.parameters['position'] = 0
        slicing.parameters['unit'] = 'axis'
        slicing.parameters['axis'] = 1
        self.zero_deg_slice = copy.deepcopy(self.dataset)
        self.zero_deg_slice.process(slicing)
        self.zero_deg_slice.label = '0°'
        slicing.parameters['position'] = 180
        self.hundredeighty_deg_slice = copy.deepcopy(self.dataset)
        self.hundredeighty_deg_slice.process(slicing)
        self.hundredeighty_deg_slice.label = '180°'

    def _configure_comparison_plotter(self):
        comparison_plotter = aspecd.plotting.MultiPlotter1D()
        comparison_plotter.datasets = [self.zero_deg_slice,
                                       self.hundredeighty_deg_slice]
        comparison_plotter.properties.from_dict({
            'drawings': [
                {'color': 'tab:blue'},
                {'color': 'tab:red'}
            ],
            'axes': {
                'yticks': [],
                'ylabel': '$EPR\ intensity$'
            }
        })
        comparison_plotter.parameters['show_legend'] = True
        self.plotter[1] = comparison_plotter

    def configure_contour_plotter(self):
        self.plotter[0].properties.from_dict({
            'axes': {
                'yticks': [0, 30, 60, 90, 120, 150, 180]
            }
        })
