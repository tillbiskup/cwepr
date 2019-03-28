"""Module containing all analysis steps

An analysis step is everything that operates on a dataset and yields a
result largely independent of this dataset. E.g., integration or determination
of a field correction value.
"""

import copy
import math
import numpy as np
import scipy.integrate

import aspecd.analysis


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class WrongOrderError(Error):
    """Exception raised when the x values given for the common space
    determination are not in increasing Order.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """
    def __init__(self, message=''):
        super().__init__()
        self.message = message


class NotEnoughDatasetsError(Error):
    """Exception raised when less than two datasets are given for
    the commonspace determination.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error
    """
    def __init__(self, message=''):
        super().__init__()
        self.message = message


class NoCommonspaceError(Error):
    """Exception raised when less than two datasets are given for
    the commonspace determination.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class FieldCorrectionValueFinding(aspecd.analysis.AnalysisStep):
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

    Parameters
    ----------
    nu_value: :class:`float`
        Frequency value of the measurement used to calculate the expected
        field value.
    """
    VALUE_G_LILIF = 2.002293
    VALUE_MuB = 9.27401*10**(-24)
    VALUE_H = 6.62607*10**(-34)

    def __init__(self, nu_value):
        super().__init__()
        self.nu_value = nu_value
        self.description = "Determination of a field correction value"

    def _perform_task(self):
        """Wrapper around the method determining the field correction value.
        """
        self.results["Delta_B0"] = self.get_field_correction_value()

    def get_field_correction_value(self):
        """Calculates a field correction value.

        Finds the approximate maximum of the peak in a field standard
        spectrum by using the difference between minimum and maximum in
        the derivative. This value is subtracted from the the expected
        field value for the MW frequency provided.

        Returns
        -------
        delta_b0: :class:`float`
            Field correction value
        """
        index_max = np.argmax(self.dataset.data.axes[0].values)
        index_min = np.argmin(self.dataset.data.axes[0].values)
        experimental_field = (
            self.dataset.data.data[index_max] -
            self.dataset.data.data[index_min])/2.0
        calcd_field = \
            self.VALUE_H*self.nu_value/self.VALUE_G_LILIF/self.VALUE_MuB
        delta_b0 = calcd_field - experimental_field
        return delta_b0


class BaselineFitting(aspecd.analysis.AnalysisStep):
    """Analysis step for finding a baseline correction polynomial.

    Attributes
    ----------
    order: :class:`int`
        Order of the polynomial to create

    percentage: :class:`int`
        Percentage of the spectrum to consider as baseline on
        EACH SIDE of the spectrum. I.e. 10% means 10% left and
        10 % right.

    """
    def __init__(self, order=0, percentage=10):
        super().__init__()
        self.parameters["order"] = order
        self.parameters["percentage"] = percentage
        self.description = "Polynomial fit to baseline"

    def _perform_task(self):
        """Call the function to find a polynomial
        and set it into the results.
        """
        self.results["Fit_Coeffs"] = self._find_polynome_by_fit()
        self.resulting_dataset = aspecd.dataset.CalculatedDataset()
        x = self.dataset.data.axes[0].values
        self.resulting_dataset.data.axes[0].values = x
        self.resulting_dataset.data.data = np.polyval(np.poly1d(self.results["Fit_Coeffs"]), x)

    def _find_polynome_by_fit(self):
        """Perform a polynomial fit on the baseline.

        This method assembles the data points of the spectrum to consider
        and uses a numpy polynomial fit on these points.
        """
        number_of_points = len(self.dataset.data.data)
        points_per_side = \
            math.ceil(number_of_points*self.parameters["percentage"]/100.0)
        dataset_copy_y = copy.deepcopy(self.dataset.data.data)
        data_list_y = dataset_copy_y.tolist()
        data_list_x = (copy.deepcopy(self.dataset.data.axes[0].values)).tolist()
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

        Slices the list of all data points to have a list of
        points from each side of the spectrum to use for polynomial fitting.

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
        left_part = data[:points_per_side+1]
        right_part = data[len(data) - points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use


class IntegrationIndefinite(aspecd.analysis.AnalysisStep):
    """Performs an indefinite integration.

    Indefinite integration yields a new array of y values of the integrated
    function.

    Attributes
    ----------
    y: :class:`list`
        y values to use for the integration. If this is omitted the y values
        of the dataset are used.
    """
    def __init__(self, y=None):
        super().__init__()
        self.y = y
        self.description = "Indefinite Integration"

    def _perform_task(self):
        """Perform the actual integration.

        Perform the actual integration using trapezoidal integration
        functionality from scipy. The keyword argument initial=0 is used
        to yield a list of length identical to the original one.
        """
        x = self.dataset.data.axes[0].values
        if self.y is None:
            y = self.dataset.data.data
        else:
            y = self.y

        integral_values = scipy.integrate.cumtrapz(y, x, initial=0)
        self.results["integral_values"] = integral_values


class IntegrationDefinite(aspecd.analysis.AnalysisStep):
    """Makes a definite integration, i.e. calculates the area under the curve.

    Attributes
    ----------
    y: :class:`list`
        y values to use for the integration.
    """
    def __init__(self, y):
        super().__init__()
        self.y = y
        self.description = "Definite Integration / Area und the curve"

    def _perform_task(self):
        """Performs the actual integration. The x values
        from the dataset are used."""
        x = self.dataset.data.axes[0].values
        y = self.y

        integral = np.trapz(y, x)
        self.results["integral"] = integral


class IntegrationVerification(aspecd.analysis.AnalysisStep):
    """Verifies, if the spectrum was correctly preprocessed.

    In the case of a correct preprocessing, the curve after the first
    integration should be close to zero on the rightmost part of the spectrum,
    i.e. the area under this curve should also be close to zero.

    Attributes
    ----------
    y: :class:`list`
        y values to use for the integration

    percentage: :class:`int`
        Percentage of the spectrum to consider

    threshold: :class:`float`
        Threshold for the integral. If the integral determined is smaller
        the preprocessing is considered to have been successful.
    """
    def __init__(self, y, percentage=15, threshold=0.001):
        super().__init__()
        self.y = y
        self.percentage = percentage
        self.threshold = threshold
        self.description = "Preprocessing verification after first integration"

    def _perform_task(self):
        """Perform the actual verification.

        Performs the actual integration on a certain percentage of the
        points from the right part of the spectrum and compares them to the
        threshold.

        The result is a boolean: Is the integral lower than the threshold?
        """
        number_of_points = math.ceil(len(self.y)*self.percentage/100.0)
        points_y = self.y[len(self.y) - number_of_points - 1:]
        points_x = \
            self.dataset.data.axes[0].values[len(self.y) - number_of_points - 1:]
        integral = np.trapz(points_y, points_x)
        self.results["integral_okay"] = (integral < self.threshold)


class CommonspaceAndDelimiters(aspecd.analysis.AnalysisStep):
    """Analysis step for determine how much common definition range
    some given spectra have.

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

    WrongOrderError
        Exception raised when any given x axis does not start with the
        smallest and end with the highest value (determined by comparison
        of the first and last value).

    NoCommonspaceError
        Exception raised when the size of the common definition range is
        considered too low (vide supra).
    """
    def __init__(self, datasets, threshold=0.05):
        super().__init__()
        self.datasets = datasets
        self.threshold = threshold
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
        finally the delimiter points between different ranges are
        determined.
        These points are returned as result to possibly display them in a plot
        using multiple spectra.

        Raises
        ------
        NotEnoughDatasetsError
            Exception raised when less than two datasets are provided.
        """
        if len(self.datasets) < 2:
            raise NotEnoughDatasetsError(
                "Number of datasets( " + str(len(self.datasets)) +
                ") is too low!")
        self._acquire_data()
        self._check_commonspace_for_all()
        self.results["delimiters"] = self._find_all_delimiter_points()

    def _acquire_data(self):
        """All relevant data (see class attributes) are collected.

        Raises
        ------
        WrongOrderError
            Exception raised when any given x axis does not start with the
            smallest and end with the highest value (determined by comparison
            of the first and last value).
        """
        for dataset in self.datasets:
            x = dataset.data.axes[0].values
            if x[-1] < x[0]:
                dataset_name = dataset.id
                raise WrongOrderError("Dataset " + dataset_name +
                                      " has x values in the wrong order.")

        for dataset in self.datasets:
            x = dataset.data.axes[0].values
            self.start_points.append(x[0])
            self.end_points.append(x[-1])
            if self.minimum is None or x[0] < self.minimum:
                self.minimum = x[0]
            if self.maximum is None or x[-1] > self.maximum:
                self.maximum = x[-1]
            if self.minimal_width is None or (x[-1]-x[0]) < self.minimal_width:
                self.minimal_width = x[-1]-x[0]

    def check_commonspace_for_two(self, index1, index2):
        """Compares the definition ranges of two datasets.

        Determines whether or not the common definition range of two specta
        is considered large enough. This is determined by measuring the
        distance between the start and end points of the spectra x axis.
        Two factors considered are the difference in length between the axes
        as well as the user provided threshold value.

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
        width_delta = math.fabs(width1-width2)
        if (math.fabs(self.start_points[index1]-self.start_points[index2]) > (
                width_delta + self.threshold*(min(width1, width2)))) or (
            math.fabs(self.end_points[index1] - self.end_points[index2]) > (
                width_delta + self.threshold * (min(width1, width2)))):
            name1 = self.datasets[index1].id
            name2 = self.datasets[index1].id
            errormessage = ("Datasets " + name1 + " and " + name2 +
                                     "have not enough commonspace.")
            raise NoCommonspaceError(errormessage)

    def _check_commonspace_for_all(self):
        """Checks the common definition range for any combination of two
        different spectra.

        .. todo::
            Avoid calculating every combination twice.
        """
        for n in range(len(self.datasets)):
            for m in range(len(self.datasets)):
                if n != m:
                    self.check_commonspace_for_two(n, m)

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
        for n in range(len(delimiter_points)):
            if (math.fabs(delimiter_points[n] - self.minimum) <
                0.03*self.minimal_width) or (
                    math.fabs(delimiter_points[n] - self.maximum) <
                    0.03 * self.minimal_width):
                points_close_to_edge.append(n)
        points_close_to_edge.reverse()
        for n in range(len(points_close_to_edge)):
            del(delimiter_points[n])
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
            for n in range(len(points)-1):
                if math.fabs(points[n]-points[n+1]) < 0.03*self.minimal_width:
                    close_points.append([n, n+1])
            if close_points == list():
                return
            else:
                close_points.reverse()
                for pair in close_points:
                    center = math.fabs(pair[0]-pair[1])/2.0
                    del(points[pair[1]])
                    points[pair[0]] = center
                close_points = list()


class PeakToPeakLinewidth(aspecd.analysis.AnalysisStep):
    def __init__(self):
        super().__init__()
        self.description = "Determine peak-to-peak linewidth"

    def _perform_task(self):
        """Call the function to calculate the line width
        and set it into the results.
        """
        self.results["p2p_lw"] = self.get_p2p_linewidth()

    def get_p2p_linewidth(self):
        """Calculates the peak-to-peak line width.

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


class LinewidthFWHM(aspecd.analysis.AnalysisStep):
    """

    """
    def __init__(self):
        super().__init__()
        self.description = "Determine linewidth (full width at half max; FWHM)"

    def _perform_task(self):
        """Call the function to calculate the line width
        and set it into the results.
        """
        self.results["fwhm_lw"] = self.get_fwhm_linewidth()

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
        for n in range(len(spectral_data)):
            spectral_data[n] -= maximum/2
            if spectral_data[n] < 0:
                spectral_data[n] *= -1
        left_zero_cross_index = np.argmin(spectral_data[:index_max])
        right_zero_cross_index = np.argmin(spectral_data[index_max:])
        linewidth = right_zero_cross_index - left_zero_cross_index
        return linewidth


class SignalToNoise(aspecd.analysis.AnalysisStep):
    def __init__(self, percentage=10):
        super().__init__()
        self.parameters["percentage"] = percentage
        self.description = "Determine signal to noise ratio."

    def _perform_task(self):
        """Call the function to calculate the actual ratio
        and set it into the results.
        """
        data_copy = copy.deepcopy(self.dataset.data.data)
        data_list_absolute = data_copy.to_list()
        for n in range(len(data_list_absolute)):
            if data_list_absolute[n] < 0:
                data_list_absolute[n] *= -1
        signal_max = max(data_list_absolute)
        noise_max = self._get_noise_maximum(data_list_absolute)
        self.results["S/N ratio"] = signal_max/noise_max

    def _get_noise_maximum(self, data_absolute):
        """Find the maximum of the noise.

        This method assembles the data points of the spectrum to consider as
        noise and returns the maximum.
        """
        number_of_points = len(data_absolute)
        points_per_side = \
            math.ceil(number_of_points*self.parameters["percentage"]/100.0)
        points_to_use_y = \
            self._get_points_to_use(data_absolute, points_per_side)
        maximum = max(points_to_use_y)
        return maximum

    @staticmethod
    def _get_points_to_use(data, points_per_side):
        """Get a number of points from the spectrum to use for a fit.

        Slices the list of all data points to have a list of
        points from each side of the spectrum to consider as noise.

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
        left_part = data[:points_per_side+1]
        right_part = data[len(data) - points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use
