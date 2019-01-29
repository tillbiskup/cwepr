=================
The cwEPR Package
=================

The cwEPR package consists of different modules for handling experimental data from continuous wave EPR (cwEPR) experiments and is derived from the `ASpecD framework <https://www.aspecd.de/>`_.

General Ideas
=============

This package is built on the general ideas outlined in the `AspecD documentation <https://docs.aspecd.de/>`_, the most important being the reproducibility of scientific data analysis. The idea of reproducibility is a fundamental concept of science. It relies on the complete documentation of additional information relevant for the numeric data, termed metadata, *i.e.* experimental conditions and parameters as well as a history of every working step performed on this data. This process is complicated and rather tedious to perform manually. Therefore, it is a fundamental functionality of ASpecD and also of this derived package to make the metadata generation as automatic, easy and complete as possible. The aim is to provide a complete experimental documentation and gap-less coverage of all processing and analysis steps applied. In this perspective, any dataset at any point should be easy to trace back to the original raw data, the same being true for any type of representation, including but not limited to tables and plots. 
To ensure the gap-less documentation the ASpecD framework and the derived cwEPR package unite the numeric data, the respective metadata and a history of processing and analysis including all parameters employed. For any single set of numeric data this unit is a dataset. 
To be easy to use and future-proof the project is extensively documented and open-source allowing for easily creating new derived modules and functionality for any purpose. Additionally, it is worth mentioning that this package, as well as the ASpecD framework have a highly modular structure based on object-oriented programming which further simplifies this task.

Modules and functionality
=========================

The package uses the fundamental concept of the dataset as defined in ASpecD, uniting numeric data and metadata. Importers allow loading raw data, usually obtained directly from a spectrometer, for processing, while exporters allow exporting the processed data in easily accessible format. This allows to integrate the package into a work-flow involving independent processing software or to use it in cooperations involving scientists using different software.
The :mod:`cwepr.processing` module includes different routines to modify the data without yielding an independent result, *e.g.* field correction, phase correction and baseline correction.
The :mod:`cwepr.analysis` module includes different routines applied to the data yielding independent results, *e.g.* integration and determination of parameters for field correction and baseline correction.
The :mod:`cwepr.plotting` module includes multiple routines for creating highly customizable plots of the data for different purposes.

Detailed explanation
====================
Hereafter, the different possible processing and analysis routines are explained more in detail.

Baseline Correction
===================
The baseline correction makes use of two different routines: The BaselineFitting (analysis module) and BaselineCorrection (processing module). The former determines a polynomial for the baseline using the outer parts of the spectrum for a fit and a user-specified order for the polynomial and yields the polynomial coefficients as result. The latter performs the actual baseline correction by subtracting the polynomial from the spectrum.

Field Correction
================
The field correction makes use of two different routines: :class:`cwepr.analysis.FieldCorrectionValueFinding` (:mod:`cwepr.analysis` module) and :class:`cwepr.processing.FieldCorrection` (:mod:`cwepr.processing` module). The former determines a correction value from a field standard spectrum, the latter performs the actual correction by shifting the field axis by the value determined.

Frequency Correction
====================
:class:`cwepr.processing.FrequencyCorrection` is a routine of the :mod:`cwepr.processing` module used for transforming a spectrum to a different frequency which is useful for comparing spectra and a prerequisite for subtracting spectra. In the process the field axis, :math:`B_0`,  of the spectrum is transformed to a *g* axis using formula (1) and the respective original microwave frequency :math:`{\nu}_1`, then transformed back into a field axis using formula (2) and the target microwave frequency :math:`{\nu}_2`.

(1) :math:`g = \frac {h {\nu}_1 }{{\mu}_{\text{B}} B_0}`

|
(2) :math:`B_0 = \frac {h {\nu}_2 }{{\mu}_{\text{B}} g}`

Here, *h* is the Planck constant and :math:`{\mu}_{\textrm{B}}` Bohr’s magneton.

Subtracting Spectra
===================
The :class:`cwepr.processing.SubtractSpectrum` routine (:mod:`cwepr.processing` module) allows for subtracting a curve (usually a background spectrum) from a given dataset’s spectrum. The class uses interpolation automatically, though it is advisable to check the axis limits of both curves/spectra prior to subtraction. This is not done automatically, but the cwEPR package contains the routine :class:`cwepr.analysis.CommonspaceAndDelimiters` specifically designed for this purpose that will raise an error if the common axis space is rather small.

Phase Correction
================
The :class:`cwepr.processing.PhaseCorrection` routine (:mod:`cwepr.processing` module) performs a parameter-free correction. This is done by obtaining the imaginary part of the spectrum through a Hilbert transform. After rotation by the phase angle :math:`\gamma` (obtained from the metadata), using formula (3), the real part of the spectrum is retrieved.


(3) :math:`S_{\text{new}} = {\text{e}}^{-i\gamma} \cdot S_{\text{old}}`

Here, *S* is the spectral data, *i.e.* the intensities.

Normalisation
=============
The :mod:`cwepr.processing` module contains two routines for normalisation of spectra: :class:`cwepr.processing.NormaliseMaximum` for a normalisation concerning the intensity maximum and :class:`cwepr.processing.NormaliseArea` for one concerning the area under the curve. A third variant, :class:`cwepr.processing.NormaliseScanNumber`, is useful in cases where multiple scans of a spectrum are added rather than averaged.

Integration
===========
The :mod:`cwepr.analysis` module contains two routines for integration: :class:`cwepr.analysis.IntegrationIndefinite` performs an integration yielding a new function (*i.e.* a new set of *y* values) This routine is used to obtain the absorption spectrum from the first derivative spectrum. :class:`cwepr.analysis.IntegrationDefinite` yields a numeric value (*i.e.* the area under the curve). This is useful for comparing spectra and for quantification, *inter alia*.


