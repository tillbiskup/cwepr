"""Module containing the processing steps of the cwEPR package.

.. sidebar::
    processing *vs.* analysis

    For more details on the difference between processing and analysis,
    see the `ASpecD documentation <https://docs.aspecd.de/>`_.


A processing step always operates on a dataset and usually modifies the
numerical data contained therein. The result of a processing step is in any
case again a dataset, in contrast to analysis steps where this is not
necessarily the case. Typical routine processing steps are normalisation (to
area, amplitude, maximum, minimum), and for EPR spectroscopy such things as
field and frequency correction.


Processing steps implemented
============================

The processing steps implemented in this module can be separated into those
specific for cw-EPR data and those that are generally applicable and were
inherited from the ASpecD framework.


Processing steps specific for cw-EPR data
-----------------------------------------

Currently, the following processing steps are implemented:

  * :class:`FieldCorrection`
  * :class:`FrequencyCorrection`
  * :class:`GAxisCreation`

  * :class:`BaselineCorrectionWithPolynomial`

  * :class:`NormalisationOfDerivativeToArea`
  * :class:`Normalisation`

  * :class:`Integration`

  * :class:`Averaging2DDataset`
  * :class:`SubtractVector`

Implemented but not working as they should:

  * :class:`PhaseCorrection`
  * :class:`AutomaticPhaseCorrection`


General processing steps inherited from the ASpecD framework
------------------------------------------------------------

Besides the processing steps specific for cw-EPR data, a number of further
processing steps that are generally applicable to spectroscopic data have
been inherited from the underlying ASpecD framework:

* :class:`ScalarAlgebra`

  Perform scalar algebraic operation on one dataset.

  Operations available: add, subtract, multiply, divide (by given scalar)

* :class:`ScalarAxisAlgebra`

  Perform scalar algebraic operation on axis values of a dataset.

  Operations available: add, subtract, multiply, divide, power (by given scalar)

* :class:`DatasetAlgebra`

  Perform scalar algebraic operation on two datasets.

  Operations available: add, subtract

* :class:`Projection`

  Project data, *i.e.* reduce dimensions along one axis.

* :class:`SliceExtraction`

  Extract slice along one ore more dimensions from dataset.

* :class:`BaselineCorrection`

  Correct baseline of dataset.

* :class:`Averaging`

  Average data over given range along given axis.

* :class:`Filtering`

  Filter data


Further processing steps implemented in the ASpecD framework can be used as
well, by importing the respective modules. In case of recipe-driven data
analysis, simply prefix the kind with ``aspecd``:

.. code-block:: yaml

    - kind: aspecd.processing
      type: <ClassNameOfProcessingStep>


Categories of processing steps
==============================

Processing steps can be categorised further. The following is an attempt to
do that for cwEPR data and at the same time a list of processing steps one
would like to have implemented. Besides that, it seems that this list
evolves more and more towards a summary of how to properly record and
(post-)process cwEPR data.

For more authoritative answers, you may as well have a look into the EPR
literature, particularly the "EPR Primer" by Chechik/Carter/Murphy
:cite:p:`proc-chechik-v-2016` and the book on quantitative EPR by the Eatons
:cite:p:`proc-eaton-ge-2010`.


Corrections
-----------

When analysing cwEPR data, usually, a series of simple correction steps is
performed prior to any further analysis. This is particularly important if
you plan to compare different datasets or if you would like to compare your
spectra with those from the literature (always a good idea, though).

  * Magnetic field correction

    Usually, the magnetic field in an EPR measurement needs to be determined
    by measuring a field standard in the identical setup, as the actual
    magnetic field at the sample will usually differ from the field set in
    the software.

    Appropriate magnetic field correction becomes particularly important if
    you are interested in absolute *g* values of your sample, *e.g.* to
    compare it to literature data or quantum-chemical calculations and to
    get ideas as to where the unpaired spin may predominantly reside on (in
    terms of nuclear species).

  * Microwave frequency correction

    Comparing datasets is only possible in a meaningful manner if they are
    either corrected for same frequency, or their magnetic field axes
    converted in a g axis.

  * Microwave phase correction

    Usually, cwEPR spectra are not recorded with quadrature detection,
    *i.e.*, with both, absorptive and dispersive signal components. However,
    using the Hilbert transform, one can reconstruct the dispersive signal (
    imaginary component) and correct the phase of the microwave source this way.

  * Baseline correction

    However careful measurements are performed, baselines are quite often
    encountered. There are two different kinds of baseline that need to be
    corrected in different ways. Drifts of some kind can usually be handled
    by fitting and afterwards subtracting a (low-order) polynomial to the data.

    Particularly for low-temperature data, weak signals, and large magnetic
    field sweep ranges, resonator background can become quite dramatic.
    Here, usually the only viable way is to record the empty resonator
    independently under as much identical conditions as possible compared to
    recording the signal of the actual sample (but with slightly broader
    field range to compensate for different microwave frequency) and
    afterwards subtracting this dataset (empty resonator, *i.e.* resonator
    background signal) from the signal of the actual sample.


Algebra
-------

.. sidebar::
    Availability

    Algebra is available with:
    :class:`ScalarAlgebra` and
    :class:`DatasetAlgebra`

Comparing datasets often involves adding, subtracting, multiplying or
dividing the intensity values by a given fixed number. Possible scenarios
where one wants to multiply the intensity values of a cwEPR spectrum may be
comparing spectra resulting from a single species from those of known two
species, different (known) concentrations and alike.

Of course, dividing the intensity of the spectrum by the maximum intensity
is another option, however, this would be normalisation to maximum (not
always a good idea, usually normalising to area or amplitude is better),
and this is handled by a different set of processing steps (see below).

This type of simple algebra is quite *different* from adding or subtracting
datasets together. Whereas simple algebra really is a one-liner in terms of
implementation, handling different datasets involves ensuring commensurable
axis dimensions and ranges, to say the least. Dataset algebra is available as
well in this module.


Normalisation
-------------

Normalising data to some common characteristic is a prerequisite for
comparing datasets among each other.

There is a number of normalisations that are common for nearly every kind of
data, and as such, these normalisation steps should probably eventually be
implemented within the ASpecD framework. As there are:

  * Normalisation to maximum

    Simply divide the intensity values by their maximum

    Often used as a very simple "normalisation" approach. Depends highly on
    the situation and focus of the representation, but usually,
    other methods such as normalisation to amplitude or area, are better
    suited.

  * Normalisation to minimum

    Simply divide the intensity values by their minimum

    The same as for the normalisation to maximum applies here. Furthermore,
    normalising to the minimum usually only makes sense in case of
    prominent negative signal components, as in first-derivative spectra in
    cwEPR spectroscopy.

  * Normalisation to amplitude

    Divide the intensity values by the absolute of the difference between
    maximum and minimum intensity value

    Usually better suited as a simple normalisation than the naive
    normalising to maximum or minimum described above. However, it strongly
    depends on what you are interested in comparing and want to highlight.

  * Normalisation to area

    Divide the intensity values by the area under the curve of the spectrum

    Not as easy as it looks like for first-derivative cwEPR spectra,
    as here, you are usually interested in normalising to the same area (
    *i.e.*, integral of the curve) of the absorptive (zeroth-derivative or
    zeroth harmonic) spectrum.

    At least given appropriate measurement conditions (no saturation, no line
    broadening due to overmodulation, proper phasing), the cwEPR signal
    intensity should be proportional to the number of spins in the active
    volume of the resonator/probehead. Therefore, with all crucial
    experimental parameters directly affecting the signal strength being
    equal (microwave power, modulation amplitude), normalising to same area
    should be the most straight-forward way of comparing two spectra in a
    meaningful way.

    Bare in mind, however, that spectra with strongly different overall line
    width will have dramatically different minima and maxima, making
    comparison of this kind sometimes less meaningful.


Besides these rather general ways of normalising spectra (although described
above particularly with cwEPR data in mind), there are some other
normalisations more particular to cwEPR spectroscopy:

  * Normalisation to same number of scans

    Some spectrometers (probably only older ones) did usually sum the
    intensity for each scan, rather than afterwards dividing by the number
    of scans, making comparison of spectra with different number of scans
    quite tricky.

    Make sure you know exactly what you do before applying (or not applying)
    such normalisation if you would like to do some kind of (semi-)quantitative
    analysis of your data.

  * Normalisation to same receiver gain

    The preamplifiers in the signal channel (as the digitising unit in cwEPR
    spectrometers is usually called) have usually a gain that can be
    adjusted to the signal strength of the actual sample. Of course,
    this setting will have a direct impact on the intensity values recorded (
    usually something like mV).

    Comparing spectra recorded with different receiver gain settings
    therefore requires the user to *first* normalise the data to the same
    receiver gain setting. Otherwise, (semi-)quantiative comparison is not
    possible and will lead to wrong conclusions.

    Note on the side: Adjusting the receiver gain for each measurement is
    highly recommended, as setting it too high will make the signal clip and
    distort the signal shape, and setting it too low will result in data
    with (unnecessary) poor signal-to-noise ratio.



Working with 2D datasets
------------------------

2D datasets in cwEPR spectroscopy, huh? Well, yes, more often than one might
expect in the beginning. There are the usual suspects such as power sweeps
and modulation amplitude sweeps, each varying (automatically) one parameter
in a given range and record spectra for each value.

There are, however, other types of 2D datasets that are quite useful in
cwEPR spectroscopy. Some vendors of EPR spectrometers offer no simple way of
saving each individual scan in a series of accumulations. However, this may
sometimes be of interest, particularly as a single "spike" due to some
external event or other malfunctioning may otherwise ruin your entire
dataset, however long it might have taken to record it. Therefore, one way
around this limitations is to perform a 2D experiment with repeated field
scans, but saving each scan as a row in a 2D dataset.

Generally, there are at least two different processing steps of interest for
2D datasets:

  * Projection along one axis

    Equivalent to averaging along that axis

    If recording multiple scans of one and the same spectrum for better
    signal-to-noise ratio, but saving each scan individually within a row of
    a 2D dataset, this is the way to get the dataset with improved
    signal-to-noise ratio originally intended.

    May as well be used for rotation patterns, *i.e.*, angular-dependent
    measurements, if there turns out to be no angular dependence in the
    data. In this case, at least you save the measurement time by having a
    dataset with clearly better signal-to-noise ratio than initially intended.

  * Extraction of a slice along one dimension

    Having a 2D dataset, we may often be interested in only one slice along
    one dimension.

    Typical examples would be comparing two positions of the goniometer
    (zero and 180 degree would be an obvious choice) or slices with similar
    parameters for different datasets.


More complicated and probably more involved processing of 2D datasets would
be to (manually) inspect the individual scans and decide which of those to
average, *e.g.* in case of one problematic scan in between, be it due to
external noise sources or spectrometer problems.


Handling multiple datasets
--------------------------

Comparing multiple datasets by plotting them in one and the same axis is a
rather simple way of handling multiple datasets. However, usually, you would
like to perform much more advanced operations on multiple datasets, such as
adding and subtracting one from the other.

May sound pretty simple at first, but is indeed pretty demanding in terms of
its implementation, as internally, you need to check for quite a number of
things, such as commensurable axes and ranges. However, this is a rather
general problem of all kinds of datasets, hence it may be that this
functionality eventually gets incorporated in the ASpecD framework.

Particularly in EPR spectroscopy, each measurement will have a unique
microwave frequency for which the data were recorded. Therefore, to combine
the numerical values of two datasets (subtract, add, average), you will
first need to correct them for same microwave frequency. This will generally
result in different field axes for different datasets. Furthermore,
some vendors like to record data with non-equidistant field axes as well,
making handling of those datasets additionally messy.

  * Subtract a dataset from another dataset

    Ensure the datasets are compatible in terms of their axes (dimension,
    quantity, unit, common area of values), subtract the common range of
    values and return only the subtracted (*i.e.*, usually truncated) dataset.

    A common use case for subtracting a dataset from another would be a
    resonator background signal independently recorded, or some other
    background signal such as the "glass signal" (from impurities in the
    glass tube you've used).

    Other, more advanced applications may involve subtracting the spectrum
    of a single species from that of a spectrum consisting this and other
    species. However, in such case be aware of the fact that the spectrum
    containing more than one species may not be a simple superposition of
    the spectra of the two independent species.

  * Add a dataset to another dataset

    Ensure the datasets are compatible in terms of their axes (dimension,
    quantity, unit, common area of values), add the common range of values
    together and return only the summed (*i.e.*, usually truncated) dataset.

  * Average two datasets

    Ensure the datasets are compatible in terms of their axes (dimension,
    quantity, unit, common area of values), average the common range of values
    together and return only the averaged (*i.e.*, usually truncated) dataset.

    A common use case if you performed several independent measurements of
    the same sample (with otherwise similar/comparable parameters) and would
    like to average for better signal-to-noise.


Other processing steps
----------------------

There may well be further types of processing steps the authors are currently
not aware of or didn't dare to document here.


Note to developers
==================

Processing steps can be based on analysis steps, but not inverse! Otherwise,
we get cyclic dependencies what should obviously be avoided in order to keep
code working.

Implementing own processing steps is rather straight-forward. For details,
see the documentation of the :mod:`aspecd.processing` module.


Bibliography
============

.. bibliography::
   :labelprefix: P:
   :keyprefix: proc-


Module documentation
====================

What  follows is the API documentation of each class implemented in this module.

"""
import numpy as np
import scipy.integrate
import scipy.interpolate
import scipy.signal

import aspecd.processing
from cwepr import utils


class FieldCorrection(aspecd.processing.SingleProcessingStep):
    """Correct magnetic field axis by a linear offset.

    Perform a linear field correction of the data with a correction value
    previously determined.

    Attributes
    ----------
    parameters['offset']: :class:`float`
        Offset to be added to the field axis values.


    See Also
    --------
    cwepr.analysis.FieldCalibration :
        Determine offset value for a magnetic field calibration


    .. versionchanged:: 0.2
        Renamed parameter ``correction_value`` to ``offset``

    """

    def __init__(self):
        super().__init__()
        self.parameters["offset"] = None
        self.description = "Linear field correction"

    def _perform_task(self):
        """Shift all field axis data points by the correction value."""
        for axis in self.dataset.data.axes:
            # TODO: Question: Better check for quantity rather than unit?
            #       (Difficult if not filled)
            # if axis.quantity == 'magnetic field'
            if axis.unit in ('mT', 'G'):
                self.dataset.data.axes[0].values += \
                    self.parameters["offset"]


class FrequencyCorrection(aspecd.processing.SingleProcessingStep):
    """Convert data of a given frequency to another given frequency.

    This is used to make spectra comparable.

    Attributes
    ----------
    self.parameters['frequency']
        Frequency to correct for.

        Default: 9.5

    """

    def __init__(self):
        super().__init__()
        self.parameters["frequency"] = 9.5
        self.description = "Correct magnetic field axis for given frequency"

    def _perform_task(self):
        """Perform the actual transformation / correction."""
        nu_target = self.parameters['frequency']
        for axis in self.dataset.data.axes:
            # TODO: Question: Better check for quantity rather than unit?
            #       (Difficult if not filled)
            # if axis.quantity == 'magnetic field'
            if axis.unit in ('mT', 'G'):
                axis.values = self._correct_field_for_frequency(nu_target,
                                                                axis.values)
                self._write_new_frequency()

    def _correct_field_for_frequency(self, nu_target=None,
                                     b_initial=None):
        """
        Calculate new field axis for given frequency.

        Parameters
        ----------
        nu_target : :class:`float`
            Frequency the magnetic field should be computed for

        b_initial : :class:`numpy.ndarray`
            Original field axis

        Returns
        -------
        b_target : :class:`numpy.ndarray`
            Computed field axis

        """
        nu_initial = self.dataset.metadata.bridge.mw_frequency.value
        b_target = (nu_target / nu_initial) * b_initial
        return b_target

    def _write_new_frequency(self):
        self.dataset.metadata.bridge.mw_frequency.value = \
            self.parameters['frequency']


class GAxisCreation(aspecd.processing.SingleProcessingStep):
    """Change magnetic field axis to *g* axis.

    Particularly when comparing EPR spectra recorded at different frequency
    bands, the only sensible way to directly compare these spectra is to
    transform their magnetic field axis to a *g* axis.

    .. note::
        If you only want to have a *g* axis appearing in your plots
        (additionally to your magnetic field axis), you can tell the
        plotters to add a *g* axis at the opposite side of your axes. See
        the documentation of the plotters in the :mod:`cwepr.plotting`
        module for more details.


    .. versionchanged:: 0.2
        axis quantity is set to "g value", correct calculation of *g* values

    """

    def __init__(self):
        super().__init__()
        self.description = "Convert magnetic field axis to g axis."

    def _perform_task(self):
        for axis in self.dataset.data.axes:
            if axis.unit == 'mT':
                mw_freq = self.dataset.metadata.bridge.mw_frequency.value
                axis.values = utils.convert_mT2g(axis.values, mw_freq=mw_freq)
                axis.unit = ''
                axis.quantity = 'g value'


class AutomaticPhaseCorrection(aspecd.processing.SingleProcessingStep):
    """Automatic phase correction via Hilbert transform.

    .. important::
        Experimental state: Other methods have been proven to provide a
        better and reliable phase correction.

    .. todo::
        Does not work properly. Already gives wrong values with simulated
        data without a hyperfine-coupling. Reimplement with other method...

    Adapted from the matlab functionality in the cwEPR-toolbox.
    """

    def __init__(self):
        super().__init__()
        # Public properties
        self.description = "Automatic phase correction via Hilbert transform"
        self.parameters['order'] = 1
        self.parameters['points_percentage'] = 10
        self.parameters['phase_angle'] = 0
        # private properties
        self._analytic_signal = None
        self._points_per_side = None
        self._area_under_curve = None

    def _perform_task(self):
        self._analytic_signal = scipy.signal.hilbert(self.dataset.data.data)
        self._find_initial_negative_area()
        self._find_best_phase()
        self._reconstruct_real_signal()
        self._print_results_to_command_line()

    def _find_initial_negative_area(self):
        """Get area/values below zero as indicator of the phase deviation."""
        ft_sig_tmp = self._analytic_signal
        if self.parameters['order'] > 0:
            # pylint: disable=unused-variable
            for j in range(self.parameters['order']):  # integrate j times
                ft_sig_tmp = scipy.integrate.cumtrapz(self._analytic_signal,
                                                      initial=0)
        ft_sig_tmp = self._baseline_correction(signal=np.real(ft_sig_tmp))
        elements_inf_zero = [x for x in ft_sig_tmp if x < 0]
        self._area_under_curve = abs(np.trapz(elements_inf_zero))

    def _baseline_correction(self, signal=None):
        signal = np.asarray(signal)
        signal_size = signal.size
        if len(signal.shape) > 1 and signal.shape[1] != 1:
            signal.transpose()
        self._points_per_side = \
            int(np.ceil((self.parameters['points_percentage'] / 100) *
                        signal_size))

        data_parts = self._extract_points(signal)
        x_axis_parts = self._extract_points(self.dataset.data.axes[0].values)
        coefficients = np.polyfit(x_axis_parts, data_parts,
                                  deg=self.parameters['order'])
        baseline = np.polyval(coefficients, self.dataset.data.axes[0].values)

        corrected_signal = signal - baseline
        if len(signal.shape) > 1 and signal.shape[1] != 1:
            corrected_signal = corrected_signal.transpose()
        return corrected_signal

    def _extract_points(self, values):
        # pylint: disable=invalid-unary-operand-type
        vector_parts = np.concatenate([values[:self._points_per_side],
                                       values[-self._points_per_side:]])
        return vector_parts

    def _find_best_phase(self):
        min_angle = -np.pi / 2
        max_angle = np.pi / 2
        # TODO: introduce parameter step width/number of points.
        angles = np.linspace(min_angle, max_angle, num=181)
        for angle in angles:
            rotated_signal = (np.exp(1j * angle) * self._analytic_signal)
            if self.parameters['order'] > 0:
                # pylint: disable=unused-variable
                for j in range(self.parameters['order']):
                    rotated_signal = scipy.integrate.cumtrapz(rotated_signal,
                                                              initial=0)
            rotated_signal = self._baseline_correction(signal=np.real(
                rotated_signal))
            elements_inf_zero = [x for x in rotated_signal if x < 0]
            area = abs(np.trapz(elements_inf_zero))
            if area < self._area_under_curve:
                self._area_under_curve = area
                self.parameters['phase_angle'] = angle

    def _reconstruct_real_signal(self):
        self.dataset.data.data = np.real(np.exp(1j * self.parameters[
            'phase_angle']) * self._analytic_signal)
        assert not np.iscomplex(self.dataset.data.data).all()

    def _print_results_to_command_line(self):
        phi_degree = self.parameters['phase_angle'] * 180 / np.pi
        print('Phase correction was done with phi = %.3f degree' % phi_degree)


class NormalisationOfDerivativeToArea(aspecd.processing.SingleProcessingStep):
    """Normalise a spectrum to the area under the curve.

    As typical cw-EPR spectra are derivative spectra, calculating the area
    under the curve involves an integration step beforehand. This is done
    here as well.

    .. note::
        If the integrated spectra has a baseline shift, it is not currently
        accounted for.
    """

    def __init__(self):
        super().__init__()
        self.description = "Normalisation to area"
        self.undoable = True
        self._area = float()

    def _perform_task(self):
        self._integrate_spectrum()
        self.dataset.data.data /= self._area

    def _integrate_spectrum(self):
        integrated_spectrum = \
            scipy.integrate.cumtrapz(self.dataset.data.data, initial=0)
        self._area = np.trapz(integrated_spectrum)


class Normalisation(aspecd.processing.Normalisation):
    """Normalise data.

    Additional to kinds implemented in the parent class, this class provides
    the following normalisations:

    * receiver_gain

      Normalise data to identical receiver gain

    * scan_number

      Normalise data to same number of scans

    For an extended documentation of the kinds implemented directly in
    ASpecD, see the corresponding documentation:
    :class:`aspecd.processing.Normalisation`.


    Some details for the two additional kinds of normalisation are given
    below.

    Due to the logarithmic scale of the **receiver gain** (in dB) at least in
    Bruker spectrometers, it has to be transferred into the "normal" scale. It
    calculates as following:

        receiver gain = 10^(receiver gain in dB/20)

    Source: Stefan Stoll, EasySpin source code, according to Xenon Manual 2011

    The normalisation according to the **number of scans** is necessary to make
    spectra in which the intensity of different scans is the sum of the
    single scans, comparable to those where it is averaged.

    .. important::

        Know what you are doing, as depending on the software used for
        recording your data, the data are already normalised with respect to
        the number of scans.


    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    To normalise your dataset(s) with respect to the receiver gain used:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             kind: receiver_gain


    To normalise your dataset(s) with respect to the number of scans that
    have been recorded:

    .. code-block:: yaml

       - kind: processing
         type: Normalisation
         properties:
           parameters:
             kind: scan_number

    """

    def _perform_task(self):
        if 'receiver' in self.parameters["kind"].lower():
            self._normalise_for_receiver_gain()
        elif 'scan_number' in self.parameters["kind"].lower():
            self.dataset.data.data \
                /= self.dataset.metadata.signal_channel.accumulations
        else:
            super()._perform_task()

    def _normalise_for_receiver_gain(self):
        receiver_gain = self.dataset.metadata.signal_channel.receiver_gain.value
        receiver_gain_value = 10 ** (receiver_gain / 20)
        self.dataset.data.data /= receiver_gain_value


class AxisInterpolation(aspecd.processing.SingleProcessingStep):
    """Interpolating axes to given number of equidistant field points.

    Iterates over axes and takes the first axis that is not equidistant and
    interpolates it and the data as well.

    Attributes
    ----------
    parameters['points']
        Number of points that should be interpolated to.

    """

    def __init__(self):
        super().__init__()
        self.description = 'Interpolate axis to get equidistant points.'
        self.parameters['points'] = None

    def _perform_task(self):
        for num, axis in enumerate(self.dataset.data.axes):
            if not axis.equidistant:
                if not self.parameters['points']:
                    self._get_axis_length(ax_nr=num)
                self._interpolate_axis(num)
                break

    def _interpolate_axis(self, ax_number=None):
        points = self.parameters['points']
        # Actual interpolation
        start = self.dataset.metadata.magnetic_field.start.value
        stop = self.dataset.metadata.magnetic_field.stop.value
        new_x_axis = np.linspace(start, stop, num=points)
        self.dataset.data.data = np.interp(new_x_axis, self.dataset.data.axes[
            ax_number].values, self.dataset.data.data)
        self.dataset.data.axes[ax_number].values = new_x_axis

    def _get_axis_length(self, ax_nr):
        self.parameters['points'] = len(self.dataset.data.axes[ax_nr].values)


class ScalarAlgebra(aspecd.processing.ScalarAlgebra):
    """Perform scalar algebraic operation on one dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.ScalarAlgebra`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add a fixed value of 42 to your dataset:

    .. code-block:: yaml

       - kind: processing
         type: ScalarAlgebra
         properties:
           parameters:
             kind: add
             value: 42

    Similarly, you could use "minus", "times", "by", "add", "subtract",
    "multiply", or "divide" as kind - resulting in the given algebraic
    operation.

    """


class ScalarAxisAlgebra(aspecd.processing.ScalarAxisAlgebra):
    """Perform scalar algebraic operation on the axis of a dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.ScalarAxisAlgebra`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add a fixed value of 42 to the first axis
    (index 0) your dataset:

    .. code-block:: yaml

       - kind: processing
         type: ScalarAxisAlgebra
         properties:
           parameters:
             kind: plus
             axis: 0
             value: 42

    Similarly, you could use "minus", "times", "by", "add", "subtract",
    "multiply", "divide", and "power" as kind - resulting in the given
    algebraic operation.

    """


class DatasetAlgebra(aspecd.processing.DatasetAlgebra):
    """Perform scalar algebraic operation on two datasets.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.DatasetAlgebra`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In case you would like to add the data of the dataset referred to by its
    label ``label_to_other_dataset`` to your dataset:

    .. code-block:: yaml

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset

    Similarly, you could use "minus", "add", "subtract" as kind - resulting
    in the given algebraic operation.

    As mentioned already, the data of both datasets need to have identical
    shape, and comparison is only meaningful if the axes are compatible as
    well. Hence, you will usually want to perform a CommonRangeExtraction
    processing step before doing algebra with two datasets:

    .. code-block:: yaml

       - kind: multiprocessing
         type: CommonRangeExtraction
         results:
           - label_to_dataset
           - label_to_other_dataset

       - kind: processing
         type: DatasetAlgebra
         properties:
           parameters:
             kind: plus
             dataset: label_to_other_dataset
         apply_to:
           - label_to_dataset

    """


class Projection(aspecd.processing.Projection):
    """Project data, *i.e.* reduce dimensions along one axis.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.Projection`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the projection with default values:

    .. code-block:: yaml

       - kind: processing
         type: Projection

    This will project the data along the first axis (index 0), yielding a 1D
    dataset.

    If you would like to project along the second axis (index 1), simply set
    the appropriate parameter:

    .. code-block:: yaml

       - kind: processing
         type: Projection
         properties:
           parameters:
             axis: 1

    This will project the data along the second axis (index 1), yielding a 1D
    dataset.

    """


class SliceExtraction(aspecd.processing.SliceExtraction):
    """Extract slice along one ore more dimensions from dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.SliceExtraction`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the slice extraction with an index only:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 5

    This will extract the sixth slice (index five) along the first axis (index
    zero).

    If you would like to extract a slice along the second axis (with index
    one), simply provide both parameters, index and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 5
             axis: 1

    This will extract the sixth slice along the second axis.

    And as it is sometimes more convenient to give ranges in axis values
    rather than indices, even this is possible. Suppose the axis you would
    like to extract a slice from runs from 340 to 350 and you would like to
    extract the slice corresponding to 343:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: 343
             unit: axis

    In case of you providing the range in axis units rather than indices,
    the value closest to the actual axis value will be chosen automatically.

    For ND datasets with N>2, you can either extract a 1D or ND slice,
    with N always at least one dimension less than the original data. To
    extract a 2D slice from a 3D dataset, simply proceed as above, providing
    one value each for position and axis. If, however, you want to extract a
    1D slice from a 3D dataset, you need to provide two values each for
    position and axis:

    .. code-block:: yaml

       - kind: processing
         type: SliceExtraction
         properties:
           parameters:
             position: [21, 42]
             axis: [0, 2]

    This particular case would be equivalent to ``data[21, :, 42]`` assuming
    ``data`` to contain the numeric data, besides, of course, that the
    processing step takes care of removing the axes as well.

    """


class BaselineCorrection(aspecd.processing.BaselineCorrection):
    """Subtract baseline from dataset.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.BaselineCorrection`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    In the simplest case, just invoke the baseline correction with default
    values:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection

    In this case, a zeroth-order polynomial baseline will be subtracted from
    your dataset using ten percent to the left and right, and in case of a
    2D dataset, the baseline correction will be performed along the first
    axis (index zero) for all indices of the second axis (index 1).

    Of course, often you want to control a little bit more how the baseline
    will be corrected. This can be done by explicitly setting some parameters.

    Suppose you want to perform a baseline correction with a polynomial of
    first order:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             order: 1

    If you want to change the (percental) area used for fitting the
    baseline, and even specify different ranges left and right:

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             fit_area: [5, 20]

    Here, five percent from the left and 20 percent from the right are used.

    Finally, suppose you have a 2D dataset and want to average along the
    second axis (index one):

    .. code-block:: yaml

       - kind: processing
         type: BaselineCorrection
         properties:
           parameters:
             axis: 1

    Of course, you can combine the different options.

    """


class Filtering(aspecd.processing.Filtering):
    """Filter data.

    As the class is fully inherited from ASpecD for simple usage, see the
    ASpecD documentation of the :class:`aspecd.processing.Filtering`
    class for details.

    Examples
    --------
    For convenience, a series of examples in recipe style (for details of
    the recipe-driven data analysis, see :mod:`aspecd.tasks`) is given below
    for how to make use of this class. The examples focus each on a single
    aspect.

    Generally, filtering requires to provide both, a type of filter and a
    window length. Therefore, for uniform and Gaussian filters, this would be:

    .. code-block:: yaml

       - kind: processing
         type: Filtering
         properties:
           parameters:
             type: uniform
             window_length: 10

    Of course, at least uniform filtering (also known as boxcar or moving
    average) is strongly discouraged due to the artifacts introduced.
    Probably the best bet for applying a filter to smooth your data is the
    Savitzky-Golay filter:

    .. code-block:: yaml

       - kind: processing
         type: Filtering
         properties:
           parameters:
             type: savitzky-golay
             window_length: 10
             order: 3

    Note that for this filter, you need to provide the polynomial order as
    well. To get best results, you will need to experiment with the
    parameters a bit.

    """
