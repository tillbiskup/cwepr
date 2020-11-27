===================
cwEPR documentation
===================

Welcome! This is the documentation for cwEPR, a Python package for processing and analysis of continuous-wave electron paramagnetic resonance (cw-EPR) spectra based on the `ASpecD framework <https://www.aspecd.de/>`_. For general information see its `Homepage <https://www.cwepr.de/>`_.


Features
========

A list of features, not all implemented yet but aimed at for the first public release (cwEPR 0.1):

* History of each processing step, automatically generated, aiming at full reproducibility

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


.. toctree::
   :maxdepth: 2
   :caption: User Manual:

   audience
   introduction
   concepts
   usecases


.. toctree::
   :maxdepth: 2
   :caption: cw-EPR Primer:

   cwepr/index
   cwepr/recording
   cwepr/processing
   cwepr/analysis

.. toctree::
   :maxdepth: 2
   :caption: Developers:

   people
   developers
   roadmap
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
