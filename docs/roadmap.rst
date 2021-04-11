.. include:: <isonum.txt>

=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:

* Processing: create g-axis.

* Implement derived importers for Magnettech files

  * Magnettech stores datasets in individual files, be it individual scans for accumulations or different steps in a series of measurements.
  * At least for goniometer, power, and modulation amplitude sweeps, these should be transformed into single datasets.
  * Requires interpolation of data, as each individual dataset has its own *x* axis (usually field).

* Implement advanced plotters

  * Hot candidates will be plotters for rotation patterns

* Implement all missing processing and analysis tools currently available in the cwepr toolbox developed for MATLAB\ |reg|

* Start to (re)implement functionality test-driven.

* Handling of Magnettech files

  * Renaming to sensible conventions (recursively through directories)

* Batch processing

  * Basic preprocessing, plot, export as PNG/PDF, figure caption for dokuwiki

* Creating/correcting Info files afterwards

  * Read *all* necessary parameters from vendor file format
  * Create/complete/correct info file


Todos
=====

A list of todos, extracted from the code and documentation itself, and only meant as convenience for the main developers. Ideally, this list will be empty at some point.

.. todolist::

