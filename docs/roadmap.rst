.. include:: <isonum.txt>

=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.6
===============

* Implement derived importers for Magnettech files

  * Magnettech stores datasets in individual files, be it individual scans for accumulations or different steps in a series of measurements.
  * At least for goniometer, power, and modulation amplitude sweeps, these should be transformed into single datasets.
  * Requires interpolation of data, as each individual dataset has its own *x* axis (usually field).

* Import infofiles in all magnettech importers.

* Put infofile importer in utils module or elsewhere, to not copy code in every single importer

* Implement handling of "RT" as temperature value in the infofile.

* adapt infofile-importer (in every importer)

* Logging

  * Frequency correction should issue a warning (rather than throwing an exception) if no MW frequency value is contained in dataset (yes, such datasets do exist unfortunately)

* Reorganise templates for reports, according to the directory layout proposed by aspecd (see :mod:`aspecd.report` for details).


* Bugfixes

  * Handle filename with '.' in TxtImporter that is given without extension

  * Keep step parameter of magnetic field or not?

  * Fix docs in txt-file importer module.

  * Check Offset method of Frequency correction. Might be incorrect.


For later versions
==================

* Start to (re)implement functionality test-driven.

* Handling of Magnettech files

  * Renaming to sensible conventions (recursively through directories)

* Batch processing (via recipes?)

  * Basic preprocessing, plot, export as PNG/PDF, figure caption for dokuwiki


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

