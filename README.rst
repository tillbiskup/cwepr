cwEPR
=====

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4896687.svg
   :target: https://doi.org/10.5281/zenodo.4896687
   :align: right

The cwEPR package provides tools for handling experimental data obtained using continuous-wave EPR (cwEPR) spectroscopy and is derived from the `ASpecD framework <https://www.aspecd.de/>`_. Due to inheriting from the ASpecD superclasses, all data generated with the cwepr package are completely reproducible and have a complete history.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Have a look at the following example::

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

For more general information on the cwepr package and for how to use it, see its `documentation <https://doc.cwepr.de/>`_.


Features
--------

A list of features:

- Fully reproducible processing of cw-EPR data
- Import of EPR data from diverse sources (Bruker ESP, EMX, Elexsys; Magnettech)
- Generic plotting capabilities, easily extendable
- Report generation using pre-defined templates
- Recipe-driven data analysis, allowing tasks to be performed fully unattended in the background

And to make it even more convenient for users and future-proof:

- Open source project written in Python (>= 3.7)
- Extensive user and API documentation


Target audience
---------------

The cwepr package addresses scientists working with cwEPR data (both, measured and calculated) on a daily base and concerned with `reproducibility <https://www.reproducible-research.de/>`_. Due to being based on the `ASpecD framework <https://www.aspecd.de/>`_, the cwepr package ensures reproducibility and---as much as possible---replicability of data processing, starting from recording data and ending with their final (graphical) representation, e.g., in a peer-reviewed publication. This is achieved by automatically creating a gap-less record of each operation performed on your data. If you do care about reproducibility and are looking for a system that helps you to achieve this goal, the cwepr package may well be interesting for you.


How to cite
-----------

cwepr is free software. However, if you use cwepr for your own research, please cite both, the article describing it and the software itself:

  * Mirjam Schröder, Till Biskup. cwepr -- a Python package for analysing cw-EPR data focussing on reproducibility and simple usage. *Journal of Magnetic Resonance* **335**:107140, 2022. `doi:10.1016/j.jmr.2021.107140 <https://doi.org/10.1016/j.jmr.2021.107140>`_ | `PDF <https://www.till-biskup.de/_media/de/person/schr-jmr-335-107140-accepted.pdf>`_ | `SI <https://www.till-biskup.de/_media/de/person/schr-jmr-335-107140-si.pdf>`_

  * Mirjam Schröder, Till Biskup. cwepr (2021). `doi:10.5281/zenodo.4896687 <https://doi.org/10.5281/zenodo.4896687>`_

To make things easier, cwepr has a `DOI <https://doi.org/10.5281/zenodo.4896687>`_ provided by `Zenodo <https://zenodo.org/>`_, and you may click on the badge below to directly access the record associated with it. Note that this DOI refers to the package as such and always forwards to the most current version.

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4896687.svg
   :target: https://doi.org/10.5281/zenodo.4896687


Related projects
----------------

There is a number of related packages users of the cwepr package may well be interested in, as they have a similar scope, focussing on spectroscopy and reproducible research.

* `ASpecD <https://docs.aspecd.de/>`_

  A Python framework for the analysis of spectroscopic data focussing on reproducibility and good scientific practice. The framework the cwepr package is based on, developed by T. Biskup.

* `trepr <https://docs.trepr.de/>`_

  Package for processing and analysing time-resolved electron paramagnetic resonance (TREPR) data, originally developed by J. Popp, currently developed and maintained by M. Schröder and T. Biskup.

* `FitPy <https://docs.fitpy.de/>`_

  Framework for the advanced fitting of models to spectroscopic data focussing on reproducibility, developed by T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.


Installation
------------

Install the package by running::

    pip install cwepr


License
-------

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.
