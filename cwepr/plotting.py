"""
Plotting: Graphical representations of data extracted from datasets.

Graphical representations of cw-EPR data are an indispensable aspect of data
analysis. To facilitate this, a series of different plotters are available.

Plotting relies on `matplotlib <https://matplotlib.org/>`_, and mainly its
object-oriented interface should be used for the actual plotting.

Generally, two types of plotters can be distinguished:

* Plotters for handling single datasets

  Shall be derived from :class:`aspecd.plotting.SinglePlotter`.

* Plotters for handling multiple datasets

  Shall be derived from :class:`aspecd.plotting.MultiPlotter`.

In the first case, the plot is usually handled using the :meth:`plot` method
of the respective :obj:`cwepr.dataset.Dataset` object. Additionally,
those plotters always only operate on the data of a single dataset, and the
plot can easily be attached as a representation to the respective dataset.
Plotters handling single datasets should always inherit from the
:class:`aspecd.plotting.SinglePlotter` class.

In the second case, the plot is handled using the :meth:`plot` method of the
:obj:`aspecd.plotting.Plotter` object, and the datasets are stored as a list
within the plotter. As these plots span several datasets, there is no easy
connection between a single dataset and such a plot in sense of
representations stored in datasets. Plotters handling multiple datasets should
always inherit from the :class:`aspecd.plotting.MultiPlotter` class.


A note on array dimensions and axes
===================================

Something often quite confusing is the apparent inconsistency between the
order of array dimensions and the order of axes. While we are used to assign
axes in the order *x*, *y*, *z*, and assuming *x* to be horizontal,
*y* vertical (and *z* sticking out of the paper plane), arrays are usually
indexed row-first, column-second. That means, however, that if you simply
plot a 2D array in axes, your *first* dimension is along the *y* axis,
the *second* dimension along the *x* axis.

Therefore, as the axes of your datasets will always correspond to the array
dimensions of your data, in case of 2D plots you will need to *either* use
the information contained in the second axis object for your *x* axis label,
and the information from the first axis object for your *y* axis label,
*or* to transpose the data array.

Another aspect to have in mind is the position of the origin. Usually,
in a Cartesian coordinate system, convention is to have the origin (0,
0) in the *lower left* of the axes (for the positive quadrant). However,
for images, convention is to have the corresponding (0, 0) pixel located in
the *upper left* edge of your image. Therefore, those plotting methods
dealing with images will usually *revert* the direction of your *y* axis.
Most probably, eventually you will have to check with real data and ensure
the plotters to plot data and axes in a consistent fashion.


Types of concrete plotters
==========================

The cwepr package comes with a series of concrete plotters included ready
to be used, thanks to inheriting from the underlying ASpecD framework. As
stated above, plotters can generally be divided into two types: plotters
operating on single datasets and plotters combining the data of multiple
datasets into a single figure.

Additionally, plotters can be categorised with regard to creating figures
consisting of a single or multiple axes. The latter are plotters inheriting
from the :class:`aspecd.plotting.CompositePlotter` class. The latter can be
thought of as templates for the other plotters to operate on, *i.e.* they
provide the axes for other plotters to display their results.


Concrete plotters for single datasets
-------------------------------------

* :class:`cwepr.plotting.SinglePlotter1D`

  Basic line plots for single datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`cwepr.plotting.SinglePlotter2D`

  Basic 2D plots for single datasets, allowing to plot a series of 2D plots,
  including contour plots and image-type display

* :class:`cwepr.plotting.SingleCompositePlotter`

  Composite plotter for single datasets, allowing to plot different views of
  one and the same datasets by using existing plotters for single datasets.

* :class:`cwepr.plotting.GoniometerSweepPlotter`

  Composite plotter for single datasets representing goniometer sweeps,
  *i.e.* angular-dependent cw-EPR measurements.


Concrete plotters for multiple datasets
---------------------------------------

* :class:`cwepr.plotting.MultiPlotter1D`

  Basic line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots

* :class:`cwepr.plotting.MultiPlotter1DStacked`

  Stacked line plots for multiple datasets, allowing to plot a series of
  line-type plots, including (semi)log plots


Module documentation
====================

"""
import copy

import aspecd.plotting
import aspecd.processing

from cwepr import utils


class GoniometerSweepPlotter(aspecd.plotting.SingleCompositePlotter):
    """Overview of the results of a goniometer sweep.

    A goniometer sweep, *i.e.* a series of cw-EPR spectra as a function of
    the angle of the sample with respect to the external magnetic field,
    is usually performed over at least 180°, regardless of the step size.
    The reason is simply that the spectra for 0° and 180° should be
    identical due to the underlying physics of magnetic resonance.

    The plotter will create three subpanels:

    * A 2D plot (scaled image plot) as a general overview.

    * A 1D multiplot comparing the signals for 0° and 180° to check for
      consistency during the measurement.

    * A stacked plot showing all angular positions, providing an alternative
      view of the angular-dependent signal changes compared to the 2D plot.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class.

    To get an overview of your goniometer sweep, just invoke the plotter with
    default values:

    .. code-block:: yaml

       - kind: singleplot
         type: GoniometerSweepPlotter
         properties:
           filename: output.pdf

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
        self.parameters['show_zero_lines'] = False
        self.__kind__ = 'singleplot'
        self._exclude_from_to_dict.extend(['dataset', 'zero_deg_slice',
                                           'hundredeighty_deg_slice'])

    def _create_plot(self):
        self._configure_traces_plotter()
        self._configure_contour_plotter()
        self._extract_traces()
        self._configure_comparison_plotter()
        super()._create_plot()

    def _configure_contour_plotter(self):
        upper_contour = self.plotter[0]
        upper_contour.type = 'contourf'
        upper_contour.parameters['show_contour_lines'] = True
        upper_contour.properties.from_dict({
            'axes': {
                'yticks': [0, 30, 60, 90, 120, 150, 180]
            }
        })
        self.plotter[0] = upper_contour

    def _extract_traces(self):
        slicing = aspecd.processing.SliceExtraction()
        slicing.parameters['axis'] = axis_no = 1
        zero_value = self._get_angle_closest_to_value(axis_no, 0)
        hundredeighty_value = self._get_angle_closest_to_value(axis_no, 180)
        slicing.parameters['unit'] = 'axis'
        slicing.parameters['position'] = zero_value
        self.zero_deg_slice = copy.deepcopy(self.dataset)
        self.zero_deg_slice.process(slicing)
        self.zero_deg_slice.label = f'{zero_value:.1f}°'
        slicing.parameters['position'] = hundredeighty_value
        self.hundredeighty_deg_slice = copy.deepcopy(self.dataset)
        self.hundredeighty_deg_slice.process(slicing)
        self.hundredeighty_deg_slice.label = f'{hundredeighty_value:.1f}°'

    def _get_angle_closest_to_value(self, axis_no=0, value=None):
        axis = self.dataset.data.axes[axis_no].values
        return axis[min(range(len(axis)), key=lambda i: abs(axis[i]-value))]

    def _configure_comparison_plotter(self):
        comparison_plotter = self.plotter[1]
        comparison_plotter.datasets = [self.zero_deg_slice,
                                       self.hundredeighty_deg_slice]
        comparison_plotter.properties.from_dict({
            'drawings': [
                {'color': 'tab:blue'},
                {'color': 'tab:red'}
            ],
            'axes': {
                'yticks': [],
                'ylabel': r'$EPR\ intensity$'
            }
        })
        comparison_plotter.parameters['show_legend'] = True
        self.plotter[1] = comparison_plotter

    def _configure_traces_plotter(self):
        self.plotter[2].parameters['yticklabelformat'] = '%.1f'
        self.plotter[2].parameters['ytickcount'] = 19


class SinglePlotter1D(aspecd.plotting.SinglePlotter1D):
    """1D plots of single datasets.

    Convenience class taking care of 1D plots of single datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter1D`
    class for details.


    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for the plot, implicit and explicit

        The following keys exist, in addition to those of the superclass:

        g-axis: :class:`bool`
            Whether to show an additional opposite of the magnetic field axis

            This assumes the magnetic field axis to be the *x* axis and the
            magnetic field unit to be millitesla (mT).


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           filename: output.pdf


    In case you would have a *g* axis plotted as a second *x* axis on top:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter1D
         properties:
           parameters:
             g-axis: true
           filename: output.pdf

    """

    def __init__(self):
        super().__init__()
        self.parameters['g-axis'] = False

    def _create_plot(self):
        super()._create_plot()
        if self.parameters['g-axis'] and self.dataset.data.axes[0].unit == 'mT':
            self._create_g_axis()

    def _create_g_axis(self):
        mw_freq = self.dataset.metadata.bridge.mw_frequency.value

        def forward(values):
            return utils.convert_mT2g(values, mw_freq=mw_freq)

        def backward(values):
            return utils.convert_g2mT(values, mw_freq=mw_freq)

        gaxis = self.ax.secondary_xaxis('top', functions=(backward, forward))
        gaxis.set_xlabel('$g\ value$')


class SinglePlotter2D(aspecd.plotting.SinglePlotter2D):
    """2D plots of single datasets.

    Convenience class taking care of 2D plots of single datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SinglePlotter2D`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf

    To change the axes (flip *x* and *y* axis):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           parameters:
             switch_axes: True

    To use another type (here: contour):

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour

    To set the number of levels of a contour plot to 10:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           type: contour
           parameters:
             levels: 10

    To change the colormap (cmap) used:

    .. code-block:: yaml

       - kind: singleplot
         type: SinglePlotter2D
         properties:
           filename: output.pdf
           properties:
             drawing:
               cmap: RdGy

    Make sure to check the documentation of the ASpecD
    :mod:`aspecd.plotting` module for further parameters that can be set.

    """


class MultiPlotter1D(aspecd.plotting.MultiPlotter1D):
    """1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.MultiPlotter1D`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1D
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    """


class MultiPlotter1DStacked(aspecd.plotting.MultiPlotter1DStacked):
    """Stacked 1D plots of multiple datasets.

    Convenience class taking care of 1D plots of multiple datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.MultiPlotter1DStacked`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. Of course, all parameters settable
    for the superclasses can be set as well. The examples focus each on a
    single aspect.

    In the simplest case, just invoke the plotter with default values:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf

    To change the settings of each individual line (here the colour and label),
    supposing you have three lines, you need to specify the properties in a
    list for each of the drawings:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           properties:
             drawings:
               - color: '#FF0000'
                 label: foo
               - color: '#00FF00'
                 label: bar
               - color: '#0000FF'
                 label: foobar

    .. important::
        If you set colours using the hexadecimal RGB triple prefixed by
        ``#``, you need to explicitly tell YAML that these are strings,
        surrounding the values by quotation marks.

    Sometimes you want to have horizontal "zero lines" appear for each
    individual trace of the stacked plot. This can be achieved explicitly
    setting the "show_zero_lines" parameter to "True" that is set to "False"
    by default:

    .. code-block:: yaml

       - kind: multiplot
         type: MultiPlotter1DStacked
         properties:
           filename: output.pdf
           parameters:
             show_zero_lines: True

    """


class CompositePlotter(aspecd.plotting.CompositePlotter):
    """Base class for plots consisting of multiple axes.

    The underlying idea of composite plotters is to use a dedicated
    existing plotter for each axis and assign this plotter to the list of
    plotters of the CompositePlotter object. Thus the actual plotting task
    is left to the individual plotter and the CompositePlotter only takes
    care of the specifics of plots consisting of more than one axis.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.CompositePlotter`
    class for details.

    """


class SingleCompositePlotter(aspecd.plotting.SingleCompositePlotter):
    """Composite plotter for single datasets.

    This composite plotter is used for different representations of one and the
    same dataset in multiple axes contained in one figure. In this respect,
    it works like all the other ordinary single plotters derived from
    :class:`SinglePlotter`, *i.e.* it usually gets called by using the dataset's
    :meth:`aspecd.dataset.Dataset.plot` method.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.SingleCompositePlotter`
    class for details.

    """


class Saver(aspecd.plotting.Saver):
    """Base class for saving plots.

    For basic saving of plots, no subclassing is necessary, as the
    :meth:`save` method uses :meth:`matplotlib.figure.Figure.savefig` and
    can cope with all possible parameters via the :attr:`parameters` property.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.plotting.Saver` class for
    details.

    """
