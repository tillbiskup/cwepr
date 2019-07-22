"""Module containing all analysis steps

An analysis step is everything that operates on a dataset and yields a result
largely independent of this dataset. E.g., integration or determination of a
field correction value.
"""

import copy
import math
import numpy as np

import aspecd.analysis


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class ValuesNotIncreasingError(Error):
    """Exception raised when x values are decreasing.

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


class NotEnoughDatasetsError(Error):
    """Exception raised when common definition range can't be determined.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class NoCommonSpaceError(Error):
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

    References for the constants:

    g value for Li:LiF::

        g(LiLiF) = 2.002293 +- 0.000002

    Reference: Rev. Sci. Instrum. 1989, 60, 2949-2952.

    Bohr magneton::

        mu_B = 9.27401*10**(-24)

    Reference: Rev. Mod. Phys. 2016, 88, 035009.

    Planck constant::

        h = 6.62607*10**(-34)

    Reference: Rev. Mod. Phys. 2016, 88, 035009.
    """

    G_LILIF = 2.002293
    BOHR_MAGNETON = 9.27401 * 10 ** (-24)
    PLANCK_CONSTANT = 6.62607 * 10 ** (-34)

    def __init__(self):
        super().__init__()
        self.nu_value = 0.0
        self.description = "Determination of a field correction value"

    def _perform_task(self):
        """Wrapper around field correction value determination method."""
        self.nu_value = self.dataset.metadata.bridge.mw_frequency.value
        self.result = self._get_field_correction_value()

    def _get_field_correction_value(self):
        """Calculates a field correction value.

        Finds the approximate maximum of the peak in a field standard spectrum
        by using the difference between minimum and maximum in the derivative.
        This value is subtracted from the the expected field value for the MW
        frequency provided.

        Returns
        -------
        delta_b0: :class:`float`
            Field correction value

        """
        index_max = np.argmax(self.dataset.data.axes[0].values)
        index_min = np.argmin(self.dataset.data.axes[0].values)
        experimental_field = (
            self.dataset.data.data[index_max] -
            self.dataset.data.data[index_min]) / 2.0
        calculated_field = \
            self.PLANCK_CONSTANT * self.nu_value / (self.G_LILIF * self.BOHR_MAGNETON)
        delta_b0 = calculated_field - experimental_field
        return delta_b0


class PolynomialBaselineFitting(aspecd.analysis.SingleAnalysisStep):
    """Analysis step for finding a baseline correction polynomial.

    An actual correction with the respective polynomial can be performed afterwards
    using :class:`cwepr.processing.BaselineCorrectionWithPolynomial`.

    Attributes
    ----------
    order: :class:`int`
        Order of the polynomial to create

    percentage: :class:`int`
        Percentage of the spectrum to consider as baseline on EACH SIDE of the
        spectrum. I.e. 10% means 10% left and 10 % right.

    """

    def __init__(self, order=0, percentage=10):
        super().__init__()
        self.parameters["order"] = order
        self.parameters["percentage"] = percentage
        self.description = "Polynomial fit to baseline"

    def _perform_task(self):
        """Wrapper around polynomial determination."""
        coefficients = self._find_polynomial_by_fit()
        self.result = coefficients

    def _find_polynomial_by_fit(self):
        """Perform a polynomial fit on the baseline.

        Assemble the data points of the spectrum to consider and use a numpy
        polynomial fit on these points.
        """
        number_of_points = len(self.dataset.data.data)
        points_per_side = \
            math.ceil(number_of_points * self.parameters["percentage"] / 100.0)
        dataset_copy_y = copy.deepcopy(self.dataset.data.data)
        data_list_y = dataset_copy_y.tolist()
        data_list_x = \
            (copy.deepcopy(self.dataset.data.axes[0].values)).tolist()
        points_to_use_x = \
            self._get_points_to_use(data_list_x, points_per_side)
        points_to_use_y = \
            self._get_points_to_use(data_list_y, points_per_side)
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
        right_part = data[len(data) - points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use


class AreaUnderCurve(aspecd.analysis.SingleAnalysisStep):
    """Make definite integration, i.e. calculate the area under the curve."""

    def __init__(self):
        super().__init__()
        self.description = "Definite integration / area und the curve"

    def _perform_task(self):
        """Perform the actual integration.

        The x values from the dataset are used.
        """
        x_coordinates = self.dataset.data.axes[0].values
        y_coordinates = self.dataset.data.data

        integral = np.trapz(y_coordinates, x_coordinates)
        self.result = integral


class IntegrationVerification(aspecd.analysis.SingleAnalysisStep):
    """Verify whether the spectrum was correctly preprocessed.

    In the case of a correct preprocessing, the curve after the first
    integration should be close to zero on the rightmost part of the spectrum,
    i.e. the area under this curve should also be close to zero.
    The indefinite integration can be performed using :class:`cwepr.processing.Integration`

    Attributes
    ----------
    y: :class:`list`
        y values to use for the integration

    percentage: :class:`int`
        Percentage of the spectrum to consider

    threshold: :class:`float`
        Threshold for the integral. If the integral determined is smaller the
        preprocessing is considered to have been successful.

    """

    def __init__(self, y, percentage=15, threshold=0.001):
        super().__init__()
        self.parameters["y"] = y
        self.percentage = percentage
        self.threshold = threshold
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

    If the common range is inferior to a certain value, an exception is raised.
    This can be transformed to a warning on a higher level application. In this
    respect the analysis determines if a large enough common space exists. This
    is the case if no exception is raised.

    Additionally the analysis finds the edges of common ranges and returns them
    which can be used to display them in a plot.

    Attributes
    ----------
    datasets: :class:`list`
        List of datasets to consider in the determination.

    threshold: :class:`float`
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
            raise NotEnoughDatasetsError(
                "Number of datasets( " + str(len(self.parameters["datasets"]))
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
                raise ValuesNotIncreasingError("Dataset " + dataset_name +
                                      " has x values in the wrong order.")
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
                            "have not enough commonspace.")
            raise NoCommonSpaceError(errormessage)

    def _check_commonspace_for_all(self):
        """Check all possible common definition ranges.

        .. todo::
            Avoid calculating every combination twice.

        """
        for dataset_index_1 in range(len(self.parameters["datasets"])):
            for dataset_index_2 in range(len(self.parameters["datasets"])):
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


class LinewidthPeakToPeak(aspecd.analysis.SingleAnalysisStep):
    """Linewidth measurement (peak to peak in derivative)"""

    def __init__(self):
        super().__init__()
        self.description = "Determine peak-to-peak linewidth"

    def _perform_task(self):
        self.result = self.get_peak_to_peak_linewidth()

    def get_peak_to_peak_linewidth(self):
        """Calculates the peak-to-peak linewidth.

        This is done by determining the distance between the maximum and the
        minimum in the derivative spectrum which should yield acceptable
        results in a symmetrical signal.

        Returns
        -------
        linewidth: :class:`float`
            line width as determined

        """
        index_max = np.argmax(self.dataset.data.axes[0].values)
        index_min = np.argmin(self.dataset.data.axes[0].values)
        linewidth = (
            self.dataset.data.data[index_max] -
            self.dataset.data.data[index_min])
        return linewidth


class LinewidthFWHM(aspecd.analysis.SingleAnalysisStep):
    """Linewidth measurement at half maximum"""

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
        index_max = np.argmax(self.dataset.data.axes[0].values)
        spectral_data = copy.deepcopy(self.dataset.data.data)
        maximum = self.dataset.data.axes[0].values[index_max]
        for data_index, data_value in enumerate(spectral_data):
            data_value -= maximum / 2
            if data_value < 0:
                data_value *= -1
            spectral_data[data_index] = data_value
        left_zero_cross_index = np.argmin(spectral_data[:index_max])
        right_zero_cross_index = np.argmin(spectral_data[index_max:])
        linewidth = right_zero_cross_index - left_zero_cross_index
        return linewidth


class SignalToNoiseRatio(aspecd.analysis.SingleAnalysisStep):
    """Measure a spectrum's signal to noise ratio.

    This is done by comparing the absolute maximum of the spectrum to the
    maximum of the edge part of the spectrum (i.e. a part which is considered
    to not contain any signal.

    Attributes
    ----------
    percentage: :class:`int`
        percentage of the spectrum to be considered edge part on any side
        (i.e. 10% means 10% on each end).

    """

    def __init__(self, percentage=10):
        super().__init__()
        self.parameters["percentage"] = percentage
        self.description = "Determine signal to noise ratio."

    def _perform_task(self):
        """Determine signal to noise ratio.

        Call method to get the amplitude of the noise, compare it to the
        absolute amplitude and set a result.

        .. todo::
            numpy.abs or similar should do the trick for absolute values...

        """
        data_copy = copy.deepcopy(self.dataset.data.data)
        data_list_absolute = data_copy.to_list()
        for data_index, data_value in enumerate(data_list_absolute):
            if data_value < 0:
                data_list_absolute[data_index] *= -1
        signal_amplitude = max(data_list_absolute)
        noise_amplitude = self._get_noise_amplitude(data_list_absolute)
        self.result = signal_amplitude / noise_amplitude

    def _get_noise_amplitude(self, data_absolute):
        """Find the maximum of the noise.

        This method assembles the data points of the spectrum to consider as
        noise and returns the maximum.

        """
        number_of_points = len(data_absolute)
        points_per_side = \
            math.ceil(number_of_points * self.parameters["percentage"] / 100.0)
        points_to_use_y = \
            self._get_points_to_use(data_absolute, points_per_side)
        amplitude = max(points_to_use_y)
        return amplitude

    @staticmethod
    def _get_points_to_use(data, points_per_side):
        """Get a number of points from the spectrum to use for a fit.

        Slices the list of all data points to have a list of points from each
        side of the spectrum to consider as noise.

        WARNING: The spectral data needs to be provided and/or the percentage
        to use set in a way that no actual peak lies in this range.

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
        right_part = data[len(data) - points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use
