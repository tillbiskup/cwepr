"""Module containing all processing steps.

A processing step is anything that modifies the dataset without giving an
a independent result. E.g., Field Correction or Baseline correction.
"""

import numpy as np
from scipy import signal

import aspecd.processing


class FieldCorrection(aspecd.processing.ProcessingStep):
    """Perform field correction of the data with a correction
    value previously determined.

    Parameters
    ----------
    correction_value: :class:'float'
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

    Attributes
    ----------
    nu_given: :class:'float'
        Given frequency of the data present.

    nu_target: :class:'float'
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
         value: :class:'float'
         B value to transform.

        Returns
        -------
        g_value: :class:'float'
        Transformed value.
        """
        g_value = self.VALUE_H*self.parameters["nu_given"].value \
            / self.VALUE_MuB/value
        return g_value

    def _transform_to_b(self, value):
        """Transforms a g axis value to a field (B) axis value.

        Parameters
        ----------
        value: :class:'float'
        g value to transform.

        Returns
        -------
        b_value: :class:'float'
        Transformed value.
        """
        b_value = self.VALUE_H * self.parameters["nu_target"].value \
            / self.VALUE_MuB / value
        return b_value


class BaselineCorrection(aspecd.processing.ProcessingStep):
    """Performs a baseline correction using a polynomial
    previously determined.

    Attributes
    ----------
    coeffs: :class:'list'
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


class SubtractSpectrum(aspecd.processing.ProcessingStep):
    """Processing routine to subtract a given spectrum, i.e. in general
    a background, from the processed spectrum

    Attributes
    ----------
    scnd_dataset: :class:'cwepr.dataset.Dataset'
        Dataset containing the spectrum that should be subtracted.
    """
    def __init__(self, scnd_dataset):
        super().__init__()
        self.scnd_dataset = scnd_dataset

    def _perform_task(self):
        """Overridden main method used as wrapper around the :meth: subtract
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
        is first interpolated on the x values of the other one.
        """
        y_interp = self.interpolate()
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[1, n] -= y_interp[n]


class PhaseCorrection(aspecd.processing.ProcessingStep):
    """Processing step for phase correction.

    The functionality is suitable for automatic phase correction, no
    parameters need to be provided manually.
    """
    def __init__(self):
        super().__init__()

    def _perform_task(self):
        """Perform the actual phase correction. The phase angle is
        acquired from the dataset's metadata and transformed to radians
        if necessary.
        The phase correction is then applied and the corrected data inserted
        into the dataset.
        """
        phaseangle_raw = self.dataset.metadata.signal_channel.phase
        self.parameters["phaseangle_value"] = phaseangle_raw.value
        self.parameters["phaseangle_unit"] = phaseangle_raw.unit
        if self.parameters["phaseangle_unit"] == "deg":
            self.parameters[
                "phaseangle_value"] = (
                        np.pi * self.parameters["phaseangle_value"]) / 180
            self.parameters["phaseangle_unit"] = "rad"

        data = self.dataset.data.data
        data_imag = signal.hilbert(data)
        data_imag = np.exp(-1j*self.parameters["phaseangle_value"])*data_imag
        data_real = np.real(data_imag)
        self.dataset.data.data = data_real


class NormaliseMaximum(aspecd.processing.ProcessingStep):
    """Normalises a spectrum concerning the height of the maximum.

    Should only be used on an integrated spectrum.
    """
    def __init__(self):
        super().__init__()

    def _perform_task(self):
        maximum = max(self.dataset.data.data[0, :])
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] /= maximum


class NormaliseArea(aspecd.processing.ProcessingStep):
    """Normalises a spectrum concerning the area under the curve.

    Should only be used on an integrated spectrum.

    Parameters
    ----------
    integral: :class:'float'
        Area under the curve.
    """
    def __init__(self, integral):
        super().__init__()
        self.parameters["integral"] = integral

    def _perform_task(self):
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] /= self.parameters["integral"]


class NormaliseScanNumber(aspecd.processing.ProcessingStep):
    """Normalises a spectrum concerning the area under the curve.

    This is necessary to make spectra where the intensity of different scans
    is added comparable to ones where it is averaged.
    """
    def __init__(self):
        super().__init__()

    def _perform_task(self):
        self.parameters["scannumber"] = \
            self.dataset.metadata.signal_channel.accumulations
        for n in range(len(self.dataset.data.data[0, :])):
            self.dataset.data.data[0, n] /= self.parameters["scannumber"]

