"""Module containing composite processing steps.

In the definition of this package, a composite processing step_width includes both,
processing and analysis. Generally this is the case if a processing step_width is
performed which uses parameters obtained through an analysis step_width.

This module exists for logical as well as technical reasons:
1) It is not sensible to put combined processing and analysis in either of
those modules.
2) Both processing and analysis importing each other leads to infinite
recursion.
"""

from copy import deepcopy

import numpy as np

import aspecd.processing
import aspecd.analysis
import cwepr.analysis
import cwepr.processing


class BaselineCorrection(aspecd.processing.ProcessingStep):
    """Perform fit on spectral data and subtract baseline.

    Wrapper around :class:`cwepr.analysis.PolynomialBaselineFitting` and
    :class:`cwepr.processing.BaselineCorrectionWithCalculatedDataset`
    to fit a polynomial on the baseline and subtract it.

    Attributes
    ----------
    order: :class:`int`
        order of the polynomial to be fitted

    percentage: :class:`int`
        percentage of the data to be used for the fit default is 10% (per side)

    """

    def __init__(self, order=0, percentage=10):
        super().__init__()
        self.parameters["order"] = order
        self.parameters["percentage"] = percentage
        self.description = "Complete baseline correction"

    def _perform_task(self):
        baseline_fit_step = cwepr.analysis.PolynomialBaselineFitting(
            self.parameters["order"], self.parameters["percentage"])
        baseline_analysis = self.dataset.analyse(baseline_fit_step)
        self.parameters["baseline_coefficients"] = baseline_analysis.result
        baseline = aspecd.dataset.CalculatedDataset()
        x_coordinates = self.dataset.data.axes[0].values
        baseline.data.axes[0].values = x_coordinates
        baseline.data.data = np.polyval(np.poly1d(self.parameters[
                                        "baseline_coefficients"]),
                                        x_coordinates)
        baseline_correct_step = \
            cwepr.processing.BaselineCorrectionWithCalculatedDataset(baseline)
        self.dataset.process(baseline_correct_step)


class FieldCorrection(aspecd.processing.ProcessingStep):
    """Acquire a correction value and apply it to the spectral data.

    Wrapper around :class:`cwepr.analysis.FieldCorrectionValue` and
    :class:`cwepr.processing.FieldCorrection` to find a correction value and
    apply it to the spectral data, i.e. shift the spectrum.

    Attributes
    ----------
    dataset: :class:`cwepr.dataset.ExperimentalDataset`
        dataset of the field standard measurement

    """

    def __init__(self, dataset=None):
        super().__init__()
        self.parameters["dataset"] = dataset
        self.kind = "standard"
        self.description = "Complete linear field correction"

    def _perform_task(self):
        value_finding_step = cwepr.analysis.FieldCorrectionValue()
        field_analysis = self.parameters["dataset"].analyse(
            value_finding_step)
        self.parameters["correction_value"] = field_analysis.result
        correction_step = \
            cwepr.processing.FieldCorrection(self.parameters[
                                             "correction_value"])
        self.dataset.process(correction_step)


class IntegrationIndefinite(aspecd.analysis.SingleAnalysisStep):
    """Performs an indefinite integration.

    Yield the integral function as new dataset.
    """

    def __init__(self):
        super().__init__()
        self.description = "Indefinite Integration"

    def _perform_task(self):
        """Perform indefinite integration on copy of dataset."""
        integral_dataset = deepcopy(self.dataset)
        integration_step = cwepr.processing.Integration()
        integral_dataset.process(integration_step)
        self.result = integral_dataset
