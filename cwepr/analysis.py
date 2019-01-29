"""Module containing all analysis steps

An analysis step is everything that operates on a dataset and yields a
result largely independent of this dataset. E.g., integration or determination
of a field correction value.
"""

from copy import deepcopy
from math import fabs, ceil
import numpy as np
from scipy import integrate

import aspecd.analysis


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class WrongOrderError(Error):
    """Exception raised when the x values given for the commonspace
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
    """Determine correction value for field correction.

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
    nu_value: :class:'float'
        Frequency value of the measurement used to calculate the expected
        field value.
    """
    VALUE_G_LILIF = 2.002293
    VALUE_MuB = 9.27401*10**(-24)
    VALUE_H = 6.62607*10**(-34)

    def __init__(self, nu_value):
        super().__init__()
        self.nu_value = nu_value

    def _perform_task(self):
        """Call the function to calculate the correction value
        and set it into the results.
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
        delta_b0: :class:'float'
            Field correction value
        """
        index_max = np.argmax(self.dataset.data.data[1, :])
        index_min = np.argmin(self.dataset.data.data[1, :])
        experimental_field = (
            self.dataset.data.data[0, index_max] -
            self.dataset.data.data[0, index_min])/2.0
        calcd_field = \
            self.VALUE_H*self.nu_value/self.VALUE_G_LILIF/self.VALUE_MuB
        delta_b0 = calcd_field - experimental_field
        return delta_b0


class BaselineFitting(aspecd.analysis.AnalysisStep):
    """Analysis step for finding a baseline correction polynomial.

    Attributes
    ----------
    order: :class:'int'
        Order of the polynomial to create

    percentage: :class:'int'
        Percentage of the spectrum to consider as baseline on
        EACH SIDE of the spectrum. I.e. 10% means 10% left and
        10 % right.

    """
    def __init__(self, order, percentage=10):
        super().__init__()
        self.parameters["order"] = order
        self.parameters["percentage"] = percentage

    def _perform_task(self):
        """Call the function to find a polynomial
        and set it into the results.
        """
        self.results["Fit_Coeffs"] = self._find_polynome_by_fit()

    def _find_polynome_by_fit(self):
        """This method assembles the data points of the spectrum to consider
        and uses a numpy polynomial fit on these points.
        """
        number_of_points = len(self.dataset.data.data[0, :])
        points_per_side = \
            ceil(number_of_points*self.parameters["percentage"]/100.0)
        dataset_copy = deepcopy(self.dataset.data.data)
        data_list = dataset_copy.tolist()
        points_to_use_x = \
            self._get_points_to_use(data_list[0], points_per_side)
        points_to_use_y = \
            self._get_points_to_use(data_list[1], points_per_side)
        coefficients = np.polyfit(
            np.asarray(points_to_use_x), np.asarray(points_to_use_y),
            self.parameters["order"])
        return coefficients

    @staticmethod
    def _get_points_to_use(data, points_per_side):
        """Slices the list of all data points to have a list of
        points from each side of the spectrum to use for polynomial fitting.

        Parameters
        ----------
        data: :class:'list'
            List from which points should be used on each side.

        points_per_side: :class:'int'
            How many points from each end of the list should be used.

        Returns
        -------
        points_to_use: :class:'list'
            List only containing the correct number of points from each side
            and not the points in between.
        """
        left_part = data[:points_per_side+1]
        right_part = data[len(data) - points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use


class IntegrationIndefinite(aspecd.analysis.AnalysisStep):
    """Makes an indefinite integration, yielding a new array of y
    values of the integrated function.

    Attributes
    ----------
    y: :class:'list'
        y values to use for the integration. If this is omitted the y values
        of the dataset are used.
    """
    def __init__(self, y=None):
        super().__init__()
        self.y = y

    def _perform_task(self):
        """Perform the actual integration using trapezoidal integration
        functionality from scipy. The keyword argument initial=0 is used
        to yield a list of length identical to the original one.
        """
        x = self.dataset.data.data[0, :]
        if self.y is None:
            y = self.dataset.data.data[1, :]
        else:
            y = self.y

        integral_values = integrate.cumtrapz(y, x, initial=0)
        self.results["integral_values"] = integral_values


class IntegrationDefinite(aspecd.analysis.AnalysisStep):
    """Makes a definite integration and calculates the area under the curve.

    Attributes
    ----------
    y: :class:'list'
        y values to use for the integration.
    """
    def __init__(self, y):
        super().__init__()
        self.y = y

    def _perform_task(self):
        """Performs the actual integration. The x values
        from the dataset are used."""
        x = self.dataset.data.data[0, :]
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
    y: :class:'list'
        y values to use for the integration

    percentage: :class:'int'
        Percentage of the spectrum to consider

    threshold: :class:'float'
        Threshold for the integral. If the integral determined is smaller
        the preprocessing is considered to have been successful.
    """
    def __init__(self, y, percentage=15, threshold=0.001):
        super().__init__()
        self.y = y
        self.percentage = percentage
        self.threshold = threshold

    def _perform_task(self):
        """Performs the actual integration on a certain percentage of the
        points from the right part of the spectrum and compares them to the
        threshold.

        The result is a boolean: Is the integral lower than the threshold?
        """
        number_of_points = ceil(len(self.y)*self.percentage/100.0)
        points_y = self.y[len(self.y) - number_of_points - 1:]
        points_x = \
            self.dataset.data.data[0, len(self.y) - number_of_points - 1:]
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
    datasets: :class:'list'
        List of datasets to consider in the determination.

    threshold: :class:'float'
        Distance used for determining whether or not the common
        definition range of two spectra is large enough (vide infra).

    minimum: :class:'float'
        Leftmost end of all spectra determined in the routine.

    maximum: :class:'float'
        Rightmost end of all spectra determined in the routine.

    minimal_width: :class:'float'
        Smallest width of all spectra determined in the routine.

    start_points: :class:'list'
        List of the left ends of all spectra determined in the routine.

    end_points: :class:'list'
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

    def _perform_task(self):
        """To find the common definition ranges first all relevant data points
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
            x = dataset.data.data[0, :]
            if x[-1] < x[0]:
                dataset_name = dataset.metadata.measurement.filename
                raise WrongOrderError("Dataset " + dataset_name +
                                      " has x values in the wrong order.")

        for dataset in self.datasets:
            x = dataset.data.data[0, :]
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
        index1: :class:'int'
            Index of one dataset used in the comparison. The index is given
            for the instance's list of datasets.
        index2: :class:'int'
            Index of the second dataset used in the comparison.

        Raises
        ------
        NoCommonspaceError
            Exception raised when the size of the common definition range is
            considered too low (vide supra).
        """
        width1 = self.end_points[index1] - self.start_points[index1]
        width2 = self.end_points[index2] - self.start_points[index2]
        width_delta = fabs(width1-width2)
        if (fabs(self.start_points[index1]-self.start_points[index2]) > (
                width_delta + self.threshold*(min(width1, width2)))) or (
            fabs(self.end_points[index1] - self.end_points[index2]) > (
                width_delta + self.threshold * (min(width1, width2)))):
            name1 = self.datasets[index1].metadata.measurement.filename
            name2 = self.datasets[index1].metadata.measurement.filename
            raise NoCommonspaceError("Datasets " + name1 + " and " + name2 +
                                     "have not enough commonspace.")

    def _check_commonspace_for_all(self):
        """Checks the common defintion range for any combination of two
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
            if (fabs(delimiter_points[n] - self.minimum) <
                0.03*self.minimal_width) or (
                    fabs(delimiter_points[n] - self.maximum) <
                    0.03 * self.minimal_width):
                points_close_to_edge.append(n)
        points_close_to_edge.reverse()
        for n in range(len(points_close_to_edge)):
            del(delimiter_points[n])
        return delimiter_points

    def _eliminate_close_delimiters(self, points):
        """Combine points close to each other.

        Close means less than:
            0.03*smallest width of all spectra

        This threshold is currently rather arbitrary.
        """
        close_points = list()
        while True:
            for n in range(len(points)-1):
                if fabs(points[n]-points[n+1]) < 0.03*self.minimal_width:
                    close_points.append([n, n+1])
            if close_points == list():
                return
            else:
                close_points.reverse()
                for pair in close_points:
                    center = fabs(pair[0]-pair[1])/2.0
                    del(points[pair[1]])
                    points[pair[0]] = center
                close_points = list()


class PeakToPeakLinewidth(aspecd.analysis.AnalysisStep):
    def __init__(self):
        super().__init__()

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
        linewidth: :class:'float'
            line width as determined
        """
        index_max = np.argmax(self.dataset.data.data[1, :])
        index_min = np.argmin(self.dataset.data.data[1, :])
        linewidth = (
            self.dataset.data.data[0, index_max] -
            self.dataset.data.data[0, index_min])
        return linewidth
