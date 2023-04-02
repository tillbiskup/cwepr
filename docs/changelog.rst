=========
Changelog
=========

This page contains a summary of changes between the official cwepr releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/cwepr/commits/master>`_.

Version 0.4.0
=============

Not yet released

New features
------------

* Add Frequency Correction with offset: This keeps the hyperfine splitting values.

* Amplitude sweep importer for Magnettech. Averaging of temperature and Q-Values, which are averaged, a warning is issued if they vary too much.

* Implement Digital Filter into metadata.

* Data is imported according to its file extension specified in the recipe.

* Added support for cwepr-infofile version 0.1.5


Fixes
-----

* Fix bug in analysis.FitOnData by using a helper dataset.

* Fix some metadata in magnettech importer (experiment.runs -> signal_channel.accumulations, correctly import spectrometer metadata, bring time stamp to same timezone.)

* Do range extraction and interpolation (instead of interpolation only) in GoniometerSweepImporter.


Version 0.3.0
=============

Released 2022-07-24

New features
------------

* Add linear fit with fixed intercept to FitOnData, renamed function accordingly.
* Importer for NIEHS dat, lmb, and exp files


Version 0.2.1
=============

Released 2022-06-12

New features
------------

* Reference to publication in documentation and colophon of reports.


Fixes
-----

* Import units correctly using the BES3T importer.
* Magnettech goniometer sweep importer handles situation without info file.
* Fix for import and gathering of metadata of both sources in WinEPR Importer.
* Units are imported correctly from par file in WinEPR importer.


Version 0.2.0
=============

Released 2021-11-28

**Note:** Starting with this version, cwepr requires **Python >=3.7**


New features
------------

* Importer for Bruker EMX/ESP file format (.par/.spc)
* *g* value can be provided for :class:`cwepr.analysis.FieldCalibration`
* New module :mod:`utils` for general-purpose functions regarding cw-EPR spectroscopy
* Functions :func:`cwepr.utils.convert_g2mT` and :func:`cwepr.utils.convert_mT2g` to convert between magnetic field values (in mT) and *g* values
* Plotters can add *g* axis as second axis opposite the magnetic field axis.
* :class:`cwepr.plotting.PowerSweepAnalysisPlotter` for graphical representation of power saturation curves including a second axis with the actual microwave power.
* List of example recipes, available both in the source repository and from the documentation.


Changes
-------

* Renamed class ``FieldCorrectionValue`` to :class:`cwepr.analysis.FieldCalibration`
* :class:`cwepr.processing.FieldCorrection`: Rename parameter ``correction_value`` to ``offset``


Fixes
-----

* :class:`cwepr.processing.GAxisCreation` returns correct *g* axis values
* Reporters do not contain dataset in their dict representation
* :class:`cwepr.io.factory.DatasetImporterFactory` falls back to ASpecD-supported formats if no matching format is found.


Version 0.1.2
=============

Released 2021-06-19

* Correct version on PyPI


Version 0.1.1
=============

Released 2021-06-19

The following bugs have been fixed:

* Bugfix in Normalisation in combination with aspecd
* Bugfix in Magnettech-Import, additional test for InfofileReporter
* Bugfix in GoniometerSweepImporter and Reporter to get correct format of some numbers


Version 0.1.0
=============

Released 2021-06-03

* First public release
* Based on ASpecD v.0.2.1
* List of processing steps specific for cw-EPR data
* List of analysis steps specific for cw-EPR data
* List of plots specific for cw-EPR data
* Importers for different file formats
* Recipe-driven data analysis


Version 0.1.0.dev20
====================

Released 2019-06-15

* First public pre-release on PyPI