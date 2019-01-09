import numpy as np
from math import ceil
from copy import deepcopy


import aspecd.analysis


class FieldCorrectionValueFinding(aspecd.analysis.AnalysisStep):
    """Determine correction value for field correction.

    ------
    References for the constants
    g(Lilif) = 2.002293 +- 0.000002
    Reference: Rev. Sci. Instrum. 1989, 60, 2949-2952.
    Mu(B) = 9.27401*10**(-24)
    Reference: Rev. Mod. Phys. 2016, 88, ?.
    h = 6.62607*10**(-34)
    Reference: Rev. Mod. Phys. 2016, 88, ?.
    ------

    Parameters
    ----------
    nu_value: 'float'
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
        delta_b0: 'float'
        Field correction value
        """
        index_max = np.argmax(self.dataset.data.data[1, :])
        index_min = np.argmin(self.dataset.data.data[1, :])
        experimental_field = (self.dataset.data.data[0, index_max] - self.dataset.data.data[0, index_min])/2.0
        calcd_field = self.VALUE_H*self.nu_value/self.VALUE_G_LILIF/self.VALUE_MuB
        delta_b0 = calcd_field - experimental_field
        return delta_b0


class BaselineFitting(aspecd.analysis.AnalysisStep):
    """Analysis step for finding a baseline correction polynomial.

    Attributes
    ----------
    order: 'int'
    Order of the polynomial to create

    percentage: 'int'
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
        points_per_side = ceil(number_of_points*self.parameters["percentage"]/100.0)
        dataset_copy = deepcopy(self.dataset.data.data)
        data_list = dataset_copy.tolist()
        points_to_use_x = self._get_points_to_use(data_list[0], points_per_side)
        points_to_use_y = self._get_points_to_use(data_list[1], points_per_side)
        coefficients = np.polyfit(np.asarray(points_to_use_x), np.asarray(points_to_use_y), self.parameters["order"])
        return coefficients

    @staticmethod
    def _get_points_to_use(data, points_per_side):
        """Slices the list of all data points to have a list of
        points from each side of the spectrum to use for polynomial fitting.

        Parameters
        ----------
        data: 'list'
        List from which points should be used on each side.

        points_per_side: 'int'
        How many points from each end of the list should be used.

        Returns
        -------
        points_to_use: 'list'
        List only containing the correct number of points from each side
        and not the points in between.
        """
        left_part = data[:points_per_side+1]
        right_part = data[len(data) - points_per_side - 1:]
        points_to_use = left_part
        points_to_use.extend(right_part)
        return points_to_use


