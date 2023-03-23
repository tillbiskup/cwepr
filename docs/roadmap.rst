.. include:: <isonum.txt>

=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.3.x
=================

* Documentation

  * Metadata for data acquisition: document cwepr info file and alternative methods (and implement importers for alternative methods!)
  * Add "Best Practices" section showing data publications using the package (currently only one: Järsvall et al., Chem. Mater. 2022)
  * Add "prerequisites" section to the index page (and probably more details on a separate page) -- Python, command-line access, metadata, EPR data in readable formats

* Usability

  * Frequency correction should issue a warning (rather than throwing an exception) if no MW frequency value is contained in dataset (yes, such datasets do exist unfortunately).


For version 0.4
===============

* Implement derived importers for Magnettech files

  * Magnettech stores datasets in individual files, be it individual scans for accumulations or different steps in a series of measurements.
  * At least for goniometer, power, and modulation amplitude sweeps, these should be transformed into single datasets.
  * Requires interpolation of data, as each individual dataset has its own *x* axis (usually field).

* Import infofiles in all magnettech importers.

* Handling of file extensions during import: Currently, they are cut in the init and again appended afterwards. The factory only gives source names without extension.

* Implement handling of "RT" as temperature value in the infofile.

* Handling of Magnettech-Files containing the second derivative spectrum i.e. not taking the first spectrum of the xml-file list.

* Import and store filter mode from Magnettech data

* Magnettech: Choose between raw data and data filtered during measurement.

* Logging

* Reorganise templates for reports, according to the directory layout proposed by aspecd (see :mod:`aspecd.report` for details).

* Bugfixes

  * Keep step parameter of magnetic field or not?


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

