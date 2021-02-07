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


class MissingInformationError(Error):
    """Exception raised when not enough information is provided."""

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ValuesNotIncreasingError(Error):
    """Exception raised when x values are not decreasing.

    Values given for the common space determination should always be in
    increasing order.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class DefinitionRangeDeterminationError(Error):
    """Exception raised when common definition range can't be determined.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class NoCommonRangeError(Error):
    """Exception raised when common definition range is zero.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class SpectrumNotIntegratedError(Error):
    """Exception raised when definite integration is used accidentally.

    Definite integration should only be performed on a derivative spectrum.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


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


class PolynomialBaselineFitting(aspecd.analysis.SingleAnalysisStep):
    """Analysis step_width for finding a baseline correction polynomial.

    An actual correction with the respective polynomial can be performed
    afterwards using :class:`cwepr.processing.BaselineCorrectionWithPolynomial`.

    Attributes
    ----------
    parameters['order']: :class:`int`
        Order of the polynomial.

        Default: 0

    parameters['percentage']: :class:`int`
        Percentage of the spectrum to consider as baseline on each side of the
        spectrum, i.e. 10% means 10% left and 10 % right.

        Default: 10 %

    """

    def __init__(self):
        super().__init__()
        self.parameters["order"] = 0
        self.parameters["percentage"] = 10
        self.result = None
        self.description = "Coefficients of polynomial fitted to baseline"

    def _perform_task(self):
        """Wrapper around polynomial determination."""
        self.result = self._find_polynomial_by_fit()

    def _find_polynomial_by_fit(self):
        """Perform a polynomial fit on the baseline.

        Assemble the data points of the spectrum to consider and use a numpy
        polynomial fit on these points.
        """
        number_of_points = len(self.dataset.data.data)
        points_per_side = \
            math.ceil(number_of_points * self.parameters["percentage"] / 100.0)

        data_list_y = copy.deepcopy(self.dataset.data.data).tolist()
        data_list_x = (copy.deepcopy(self.dataset.data.axes[0].values)).tolist()
        points_to_use_x = self._get_points_to_use(data_list_x, points_per_side)
        points_to_use_y = self._get_points_to_use(data_list_y, points_per_side)
        coefficients = np.polyfit(
            np.asarray(points_to_use_x), np.asarray(points_to_use_y),
            self.parameters["order"])
        return coefficients

    @staticmethod
    def _get_points_to_use(data, points_per_side):
        """Get a number of points from the spectrum to use for a fit.

        Slice the list of all data points to have a list of points from each
        side of the spectrum to use for polynomial fitting.

        Parameters
        ----------
        data: :class:`list`
            List from which points should be used on each side.

        points_per_side: :class:'int'
            How many points from each end of the list should be used.

        Returns
        -------
        points_to_use: :class:`list`
            List only containing the correct number of points from each side
            and not the points in between.

        """
        left_part = data[:points_per_side + 1]
        right_part = data[- points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use


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
    def applicable(dataset):
        return type(dataset.data.data.size) == int

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
            self.result = max(self.dataset.data.data) - \
                          min(self.dataset.data.data)
        else:
            self.result = np.amax(self.dataset.data.data, axis=0) - \
                          np.amin(self.dataset.data.data, axis=0)


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
    def applicable(dataset):
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
        """Check for ascending order, if not, revert both, root of mw-power
        and amplitude."""
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
        self.description = "Perform linear fit and return parameters."
        self.result = None
        self.parameters['points'] = 3
        self.parameters['order'] = 1
        self.parameters['return_type'] = 'coefficients'
        self.parameters['add_origin'] = False
        # private properties
        self._coefficients = []
        self._curve = aspecd.dataset.CalculatedDataset()

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
        self._coefficients = np.polyfit(x_data_to_process,
                                        y_data_to_process,
                                        self.parameters['order'])

    def _get_curve(self):
        self._curve.data.axes[0] = self.dataset.data.axes[0]
        self._curve.data.data = np.polyval(self._coefficients,
                                           self.dataset.data.axes[0].values)
        self._curve.data.axes[0].values = self.dataset.data.axes[0].values
        self._curve.metadata.calculation.parameters['coefficients'] = \
            self._coefficients

    def _assign_result(self):
        if self.parameters['return_type'].lower() == 'dataset':
            self.result = self._curve
        else:
            self.result = self._coefficients

    def _add_origin(self):
        self.dataset.data.data = np.insert(self.dataset.data.data, 0, 0)
        self.dataset.data.axes[0].values = np.insert(self.dataset.data.axes[
                                                    0].values, 0, 0)


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
    def applicable(dataset):
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

    Takes no other parameters."""

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


class IntegrationVerification(aspecd.analysis.SingleAnalysisStep):
    """Verify whether the spectrum was correctly preprocessed.

    Checks if the baseline is not too much inclined on the right side of the
    spectrum, is therefore getting the area under this curve.

    In the case of a correct preprocessing, the curve after the first
    integration should be close to zero on the rightmost part of the spectrum,
    i.e. the area under this curve should also be close to zero.
    The indefinite integration can be performed using
    :class:`cwepr.processing.Integration`

    Attributes
    ----------
    parameters[y]: :class:`list`
        y values to use for the integration

    percentage: :class:`int`
        Percentage of the spectrum to consider

    threshold: :class:`float`
        Threshold for the integral. If the determined integral is smaller, the
        preprocessing is considered successful.


    .. warning::
        Rewrite? Integrate somewhere automatically?

    """

    def __init__(self):
        super().__init__()
        self.parameters["y"] = None
        self.percentage = 15
        self.threshold = 0.001
        self.description = "Preprocessing verification after first integration"

    def _perform_task(self):
        """Perform the actual verification.

        Perform the actual integration on a certain percentage of the points
        from the right part of the spectrum and compare them to the threshold.

        The result is a boolean: Is the integral lower than the threshold?

        """
        number_of_points = math.ceil(len(self.parameters["y"]) *
                                     self.percentage / 100.0)
        points_y = self.parameters["y"][len(self.parameters["y"]) -
                                        number_of_points - 1:]
        points_x = \
            self.dataset.data.axes[0].values[len(self.parameters["y"]) -
                                             number_of_points - 1:]
        integral = np.trapz(points_y, points_x)
        self.result = (integral < self.threshold)


class CommonDefinitionRanges(aspecd.analysis.SingleAnalysisStep):
    """Determine the common definition ranges.

    Compare the axis values of two or more datasets. This might be
    interesting for further analysis and/or processing steps.

    If the common range is inferior to a certain value, an exception is raised.
    This can be transformed to a warning on a higher level application. In this
    respect the analysis determines if a large enough common range exists. This
    is the case if no exception is raised.

    Additionally the analysis finds the edges of common ranges and returns them
    which can be used to display them in a plot.

    .. note::
        Das ist eine generelle Funktionalität für Algebra auf *mehreren*
        Datensätzen, und sollte als solche vielleicht einmal sauber
        implementiert und dann ins ASpecD-Framework verschoben werden.


    Attributes
    ----------
    parameters['datasets']: :class:`list`
        List of datasets to consider in the determination.

    parameters['threshold']: :class:`float`
        Distance used for determining whether or not the common
        definition range of two spectra is large enough (vide infra).

    minimum: :class:`float`
        Leftmost end of all spectra determined in the routine.

    maximum: :class:`float`
        Rightmost end of all spectra determined in the routine.

    minimal_width: :class:`float`
        Smallest width of all spectra determined in the routine.

    start_points: :class:`list`
        List of the left ends of all spectra determined in the routine.

    end_points: :class:`list`
        List of the right ends of all spectra determined in the routine.

    Raises
    ------
    NotEnoughDatasetsError
        Exception raised when less than two datasets are provided.

    ValuesNotIncreasingError
        Exception raised when any given x axis does not start with the smallest
        and end with the highest value (determined by comparison of the first
        and last value).

    NoCommonspaceError
        Exception raised when the size of the common definition range is
        considered too low (vide supra).

    """

    def __init__(self, datasets, threshold=0.05):
        super().__init__()
        self.parameters["datasets"] = datasets
        self.parameters["threshold"] = threshold
        self.minimum = None
        self.maximum = None
        self.minimal_width = None
        self.start_points = list()
        self.end_points = list()
        self.description = "Common definition space determination"

    def _perform_task(self):
        """Main function performing the necessary subtasks.

        To find the common definition ranges first all relevant data points
        are collected. Subsequently the common ranges are determined and
        finally the delimiter points between different ranges are determined.
        These points are returned as result to possibly display them in a plot
        using multiple spectra.

        Raises
        ------
        NotEnoughDatasetsError
            Exception raised when less than two datasets are provided.

        """
        if len(self.parameters["datasets"]) < 2:
            raise DefinitionRangeDeterminationError(
                "Number of datasets ( " + str(len(self.parameters["datasets"]))
                + ") is too low!")
        self._acquire_data()
        self._check_commonspace_for_all()
        self.result = self._find_all_delimiter_points()

    def _acquire_data(self):
        """All relevant data (see class attributes) are collected.

        Raises
        ------
        ValuesNotIncreasingError
            Exception raised when any given x axis does not start with the
            smallest and end with the highest value (determined by comparison
            of the first and last value).

        """
        for dataset in self.parameters["datasets"]:
            x_coordinates = dataset.data.axes[0].values
            if x_coordinates[-1] < x_coordinates[0]:
                dataset_name = dataset.id
                message = 'ExperimentalDataset ' + dataset_name +\
                          'has x values in the wrong order.'
                raise ValuesNotIncreasingError(message=message)
        for dataset in self.parameters["datasets"]:
            x_coordinates = dataset.data.axes[0].values
            self.start_points.append(x_coordinates[0])
            self.end_points.append(x_coordinates[-1])
            if self.minimum is None or x_coordinates[0] < self.minimum:
                self.minimum = x_coordinates[0]
            if self.maximum is None or x_coordinates[-1] > self.maximum:
                self.maximum = x_coordinates[-1]
            if (self.minimal_width is None or
                    (x_coordinates[-1] - x_coordinates[0])
                    < self.minimal_width):
                self.minimal_width = x_coordinates[-1] - x_coordinates[0]

    def _check_commonspace_for_two(self, index1, index2):
        """Compare the definition ranges of two datasets.

        Determine whether or not the common definition range of two spectra
        is considered large enough. This is determined by measuring the
        distance between the start and end points of the spectra x axis. Two
        factors considered are the difference in length between the axes as
        well as the user provided threshold value.

        The maximum distance allowed on either end is
            length_difference + threshold*smaller width

        Parameters
        ----------
        index1: :class:`int`
            Index of one dataset used in the comparison. The index is given
            for the instance's list of datasets.

        index2: :class:`int`
            Index of the second dataset used in the comparison.

        Raises
        ------
        NoCommonspaceError
            Exception raised when the size of the common definition range is
            considered too low (vide supra).

        """
        width1 = self.end_points[index1] - self.start_points[index1]
        width2 = self.end_points[index2] - self.start_points[index2]
        width_delta = math.fabs(width1 - width2)
        if (math.fabs(self.start_points[index1] - self.start_points[index2])
            > (width_delta + self.parameters["threshold"] *
               (min(width1, width2)))) or (
                math.fabs(self.end_points[index1] - self.end_points[index2]) > (
                width_delta + self.parameters["threshold"] *
                (min(width1, width2)))):
            name1 = self.parameters["datasets"][index1].id
            name2 = self.parameters["datasets"][index1].id
            errormessage = ("Datasets " + name1 + " and " + name2 +
                            "have not enough common space.")
            raise NoCommonRangeError(errormessage)

    def _check_commonspace_for_all(self):
        """Check all possible common definition ranges.

        .. todo::
            Avoid calculating every combination twice.

        """
        for dataset_index_1, _ in enumerate(self.parameters["datasets"]):
            for dataset_index_2, _ in enumerate(self.parameters["datasets"]):
                if dataset_index_1 != dataset_index_2:
                    self._check_commonspace_for_two(dataset_index_1,
                                                    dataset_index_2)

    def _find_all_delimiter_points(self):
        """Find points where a spectrum starts or ends.

        Points very close to the actual edges of the whole definition range
        are not considered. Different points that are rather close to each
        other are combined.

        This method is used to provide points to display edges of common
        ranges inside a plot.

        """
        self.start_points.sort()
        self.end_points.sort()
        self._eliminate_close_delimiters(self.start_points)
        self._eliminate_close_delimiters(self.end_points)
        delimiter_points = self.start_points
        delimiter_points.extend(self.end_points)
        points_close_to_edge = list()
        for data_index, data_value in enumerate(delimiter_points):
            if (math.fabs(data_value - self.minimum) <
                0.03 * self.minimal_width) or (
                    math.fabs(data_value - self.maximum) <
                    0.03 * self.minimal_width):
                points_close_to_edge.append(data_index)
        points_close_to_edge.reverse()
        for data_index in range(len(points_close_to_edge)):
            del delimiter_points[data_index]
        return delimiter_points

    def _eliminate_close_delimiters(self, points):
        """Combine points close to each other.

        Combining means, eliminating both and adding a new point between the
        two.

        Close means less than:
            0.03*smallest width of all spectra

        This threshold is currently rather arbitrary.

        """
        close_points = list()
        while True:
            for data_index in range(len(points) - 1):
                if math.fabs(points[data_index] - points[data_index + 1]) < \
                        0.03 * self.minimal_width:
                    close_points.append([data_index, data_index + 1])
            if close_points != list():
                close_points.reverse()
                for pair in close_points:
                    center = math.fabs(pair[0] - pair[1]) / 2.0
                    del points[pair[1]]
                    points[pair[0]] = center
                close_points = list()




