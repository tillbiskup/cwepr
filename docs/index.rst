.. image:: images/zenodo.4896687.svg
   :target: https://doi.org/10.5281/zenodo.4896687
   :align: right

===================
cwepr documentation
===================

Welcome! This is the documentation for cwepr, a Python package for **processing and analysis of continuous-wave electron paramagnetic resonance (cw-EPR) spectra** based on the `ASpecD framework <https://www.aspecd.de/>`_. For general information see its `Homepage <https://www.cwepr.de/>`_. Due to the inheritance from the ASpecD framework, all data generated with the cwepr package are **completely reproducible** and have a complete history.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Have a look at the following example:


.. code-block:: yaml
    :linenos:

    format:
      type: ASpecD recipe
      version: '0.2'

    settings:
      default_package: cwepr

    datasets:
      - /path/to/first/dataset
      - /path/to/second/dataset

    tasks:
      - kind: processing
        type: FrequencyCorrection
        properties:
          parameters:
            frequency: 9.8
      - kind: processing
        type: BaselineCorrection
        properties:
          parameters:
            order: 0
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf


Interested in more real-live examples? Check out the :doc:`use cases section <usecases>` and the growing :doc:`list of examples <examples/index>` providing complete recipes for different needs.



Features
========

A list of features:

* Fully reproducible processing and analysis of cw-EPR data.

* Gap-less record of each processing/analysis step, including explicit and implicit parameters.

* Import of EPR data from diverse sources (Bruker ESP, EMX, Elexsys; Magnettech; NIEHS PEST)

* Generic representation of EPR data, independent of the original format.

* Datasets contain both, numerical data and all crucial metadata, a prerequisite for FAIR data.

* Generic plotting capabilities, easily extendable

* Report generation using pre-defined templates

* Recipe-driven data analysis, allowing tasks to be performed fully unattended in the background


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.7)

* Extensive user and API documentation


Requirements
============

The cwepr package comes with a rather minimal set of requirements:

* Python >= 3.7 with aspecd, numpy, scipy and matplotlib packages
* command-line access for :doc:`recipe-driven data analysis <usecases>`
* :doc:`metadata <metadata>` (in addition to the usual parameter files)
* EPR data in readable formats (details in the :mod:`cwepr.io` (sub)package)


.. _sec-how_to_cite:

How to cite
===========

cwepr is free software. However, if you use cwepr for your own research, please cite both, the article describing it and the software itself:

  * Mirjam Schröder, Till Biskup. cwepr -- a Python package for analysing cw-EPR data focussing on reproducibility and simple usage. *Journal of Magnetic Resonance* **335**:107140, 2022. `doi:10.1016/j.jmr.2021.107140 <https://doi.org/10.1016/j.jmr.2021.107140>`_ | `PDF <https://www.till-biskup.de/_media/de/person/schr-jmr-335-107140-accepted.pdf>`_ | `SI <https://www.till-biskup.de/_media/de/person/schr-jmr-335-107140-si.pdf>`_

  * Mirjam Schröder, Till Biskup. cwepr (2021). `doi:10.5281/zenodo.4896687 <https://doi.org/10.5281/zenodo.4896687>`_

To make things easier, cwepr has a `DOI <https://doi.org/10.5281/zenodo.4896687>`_ provided by `Zenodo <https://zenodo.org/>`_, and you may click on the badge below to directly access the record associated with it. Note that this DOI refers to the package as such and always forwards to the most current version.

.. image:: images/zenodo.4896687.svg
   :target: https://doi.org/10.5281/zenodo.4896687


Where to start
==============

Users new to the cwepr package should probably start :doc:`at the beginning <audience>`, those familiar with its :doc:`underlying concepts <concepts>` may jump straight to the section explaining frequent :doc:`use cases <usecases>`.

Those interested in a hands-on primer on cw-EPR spectroscopy, covering necessary information for how to obtain usable data with your cw-EPR spectrometer, may have a look at the :doc:`cw-EPR primer <cwepr/index>`.

The :doc:`API documentation <api/index>` is the definite source of information for developers, besides having a look at the source code.


Installation
============

To install the cwepr package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install cwepr

Have a look at the more detailed :doc:`installation instructions <installing>` as well.


Actual use cases
================

The cwepr Python package has been used already for analysing published cwepr data, and for some, the data and recipes have been published as "data publications". See the list of :doc:`data publications <examples/data-publications>` for further details.


Related projects
================

There is a number of related packages users of the cwepr package may well be interested in, as they have a similar scope, focussing on spectroscopy and reproducible research.

* `ASpecD <https://docs.aspecd.de/>`_

  A Python framework for the analysis of spectroscopic data focussing on reproducibility and good scientific practice. The framework the cwepr package is based on, developed by T. Biskup.

* `trepr <https://docs.trepr.de/>`_

  Package for processing and analysing time-resolved electron paramagnetic resonance (TREPR) data, originally developed by J. Popp, currently developed and maintained by M. Schröder and T. Biskup.

* `FitPy <https://docs.fitpy.de/>`_

  Framework for the advanced fitting of models to spectroscopic data focussing on reproducibility, developed by T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.



.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   introduction
   concepts
   metadata
   usecases
   installing


.. toctree::
   :maxdepth: 2
   :caption: cw-EPR Primer:
   :hidden:

   cwepr/index
   cwepr/recording
   cwepr/processing
   cwepr/analysis


.. toctree::
   :maxdepth: 2
   :caption: Examples:
   :hidden:

   examples/index
   examples/list
   examples/data-publications


.. toctree::
   :maxdepth: 2
   :caption: Developers:
   :hidden:

   people
   developers
   changelog
   roadmap
   dataset-structure
   api/index


Indices and tables
==================

  * :ref:`genindex`
  * :ref:`modindex`
  * :ref:`search`


License
=======

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**. However, if you use the cwepr package for your own research, please cite it appropriately. See :ref:`How to cite <sec-how_to_cite>` for details.


A note on the logo
==================

The snake (a python) resembles the lines of a cw-EPR spectrum, with additional hyperfine splitting visible at the high-field component. The copyright of the logo belongs to J. Popp.
