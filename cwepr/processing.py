"""Module containing all processing steps.

A processing step is anything that modifies the dataset without giving an
a independent result. E.g., Field Correction or Baseline correction.
"""

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
    """Converts data of a given frequency to another given
    frequency.
    This is used to make spectra comparable.

    ------
    References for the constants

    g value for Li:LiF::

        g(LiLiF) = 2.002293 +- 0.000002

    Reference: Rev. Sci. Instrum. 1989, 60, 2949-2952.

    Bohr magneton::

        mu_B = 9.27401*10**(-24)

    Reference: Rev. Mod. Phys. 2016, 88, 035009.

    Planck constant::

        h = 6.62607*10**(-34)

    Reference: Rev. Mod. Phys. 2016, 88, 035009.
    ------

    Attributes
    ----------
    nu_given: 'float'
    Given frequency of the data present.

    nu_target: 'float'
    Frequency that the data should be converted to.

    """
    VALUE_G_LILIF = 2.002293
    VALUE_MuB = 9.27401*10**(-24)
    VALUE_H = 6.62607*10**(-34)

    def __init__(self, nu_given, nu_target):
        super().__init__()
        self.parameters["nu_given"] = nu_given
        self.parameters["nu_target"] = nu_target

    def _perform_task(self):
        """For the conversion the x axis data is first converted to
        an axis in units of using the given frequency, then converted back
        using target frequency.

        """
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] = self._transform_to_g(
                self.dataset.data.data[0, n])
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] = self._transform_to_b(
                self.dataset.data.data[0, n])

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
        g_value = \
            self.VALUE_H*self.parameters["nu_given"].value/self.VALUE_MuB/value
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
        b_value = \
            self.VALUE_H * self.parameters["nu_target"].value \
            / self.VALUE_MuB / value
        return b_value


class BaselineCorrection(aspecd.processing.ProcessingStep):
    """Performs a baseline correction using a polynomial
    previously determined.

    Attributes
    ----------
    coeffs: 'list'
        List of the polynomial coefficients of the polynomial to subtract.
    """

    def __init__(self, coeffs):
        super().__init__()
        self.parameters["coeffs"] = coeffs

    def _perform_task(self):
        """Baseline correction is performed by subtraction of  a
        previously determined polynomial."""
        x = self.dataset.data.data[0, :]
        values_to_subtract = np.polyval(
            np.poly1d(self.parameters["coeffs"]), x)
        for n in range(len(list(self.dataset.data.data[1, :]))):
            self.dataset.data.data[1, n] -= values_to_subtract[n]


class SpectrumSubtract(aspecd.processing.ProcessingStep):
    """Processing routine to subtract a given spectrum, i.e. in general
    a background, from the processed spectrum

    Attributes
    ----------
    scnd_dataset: 'cwepr.dataset.Dataset'
        Dataset containing the spectrum that should be subtracted.
    """
    def __init__(self, scnd_dataset):
        super().__init__()
        self.scnd_dataset = scnd_dataset

    def _perform_task(self):
        """Overriden main method used as wrapper around the :meth: subtract
        method."""
        self.subtract()

    def interpolate(self):
        """Interpolates the spectrum that should be subtracted from the
        other one on the x values of this other spectrum.

        """
        x = self.dataset.data.data[0, :]
        xp = self.scnd_dataset.data.data[0, :]
        fp = self.scnd_dataset.data.data[1, :]
        interpolated_values = np.interp(x, xp, fp)
        return interpolated_values

    def subtract(self):
        """The actual subtraction. The second spectrum (the one gets subtracted
        is first interpolated on the x values of the other one."""
        y_interp = self.interpolate()
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[1, n] -= y_interp[n]
