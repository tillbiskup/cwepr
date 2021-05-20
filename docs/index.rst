===================
cwEPR documentation
===================

Welcome! This is the documentation for cwEPR, a Python package for **processing and analysis of continuous-wave electron paramagnetic resonance (cw-EPR) spectra** based on the `ASpecD framework <https://www.aspecd.de/>`_. For general information see its `Homepage <https://www.cwepr.de/>`_.Due to the inheritance from the ASpecD framework, all data generated with the trepr package are completely reproducible and have a complete history.

What is even better: Actual data processing and analysis **no longer requires programming skills**, but is as simple as writing a text file summarising all the steps you want to have been performed on your dataset(s) in an organised way. Curious? Have a look at the following example:


.. code-block:: yaml
    :linenos:

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
      - kind: aspecd.processing
        type: BaselineCorrection
        properties:
          parameters:
            order: 0
      - kind: aspecd.singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf


Interested in more real-live examples? Check out the :doc:`use cases section <usecases>`.



Features
========

A list of features, not all implemented yet but aimed at for the first public release (cwEPR 0.1):

* Fully reproducible processing of cw-EPR data

* Import of EPR data from diverse sources (Bruker ESP, EMX, Elexsys; Magnettech)

* Generic plotting capabilities, easily extendable

* Report generation using pre-defined templates

* Recipe-driven data analysis, allowing tasks to be performed fully unattended in the background


And to make it even more convenient for users and future-proof:

* Open source project written in Python (>= 3.5)

* Extensive user and API documentation


.. warning::
  The cwEPR package is currently under active development and still considered in Alpha development state. Therefore, expect frequent changes in features and public APIs that may break your own code. Nevertheless, feedback as well as feature requests are highly welcome.


Where to start
==============

Users new to the cwEPR package should probably start :doc:`at the beginning <audience>`, those familiar with its :doc:`underlying concepts <concepts>` may jump straight to the section explaining frequent :doc:`use cases <usecases>`.

Those interested in a hands-on primer on cw-EPR spectroscopy, covering necessary information for how to obtain usable data with your cw-EPR spectrometer, may have a look at the :doc:`cw-EPR primer <cwepr/index>`.

The :doc:`API documentation <api/index>` is the definite source of information for developers, besides having a look at the source code.


Installation
------------

To install the cwepr package on your computer (sensibly within a Python virtual environment), open a terminal (activate your virtual environment), and type in the following:

.. code-block:: bash

    pip install cwepr

Have a look at the more detailed :doc:`installation instructions <installing>` as well.


Related projects
----------------

There is a number of related packages users of the trepr package may well be interested in, as they have a similar scope, focussing on spectroscopy and reproducible research.

* `ASpecD <https://docs.aspecd.de/>`_

  A Python framework for the analysis of spectroscopic data focussing on reproducibility and good scientific practice. The framework the trepr package is based on, developed by T. Biskup.

* `trepr <https://docs.trepr.de/>`_

  Package for processing and analysing time-resolved electron paramagnetic resonance (TREPR) data, developed by J. Popp and maintained by T. Biskup.

You may as well be interested in the `LabInform project <https://www.labinform.de/>`_ focussing on the necessary more global infrastructure in a laboratory/scientific workgroup interested in more `reproducible research <https://www.reproducible-research.de/>`_. In short, LabInform is "The Open-Source Laboratory Information System".

Finally, don't forget to check out the website on `reproducible research <https://www.reproducible-research.de/>`_ covering in more general terms aspects of reproducible research and good scientific practice.



.. toctree::
   :maxdepth: 2
   :caption: User Manual:
   :hidden:

   audience
   introduction
   concepts
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

This program is free software: you can redistribute it and/or modify it under the terms of the **BSD License**.


A note on the logo
==================

The snake (a python) resembles the lines of a cw-EPR spectrum, with additional hyperfine splitting visible at the high-field component. The copyright of the logo belongs to J. Popp.
