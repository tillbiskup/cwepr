"""Module containing data plotters for different applications."""
import copy

import aspecd.plotting
import aspecd.processing


class Saver(aspecd.plotting.Saver):
    """Saver used to save an image of a given plot."""


class GoniometerSweepPlotter(aspecd.plotting.SingleCompositePlotter):
    """Goniometer plotter based on the single composite plotter.

        Besides the plots for the overview, it shows the overlay of the 0
        and 180 degree traces to check for consistency during the measurement.
    """

    def __init__(self):
        super().__init__()
        self.description = 'Plot for one goniometric dataset in different ' \
                           'representations.'
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
