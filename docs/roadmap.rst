.. include:: <isonum.txt>

=======
Roadmap
=======

A few ideas how to develop the project further, currently a list as a reminder for the main developers themselves, in no particular order, though with a tendency to list more important aspects first:


For version 0.2
===============

* Cleanup

  * Which classes are no longer used/necessary due to having been superseded by ASpecD classes?
  * Which classes may not be sensible any more or are otherwise defunct?
  * Remove classes that are currently only empty (and present due to ASpecD previously not automatically looking up classes in aspecd if not found in cwepr)? Perhaps, it would nevertheless be useful to have a list of classes available and relevant within the ASpecD framework to be present in the documentation at the top of the respective module.
  * Handling of file extensions during import: Currently, they are cut in the init and again appended afterwards. The factory only gives source names without extension.


For version 0.3
===============

* Implement derived importers for Magnettech files

  * Magnettech stores datasets in individual files, be it individual scans for accumulations or different steps in a series of measurements.
  * At least for goniometer, power, and modulation amplitude sweeps, these should be transformed into single datasets.
  * Requires interpolation of data, as each individual dataset has its own *x* axis (usually field).


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

