"""Module containing composite processing steps.

In the definition of this package, a composite processing step includes both,
processing and analysis. Generally this is the case if a processing step is
performed which uses parameters obtained through an analysis step.
"""

import numpy as np


import aspecd.processing
import cwepr.analysis
import cwepr.processing


class BaselineCorrectionComplete(aspecd.processing.ProcessingStep):
    """Perform fit on spectral data and subtract baseline.

    Wrapper around :class:`cwepr.analysis.BaselineFitting` and
    :class:`cwepr.processing.BaselineCorrectionWithClcdDataset` to fit a
    polynomial on the baseline and subtract it.

    Attributes
    ----------
    order: :class:`int`
        order of the polynomial to be fitted
    percentage: :class:`int`
        percentage of the data to be used for the fit
    """

    def __init__(self, order=0, percentage=10):
        super().__init__()
        self.parameters["order"] = order
        self.parameters["percentage"] = percentage
        self.description = "Complete baseline correction"

    def _perform_task(self):
        baseline_fit_step = cwepr.analysis.BaselineFitting(
            self.parameters["order"], self.parameters["percentage"])
        baseline_analysis = self.dataset.analyse(baseline_fit_step)
        self.parameters["baseline_coefficients"] = baseline_analysis.result
        baseline = aspecd.dataset.CalculatedDataset()
        x = self.dataset.data.axes[0].values
        baseline.data.axes[0].values = x
        baseline.data.data = np.polyval(np.poly1d(self.parameters[
                                            "baseline_coefficients"]), x)
        baseline_correct_step = cwepr.processing.BaselineCorrectionWithClcdDataset(baseline)
        self.dataset.process(baseline_correct_step)


class FieldCorrectionComplete(aspecd.processing.ProcessingStep):
    """Acquire a correction value and apply it to the spectral data.

    Wrapper around :class:`cwepr.analysis.FieldCorrectionValueFinding` and
    :class:`cwepr.processing.FieldCorrection` to find a correction value and
    apply it to the spectral data, i.e. shift the spectrum.

    Attributes
    ----------
    dataset: :class:`cwepr.dataset.Dataset`
        dataset of the field standard measurement
    """

    def __init__(self, dataset=None):
        super().__init__()
        self.parameters["dataset"] = dataset
        self.kind = "standard"
        self.description = "Complete linear field correction"

    def _perform_task(self):
        value_finding_step = cwepr.analysis.FieldCorrectionValueFinding()
        field_analysis = self.parameters["dataset"].analyse(
            value_finding_step)
        self.parameters["correction_value"] = field_analysis.result
        correction_step = cwepr.processing.FieldCorrection(self.parameters["correction_value"])
        self.dataset.process(correction_step)