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


Currently, the following processing steps are implemented:

  * :class:`FieldCorrection`
  * :class:`FrequencyCorrection`

  * :class:`BaselineCorrectionWithPolynomial`
  * :class:`BaselineCorrectionWithCalculatedDataset`

  * :class:`NormalisationToMaximum`
  * :class:`NormalisationToPeakToPeakAmplitude`
  * :class:`NormalisationOfDerivativeToArea`
  * :class:`NormalisationToScanNumber`
  * :class:`NormalisationToReceiverGain`

  * :class:`Integration`

  * :class:`Averaging2DDataset`
  * :class:`SubtractVector`

Implemented but not working as they should:

  * :class:`PhaseCorrection`
  * :class:`AutomaticPhaseCorrection`


Categories of processing steps
==============================

Processing steps can be categorised further. The following is an attempt to
do that for cwEPR data and at the same time a list of processing steps one
would like to have implemented. Besides that, it seems that this list
evolves more and more towards a summary of how to properly record and
(post-)process cwEPR data.

For more authoritative answers, you may as well have a look into the EPR
literature, particularly the "EPR Primer" by Chechik/Carter/Murphy and
the book on quantitative EPR by the Eatons.

.. todo::
    Add references here, using the BIBTeX plugin


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

    Algebra is available directly via the ASpecD Module:
    :class:`aspecd.processing.ScalarAlgebra`

Comparing datasets often involves adding, subtracting, multiplying or
dividing the intensity values by a given fixed number. This is very simple
algebra and should probably be implemented in the ASpecD framework eventually.

Possible scenarios where one wants to multiply the intensity values of a
cwEPR spectrum may be comparing spectra resulting from a single species from
those of known two species, different (known) concentrations and alike.

Of course, dividing the intensity of the spectrum by the maximum intensity
is another option, however, this would be normalisation to maximum (not
always a good idea, usually normalising to area or amplitude is better),
and this is handled by a different set of processing steps (see below).

.. note::
    This type of simple algebra is quite *different* from adding or
    subtracting datasets together. Whereas simple algebra really is a
    one-liner in terms of implementation, handling different datasets
    involves ensuring commensurable axis dimensions and ranges, to say the
    least.




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


Module documentation
====================

What  follows is the API documentation of each class implemented in this module.

"""
import copy
import math
import numpy as np
import scipy.constants
import scipy.integrate
import scipy.interpolate
import scipy.signal

import aspecd.processing


class Error(Exception):
    """Base class for exceptions in this module."""


class DimensionError(Error):
    """Exception indicating error in the dimension of an object.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class FieldCorrection(aspecd.processing.SingleProcessingStep):
    """Processing step for field correction.

    Perform a linear field correction of the data with a correction value
    previously determined.

    .. todo::
        Check that the correct axis gets corrected, meaning that it should
        be a magnetic field axis having the correct unit for the correction
        value.

    Attributes
    ----------
    parameters['correction_value']: :class:`float`
        Previously determined correction value.

    """

    def __init__(self):
        super().__init__()
        self.parameters["correction_value"] = None
        self.description = "Linear field correction"

    def _perform_task(self):
        """Shift all field axis data points by the correction value."""
        for data_index, _ in enumerate(self.dataset.data.data):
            self.dataset.data.axes[0].values[data_index] += \
                self.parameters["correction_value"]


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
        """Perform the actual transformation / correction.

        For the conversion the x axis data is first converted to an axis in
        units of using the given frequency, then converted back using target
        frequency.
        """
        nu_target = self.parameters['frequency']
        for axis in self.dataset.data.axes:
            # TODO: Question: Better check for quantity rather than unit? (
            #   Difficult if not filled)
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
    """Change magnetic field axis to g axis.

    Attributes
    ----------
    self.parameters['frequency']
        frequency to calculate g axis with.

    """

    def __init__(self):
        super().__init__()
        self.parameters["frequency"] = 9.5
        self.description = "Return a g-axis."

    def _perform_task(self):
        for axis in self.dataset.data.axes:
            if axis.unit in ('mT', 'G'):
                axis.values = self._create_g_axis(axis.values)
                axis.unit = ''

    def _create_g_axis(self, field_values=None):
        planck_constant = scipy.constants.value('Planck constant')
        mu_b = scipy.constants.value('electron mag. mom.')
        # pylint: disable=invalid-name
        nu = self.dataset.metadata.bridge.mw_frequency.value
        g_ = (planck_constant * nu) / (mu_b * field_values)
        return g_


class BaselineCorrectionWithPolynomial(aspecd.processing.SingleProcessingStep):
    """Perform a baseline correction assuming an underlying polynomial function.

    The coefficients to use will be calculated using the given order  and
    written in the parameters. If no order is explicitely given, a shifted
    baseline of zeroth order is assumed and will be processed for.
    See also: :class:`cwepr.analysis.BaselineCorrectionWithCalculatedDataset`.

    Attributes
    ----------
    parameters : :class:`dict`
        All parameters necessary for this step.

        percentage :
            Parts of the spectrum to be considered as baseline, can be given
            as list or single number. If one number is given, it takes that
            percentage from both sides, respectively, i.e. 10 means 10% left
            and 10 % right. If a list of two numbers is provided,
            the corresponding percentages are taken from each side of the
            spectrum, i.e. ``[5, 20]`` takes 5% from the left side and 20%
            from the right.

            Default: [10, 10]

        order : :class:`int`
            The order for the baseline correction if no coefficients are given.

            Default: 0

        coefficients:
            Filled during evaluation of the task, coefficients of the
            baseline polynomial.

    """

    def __init__(self):
        super().__init__()
        self.description = "Subtraction of baseline polynomial"
        self.parameters['percentage'] = [10, 10]
        self.parameters['order'] = 0
        self._cut_x_data = np.ndarray([])
        self._cut_y_data = np.ndarray([])
        self.parameters['coefficients'] = None

    @staticmethod
    def applicable(dataset):  # noqa: D102
        return dataset.data.data.ndim == 1

    def _sanitise_parameters(self):
        if isinstance(self.parameters['percentage'], (float, int)):
            percentage = self.parameters['percentage']
            self.parameters['percentage'] = [percentage, percentage]
        if isinstance(self.parameters['percentage'], list) and len(
                self.parameters['percentage']) == 1:
            percentage = self.parameters['percentage'][0]
            self.parameters['percentage'] = [percentage, percentage]

    def _perform_task(self):
        """Perform the actual correction.

        Baseline correction is performed by subtraction of  an evaluated
        polynomial.
        """
        self._get_spectrum_to_evaluate()
        values_to_subtract = self._get_values_to_subtract()
        self.dataset.data.data -= values_to_subtract

    def _get_spectrum_to_evaluate(self):
        number_of_points = len(self.dataset.data.data)
        points_left = math.ceil(number_of_points * self.parameters[
            "percentage"][0] / 100.0)
        points_right = math.ceil(number_of_points * self.parameters[
            "percentage"][1] / 100.0)
        data = self.dataset.data.data
        x_axis = self.dataset.data.axes[0].values
        self._cut_y_data = np.r_[data[:points_left], data[-points_right:]]
        self._cut_x_data = np.r_[x_axis[:points_left], x_axis[-points_right:]]

    def _get_values_to_subtract(self):
        if np.polynomial.Polynomial:
            polynomial = np.polynomial.Polynomial.fit(self._cut_x_data,
                                                      self._cut_y_data,
                                                      self.parameters['order'])
            self.parameters['coefficients'] = polynomial.coef
            return polynomial(self.dataset.data.axes[0].values)
        polynomial = np.polyfit(self._cut_x_data, self._cut_y_data,
                                self.parameters['order'])
        self.parameters['coefficients'] = polynomial
        return np.polyval(polynomial, self.dataset.data.axes[0].values)


class BaselineCorrectionWithCalculatedDataset(aspecd.processing.SingleProcessingStep):
    """Perform a baseline correction using a baseline previously determined.

    Uses a dataset with the respective baseline as data.
    See also: :class:`cwepr.analysis.BaselineCorrectionWithPolynomial`.

    Attributes
    ----------
    parameters['baseline_dataset']: :class:`cwepr.dataset.ExperimentalDataset`
        Dataset containing the baseline to subtract.

    """

    def __init__(self, baseline_dataset=None):
        super().__init__()
        self.parameters["baseline_dataset"] = baseline_dataset
        self.description = "Subtraction of baseline dataset"

    def _perform_task(self):
        """Perform the actual correction.

        Baseline correction is performed by subtraction of  a baseline dataset.
        """
        self.dataset.data.data -= self.parameters["baseline_dataset"].data.data


class PhaseCorrection(aspecd.processing.SingleProcessingStep):
    """Phase correction if phase angle is given directly or in metadata.

    Therefore the here used implementation of the processing step is also
    highly problematic as most phase deviation is not introduced on purpose
    and listed in the metadata.

    Attributes
    ----------
    parameters : :class:`dict`
        phase_angle_value: :class:`float`
            Value of the phase shift, can be given in Degree or Rad

        phase_angle_unit: :class:`str`
            Unit of the phase shift.

            Default: deg

    """

    def __init__(self):
        super().__init__()
        self.description = "Phase Correction via Hilbert transform"
        self.parameters["phase_angle_value"] = None
        self.parameters["phase_angle_unit"] = 'deg'

    def _perform_task(self):
        """Perform the actual phase correction.

        The phase angle is acquired from the dataset's metadata and
        transformed to radians if necessary. The phase correction is then
        applied and the corrected data inserted into the dataset.
        """
        if not self.parameters["phase_angle_value"]:
            self._get_phase_from_metadata()
        self._convert_deg_to_rad()
        self._do_phase_correction()

    def _do_phase_correction(self):
        data = self.dataset.data.data
        analytic_signal = scipy.signal.hilbert(data)
        corrected_analytic_signal = np.exp(-1j * self.parameters[
            "phase_angle_value"]) * analytic_signal 
        corrected_data = np.real(corrected_analytic_signal)
        self.dataset.data.data = corrected_data

    def _convert_deg_to_rad(self):
        if self.parameters["phase_angle_unit"] == "deg":
            self.parameters["phase_angle_value"] = \
                (np.pi * self.parameters["phase_angle_value"]) / 180
            self.parameters["phase_angle_unit"] = "rad"

    def _get_phase_from_metadata(self):
        phase_angle_raw = self.dataset.metadata.signal_channel.phase
        self.parameters["phase_angle_value"] = phase_angle_raw.value
        self.parameters["phase_angle_unit"] = phase_angle_raw.unit


class AutomaticPhaseCorrection(aspecd.processing.SingleProcessingStep):
    """Automatic phase correction via Hilbert transform.

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


class NormalisationToMaximum(aspecd.processing.SingleProcessingStep):
    """Normalise a spectrum to the intensity of the maximum.

    Should only be used upon an integrated spectrum.
    """

    def __init__(self):
        super().__init__()
        self.description = "Normalisation to maximum"
        self.undoable = True

    def _perform_task(self):
        maximum = max(self.dataset.data.data)
        self.dataset.data.data /= maximum


class NormalisationToPeakToPeakAmplitude(aspecd.processing.SingleProcessingStep):
    """Normalise a spectrum to the amplitude between maximum and minimum."""

    def __init__(self):
        super().__init__()
        self.description = "Normalisation to peak to peak amplitude"
        self.undoable = True

    def _perform_task(self):
        maximum = max(self.dataset.data.data)
        minimum = abs(min(self.dataset.data.data))
        peak_to_peak_amplitude = maximum + minimum
        self.dataset.data.data /= peak_to_peak_amplitude


class NormalisationOfDerivativeToArea(aspecd.processing.SingleProcessingStep):
    """Normalise a spectrum to the area under the curve.

    No other (processing) modules are used in order to keep original data.

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


class NormalisationToScanNumber(aspecd.processing.SingleProcessingStep):
    """Normalise a spectrum concerning the number of scans used.

    This is necessary to make spectra in which the intensity of different scans
    is the sum of the single scans, comparable to those where it is averaged.

    .. important::
        Know what you are doing, sometimes spectrometer software does this
        step for you silently...

    Attributes
    ----------
    parameters["scan_number"]
        Number of accumulations.

    """

    def __init__(self):
        super().__init__()
        self.description = "Normalisation to scan number"
        self.parameters["scan_number"] = None

    def _perform_task(self):
        if not self.parameters['scan_number']:
            self.parameters['scan_number'] = \
                self.dataset.metadata.signal_channel.accumulations

        self.dataset.data.data /= self.parameters["scan_number"]


class NormalisationToReceiverGain(aspecd.processing.SingleProcessingStep):
    """Normalise a spectrum to to receiver gain.

    Due to the logarithmic scale of the receiver gain at least in BRUKER
    spectrometers, it has to be transferred into the "normal" scale. It
    calculates as following:

        receiver gain = 10^(receiver gain in dB/20)

    Source: Stefan Stoll, EasySpin source code, according to Xenon Manual 2011


    Attributes
    ----------
    parameters['receiver_gain']
        Receiver gain in dB. Is taken from metadata if not given.

    """

    def __init__(self):
        super().__init__()
        self.description = "Normalisation to receiver gain"
        self.parameters['receiver_gain'] = None

    def _perform_task(self):
        if not self.parameters['receiver_gain']:
            self.parameters['receiver_gain'] = \
                self.dataset.metadata.signal_channel.receiver_gain.value
        receiver_gain = 10 ** (self.parameters['receiver_gain'] / 20)
        self.dataset.data.data /= receiver_gain


class Integration(aspecd.processing.SingleProcessingStep):
    """Perform an indefinite integration.

    Indefinite integration means integration yielding an integral function.
    The quality of the integration can be determined using
    :class:`cwepr.analysis.IntegrationVerification`
    """

    def __init__(self):
        super().__init__()
        self.description = "Indefinite Integration"

    def _perform_task(self):
        """Perform the actual integration.

        Perform the actual integration using trapezoidal integration
        functionality from scipy. The keyword argument initial=0 is used to
        yield a list of length identical to the original one.
        """
        x_coordinates = self.dataset.data.axes[0].values
        y_coordinates = self.dataset.data.data

        integral_values = \
            scipy.integrate.cumtrapz(y_coordinates, x_coordinates, initial=0)
        self.dataset.data.data = integral_values


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
        self.description = 'Interpolate magnetic field axis to get ' \
                           'equidistant field points.'
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


class Averaging2DDataset(aspecd.processing.SingleProcessingStep):
    """Average over 2D dataset to get one dimensional dataset.

    Attributes
    ----------
    parameters['axis']
        Axis along which should be averaged.

        Default: 1

    """

    def __init__(self):
        super().__init__()
        self.parameters['axis'] = 1
        self.description = 'Project 2D data in one dimension.'
        self.undoable = True

    def _perform_task(self):
        old_dataset = copy.deepcopy(self.dataset)
        self.dataset.data.data = np.average(self.dataset.data.data,
                                            axis=self.parameters['axis'])
        if self.parameters['axis'] == 1:
            self.dataset.data.axes[1] = old_dataset.data.axes[2]
            del self.dataset.data.axes[2]

    @staticmethod
    def applicable(dataset):  # noqa: D102
        return len(dataset.data.axes) == 3


class SubtractVector(aspecd.processing.SingleProcessingStep):
    """Subtract vector of same length from dataset.

    With a 2D dataset, the vector is subtracted from

    Attributes
    ----------
    parameters['vector']
        Vector that is subtracted from the data

    """

    def __init__(self):
        super().__init__()
        self.description = 'Subtract vector of same length from dataset.'
        self.parameters['vector'] = []

    def _perform_task(self):
        if len(self.parameters['vector']) != \
                self.dataset.data.data.shape[0]:
            raise DimensionError(message='Vector to subtract is not of the '
                                         'same length as dataset.')
        if self.dataset.data.data.ndim == 1:
            self.dataset.data.data -= self.parameters['vector']
        elif self.dataset.data.data.ndim == 2:
            for second_dim in range(self.dataset.data.data.shape[1]):
                self.dataset.data.data[:, second_dim] -= \
                    self.parameters['vector']
        else:
            raise DimensionError(message='Dataset has weird shape.')
