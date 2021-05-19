"""Module containing the analysis steps of the cwEPR package.

.. sidebar::
    processing *vs.* analysis

    For more details on the difference between processing and analysis,
    see the `ASpecD documentation <https://docs.aspecd.de/>`_.


An analysis step, in contrast to a processing step, does not simply modify a
given dataset, but extracts some characteristic of this dataset that is
contained in its ``results`` property. This can be as simple as a number,
*e.g.*, in case of the signal-to-noise figure of a data trace, but as
complicated as a (calculated) dataset on its own containing some measure as
function of some parameter, such as the microwave frequency for each of a
series of recordings, allowing to visualise drifts that may or may not
impact data analysis.

.. note::
    This module may be split into different modules and thus converted into
    a subpackage at some point in the future, depending on the number of
    classes for analysis steps to come (but rather likely to happen).


.. todo::
    Reduce number of error classes, as many seem to be pretty generic,
    and make use of the messages if exceptions are thrown. Carefully revise
    methods.


.. todo::
    Make methods dealing with both, 1D and 2D datasets or raising the
    respective errors.


Note to developers
==================

Processing steps can be based on analysis steps, but not inverse! Otherwise,
we get cyclic dependencies what should obviously be avoided in order to keep
code working.
"""

import copy
import math
import numpy as np
import scipy.constants

import aspecd.analysis
import aspecd.dataset

from cwepr.exceptions import MissingInformationError


class FieldCorrectionValue(aspecd.analysis.SingleAnalysisStep):
    """Determine correction value for a field correction.

    As g standard reference, it can be chosen from two substances, LiLiF and
    DPPH using the parameter "standard".

    References for the constants:

    g value of Li:LiF::

        g(LiLiF) = 2.002293 +- 0.000002

    Reference: Rev. Sci. Instrum. 1989, 60, 2949-2952.

    g value of DPPH:

        g(DPPH) = 2.0036 ± 0.0002

    Reference: Appl. Magn. Reson. 10, 339-350 (1996)

    Attributes
    ----------
    parameters['standard'] : :class:`str`
        Field standard that should be applied.

        Default: LiLiF

    parameters['mw_frequency'] : :class:`float`
        Microwave frequency to be corrected for. In general, is taken from the
        dataset what is recommended but can also be given.

    Raises
    ------
    MissingInformationError
        Raised if no microwave frequency is given neither in the dataset nor
        as parameter.

    """

    G_LILIF = 2.002293
    G_DPPH = 2.0036

    def __init__(self):
        super().__init__()
        self.parameters['mw_frequency'] = None
        self.parameters['standard'] = 'LiLiF'
        self.description = "Determination of a field correction value"
        self._g_correct = None

    def _perform_task(self):
        """Wrapper around field correction value determination method."""
        self._get_mw_frequency()
        self._get_sample_g_value()
        self.result = self._get_field_correction_value()

    def _get_mw_frequency(self):
        if not self.parameters['mw_frequency'] and not \
                self.dataset.metadata.bridge.mw_frequency.value:
            raise MissingInformationError(message='No microwave frequency '
                                                  'provided, aborting.')
        if not self.parameters['mw_frequency']:
            self.parameters['mw_frequency'] = \
                self.dataset.metadata.bridge.mw_frequency.value

    def _get_field_correction_value(self):
        """Calculates a field correction value.

        Finds the zero-crossing of a (derivative) spectrum of a field
        standard by using the difference between minimum and maximum part of the
        signal. This value is then subtracted from the the expected field
        value for the MW frequency provided.

        Returns
        -------
        delta_b0: :class:`float`
            Field correction value

        """
        i_max = np.argmax(self.dataset.data.data)
        i_min = np.argmin(self.dataset.data.data)
        zero_crossing_exp = (self.dataset.data.axes[0].values[i_min] +
                             self.dataset.data.axes[0].values[i_max]) / 2
        calculated_field = \
            scipy.constants.value('Planck constant') \
            * self.parameters['mw_frequency'] * 1e9 * 1e3 / \
            (self._g_correct * scipy.constants.value('Bohr magneton'))
        delta_b0 = calculated_field - zero_crossing_exp
        return delta_b0

    def _get_sample_g_value(self):
        if 'standard' in self.parameters.keys():
            if self.parameters['standard'].lower() == 'dpph':
                self._g_correct = self.G_DPPH
            elif self.parameters['standard'].lower() == 'lilif':
                self._g_correct = self.G_LILIF
            else:
                print('This g-standard sample is not listed, LiLiF is chosen '
                      'automatically.')


class LinewidthPeakToPeak(aspecd.analysis.SingleAnalysisStep):
    """Linewidth measurement (peak to peak in derivative).

    .. todo::
        Combine all linewidth classes into one with a switch for the method
        to use?

        However: FWHM can only be used as linewidth measure in absorptive
        spectra, not in derivative-shape spectra. Perhaps therefore rename
        to Peak2PeakDistance or similar?

    """

    def __init__(self):
        super().__init__()
        self.description = "Determine peak-to-peak linewidth"

    def _perform_task(self):
        self.result = self.get_peak_to_peak_linewidth()

    @staticmethod
    def applicable(dataset):  # noqa: D102
        return isinstance(dataset.data.data.size, int)

    def get_peak_to_peak_linewidth(self):
        """Calculates the peak-to-peak linewidth.

        This is done by determining the distance between the maximum and the
        minimum in the derivative spectrum which should yield acceptable
        results in a symmetrical signal. Limitation: Spectrum contains only
        one line.

        Returns
        -------
        linewidth: :class:`float`
            peak to peak linewidth

        """
        index_max = np.argmax(self.dataset.data.data)
        index_min = np.argmin(self.dataset.data.data)
        linewidth = abs(self.dataset.data.axes[0].values[index_min] -
                        self.dataset.data.axes[0].values[index_max])
        return linewidth


class LinewidthFWHM(aspecd.analysis.SingleAnalysisStep):
    """Full linewidth at half maximum."""

    def __init__(self):
        super().__init__()
        self.description = "Determine linewidth (full width at half max; FWHM)"

    def _perform_task(self):
        self.result = self.get_fwhm_linewidth()

    def get_fwhm_linewidth(self):
        """Calculates the line width (full width at half maximum, FWHM).

        This is done by subtracting maximum/2, building the absolute value
        and then determining the minima. The distance between these points
        corresponds to the FWHM linewidth.

        Returns
        -------
        linewidth: :class:`float`
            line width as determined

        """
        index_max = np.argmax(self.dataset.data.data)
        spectral_data = copy.deepcopy(self.dataset.data.data)

        spectral_data -= max(spectral_data) / 2
        spectral_data = abs(spectral_data)

        left_zero_cross_index = np.argmin(spectral_data[:index_max])
        right_zero_cross_index = np.argmin(spectral_data[index_max:])
        b_field_left = self.dataset.data.axes[0].values[left_zero_cross_index]
        b_field_right = self.dataset.data.axes[0].values[right_zero_cross_index]
        return b_field_right - b_field_left


class SignalToNoiseRatio(aspecd.analysis.SingleAnalysisStep):
    """Get a spectrum's signal to noise ratio.

    This is done by comparing the absolute maximum of the spectrum to the
    maximum of the edge part of the spectrum (i.e. a part which is considered
    to not contain any signal.

    Attributes
    ----------
    parameters['percentage']: :class:`int`
        percentage of the spectrum to be considered edge part on any side
        (i.e. 10 % means 10 % on each end).

        Default: 10 %

    """

    def __init__(self):
        super().__init__()
        self.parameters["percentage"] = 10
        self.description = "Determine signal to noise ratio."

    def _perform_task(self):
        """Determine signal to noise ratio.

        Call method to get the amplitude of the noise, compare it to the
        absolute amplitude and set a result.
        """
        signal = self.dataset.data.data
        noise = self._get_noise()

        noise_amplitude = self._get_amplitude(noise)
        signal_amplitude = self._get_amplitude(signal) - noise_amplitude

        self.result = signal_amplitude / noise_amplitude

    @staticmethod
    def _get_amplitude(data=None):
        return max(data) - min(data)

    def _get_noise(self):
        number_of_points = math.ceil(len(self.dataset.data.data) *
                                     self.parameters["percentage"] / 100.0)
        noise_data = np.append(self.dataset.data.data[:number_of_points],
                               self.dataset.data.data[-number_of_points:])
        return noise_data


class Amplitude(aspecd.analysis.SingleAnalysisStep):
    """Determine amplitude of dataset.

    Depending of the dimension of the dataset, the returned value is either
    a scalar (1D dataset) or a vector (2D dataset) containing the amplitude of
    each row respectively.

    Returns
    -------
    result
        amplitude(s) row-wise, thus scalar or vector.

    """

    def __init__(self):
        super().__init__()
        self.description = "Get amplitude of (derivative) spectrum."

    def _perform_task(self):
        if len(self.dataset.data.axes) == 2:
            self.result = max(self.dataset.data.data) - min(
                self.dataset.data.data)
        else:
            self.result = np.amax(self.dataset.data.data, axis=0) - np.amin(
                self.dataset.data.data, axis=0)


class AmplitudeVsPower(aspecd.analysis.SingleAnalysisStep):
    """Return a calculated dataset to further analyse a power-sweep experiment.

    The analysis of a power sweep results in a plot of the peak amplitude
    vs. the square root of the microwave power of the bridge. Both values
    are determined in this step and put together in a calculated dataset
    that can be used subsequently to perform the linear fit.

    Returns
    -------
    result: :class:`aspecd.dataset.CalculatedDataset`
       Calculated Dataset where the data is the amplitude and the axis
       values is the root of the mw-power (in ascending order).

    """

    def __init__(self):
        super().__init__()
        self.description = "Return calculated dataset for power sweep analysis."
        self.result = aspecd.dataset.CalculatedDataset()
        # private properties
        self._analysis = Amplitude()
        self._roots_of_mw_power = np.ndarray([])

    @staticmethod
    def applicable(dataset):  # noqa: D102
        return len(dataset.data.axes) > 2

    def _perform_task(self):
        self._calculate_data_and_axis()
        self._check_mw_axis()
        self._assign_data_to_result()
        self._assign_units_to_result()

    def _calculate_data_and_axis(self):
        self._roots_of_mw_power = np.sqrt(self.dataset.data.axes[1].values)
        amplitude = Amplitude()
        self._analysis = self.dataset.analyse(amplitude)

    def _check_mw_axis(self):
        """Check for ascending order.

        If not, revert both, root of mw-power and amplitude.
        """
        if self._roots_of_mw_power[-1] - self._roots_of_mw_power[0] < 0:
            self._roots_of_mw_power = self._roots_of_mw_power[::-1]
            self._analysis.result = self._analysis.result[::-1]

    def _assign_data_to_result(self):
        self.result.data.data = self._analysis.result
        self.result.data.axes[0].values = self._roots_of_mw_power

    def _assign_units_to_result(self):
        if self.dataset.data.axes[1].unit == 'mW':
            self.result.data.axes[0].unit = 'sqrt(mW)'
        elif self.dataset.data.axes[1].unit == 'W':
            self.result.data.axes[0].unit = 'sqrt(W)'
        self.result.data.axes[0].quantity = 'root of mw power'


class PolynomialFitOnData(aspecd.analysis.SingleAnalysisStep):
    """Perform polynomial fit on data and return its parameters or a dataset.

    Developed tests first.

    Attributes
    ----------
    parameters['points']
        first n points that should taken into account

        Default: 3

    parameters['order']
        order of the fit.

        Default: 1

    parameters['return_type'] : :class: `str`
        Choose to returning the coefficients of the fit or a calculated
        dataset containing the curve to plot.

        Default: coefficients.

        Valid values: 'coefficients', 'dataset'

    parameters['add_origin'] : :class: `bool`
        Adds the point (0,0) to the data and axes, but  does not guarantee
        the fit really passes the origin.

        Default: False.

    """

    def __init__(self):
        super().__init__()
        self.description = "Perform polynomial fit and return parameters."
        self.result = None
        self.parameters['points'] = 3
        self.parameters['order'] = 1
        self.parameters['return_type'] = 'coefficients'
        self.parameters['add_origin'] = False
        self.parameters['coefficients'] = []
        # private properties
        self._curve = None

    def _perform_task(self):
        if self.parameters['add_origin']:
            self._add_origin()
        self._get_coefficients()
        self._get_curve()
        self._assign_result()

    def _get_coefficients(self):
        x_data_to_process = \
            self.dataset.data.axes[0].values[:self.parameters['points']]
        y_data_to_process = self.dataset.data.data[:self.parameters['points']]
        self.parameters['coefficients'] = \
            np.polyfit(x_data_to_process, y_data_to_process, self.parameters[
                'order'])

    def _get_curve(self):
        self._curve = self.create_dataset()
        self._curve.data.axes[0] = self.dataset.data.axes[0]
        self._curve.data.data = np.polyval(self.parameters['coefficients'],
                                           self.dataset.data.axes[0].values)
        self._curve.data.axes[0].values = self.dataset.data.axes[0].values

    def _assign_result(self):
        if self.parameters['return_type'].lower() == 'dataset':
            self.result = self._curve
        else:
            self.result = self.parameters['coefficients']

    def _add_origin(self):
        self.dataset.data.axes[0].values = \
            np.insert(self.dataset.data.axes[0].values, 0, 0)
        self.dataset.data.data = np.insert(self.dataset.data.data, 0, 0)


class PtpVsModAmp(aspecd.analysis.SingleAnalysisStep):
    """Create calculated dataset for modulation sweep analysis."""

    def __init__(self):
        super().__init__()
        self.description = 'Create dataset with ptp-linewidth vs modulation ' \
                           'Amplitude.'
        self.new_dataset = aspecd.dataset.CalculatedDataset()
        self.linewidths = np.ndarray([0])

    def _perform_task(self):
        self._get_linewidths()
        self._fill_dataset()
        self.result = self.new_dataset

    @staticmethod
    def applicable(dataset):  # noqa: D102
        return len(dataset.data.axes) > 2

    def _get_linewidths(self):
        for line in self.dataset.data.data:
            index_max = np.argmax(line)
            index_min = np.argmin(line)
            linewidth = abs(self.dataset.data.axes[1].values[index_min] -
                            self.dataset.data.axes[1].values[index_max])
            self.linewidths = np.append(self.linewidths, linewidth)

    def _fill_dataset(self):
        self.new_dataset.data.data = self.linewidths
        self.new_dataset.data.axes[0] = self.dataset.data.axes[1]
        self.new_dataset.data.axes[1].unit = self.dataset.data.axes[0].unit
        self.new_dataset.data.axes[1].quantity = 'peak to peak linewidth'


class AreaUnderCurve(aspecd.analysis.SingleAnalysisStep):
    """Make definite integration, i.e. calculate the area under the curve.

    Takes no other parameters.
    """

    def __init__(self):
        super().__init__()
        self.description = "Definite integration / area und the curve"

    def _perform_task(self):
        """Perform the actual integration.

        The x values from the dataset are used.
        """
        x_values = self.dataset.data.axes[0].values
        y_values = self.dataset.data.data

        self.result = np.trapz(y_values, x_values)
