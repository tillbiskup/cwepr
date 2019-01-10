import numpy as np


import aspecd.processing


class FieldCorrection(aspecd.processing.ProcessingStep):
    """Perform field correction of the data with a correction
    value previously determined.

    Parameters
    ----------
    correction_value: 'float'
    The previously determined correction value.
    """
    def __init__(self, correction_value):
        super().__init__()
        self.parameters["correction_value"] = correction_value

    def _perform_task(self):
        """Shift all field axis data points by the correction value
        from the parameters.
        """
        for n in range(len(self.dataset.data.data[0, :])):
            round(self.parameters["correction_value"], 6)
            self.dataset.data.data[0, n] += self.parameters["correction_value"]


class FrequencyCorrection(aspecd.processing.ProcessingStep):
    """Transform data of a given frequency to another given
    frequency.
    This is used to make spectra comparable.

    ------
    References for the constants:
    g(Lilif) = 2.002293 +- 0.000002
    Reference: Rev. Sci. Instrum. 1989, 60, 2949-2952.
    Mu(B) = 9.27401*10**(-24)
    Reference: Rev. Mod. Phys. 2016, 88, ?.
    h = 6.62607*10**(-34)
    Reference: Rev. Mod. Phys. 2016, 88, ?.
    ------

    Attributes
    ----------
    nu_given: 'float'
    Given frequency of the data present.

    nu_target: 'float'
    Frequency that the data should be transformed to.

    """
    VALUE_G_LILIF = 2.002293
    VALUE_MuB = 9.27401*10**(-24)
    VALUE_H = 6.62607*10**(-34)

    def __init__(self, nu_given, nu_target):
        super().__init__()
        self.parameters["nu_given"] = nu_given
        self.parameters["nu_target"] = nu_target

    def _perform_task(self):
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] = self._transform_to_g(self.dataset.data.data[0, n])
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] = self._transform_to_b(self.dataset.data.data[0, n])

    def _transform_to_g(self, value):
        """Transforms a field (B) axis value to a g axis value.

        Parameters
        ----------
         value: 'float'
         B value to transform.

        Returns
        -------
        g_value: 'float'
        Transformed value.
        """
        g_value = self.VALUE_H*self.parameters["nu_given"]/self.VALUE_MuB/value
        return g_value

    def _transform_to_b(self, value):
        """Transforms a g axis value to a field (B) axis value.

        Parameters
        ----------
        value: 'float'
        g value to transform.

        Returns
        -------
        b_value: 'float'
        Transformed value.
        """
        b_value = self.VALUE_H * self.parameters["nu_target"] / self.VALUE_MuB / value
        return b_value


class BaselineCorrection(aspecd.processing.ProcessingStep):
    """Performs a baseline correction using a polynomial
    previously determined. """

    def __init__(self, coeffs):
        super().__init__()
        self.parameters["coeffs"] = coeffs

    def _perform_task(self):
        x = self.dataset.data.data[0, :]
        values_to_subtract = np.polyval(np.poly1d(self.parameters["coeffs"]), x)
        for n in range(len(list(self.dataset.data.data[1, :]))):
            self.dataset.data.data[1, n] -= values_to_subtract[n]


