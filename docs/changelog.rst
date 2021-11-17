=========
Changelog
=========

This page contains a summary of changes between the official cwepr releases. Only the biggest changes are listed here. A complete and detailed log of all changes is available through the `GitHub Repository Browser <https://github.com/tillbiskup/cwepr/commits/master>`_.


Version 0.2.0
=============

Not yet released

**Note:** Starting with this version, cwepr requires **Python >=3.7**


New features
------------

* *g* value can be provided for :class:`cwepr.analysis.FieldCalibration`
* New module :mod:`utils` for general-purpose functions regarding cw-EPR spectroscopy
* Functions :func:`cwepr.utils.convert_g2mT` and :func:`cwepr.utils.convert_mT2g` to convert between magnetic field values (in mT) and g values
* :class:`cwepr.plotting.SinglePlotter1D` can add *g* axis as second axis opposite the magnetic field axis.


Changes
-------

* Renamed class ``FieldCorrectionValue`` to :class:`cwepr.analysis.FieldCalibration`
* :class:`cwepr.processing.FieldCorrection`: Rename parameter ``correction_value`` to ``offset``


Fixes
-----

* :class:`cwepr.processing.GAxisCreation` returns correct *g* axis values


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