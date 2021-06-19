Developer documentation
=======================

Welcome to the developer documentation of the cwEPR package. Unlike the :doc:`API documentation <api/index>`, this part gives some general background information for developers who want to actively contribute to the project.


Virtual environment
-------------------

The whole development should take place inside a virtual python environment that should be located *outside* the project directory.

To create a new virtual python environment, open a terminal and change to a a directory where the virtual environment should reside. Then type something like:


.. code-block:: bash

   virtualenv cwepr


or alternatively:


.. code-block:: bash

  python3 -m venv cwepr


This will create a virtual environment in the directory "cwepr". To activate this virtual environment, use:


.. code-block:: bash

  source cwepr/bin/activate


To deactivate, the command would simply be:


.. code-block:: bash

  deactivate



Autoincrementing version numbers
--------------------------------

The version number is contained in the file ``VERSION`` in the project root directory. To automatically increment the version number with every commit, use a git hook that calls the file ``bin/incrementVersion.sh``. Git hooks reside in the directory ``.git/hooks``. The simplest would be to create a new file ``pre-commit`` in this directory with the following content:


.. code-block:: bash

  #!/bin/sh
  bash bin/incrementVersion.sh


Make sure to set it to executable and have a line break (aka: new or empty line) at the end of the file. Otherwise, you man run into trouble, i.e., not having your version number updated automatically with each commit.


Directory layout
----------------

The cwEPR package follows good practice of the Python community regarding directory layout. As there will be several subpackages available, these reside each in a separate directory containing its own ``__init__.py`` file. All packages/modules reside below the ``cwepr`` directory of the project root. The ``tests`` directory follows the same structure and contains all the module tests. Generally, the cwEPR package should be developed test-driven (test-first) as much as possible.

(This) documentation resides inside the ``docs`` directory of the project root. The auto-generated :doc:`API documentation <api/index>` is in its own directory.

A general overview of the overall package structure::

  bin/
  docs/
      api/
  cwepr/
      io/
  tests/


As you can see, currently there exists one subpackage, namely "io", but others will soon be created as well. For details of the cwEPR package as such, consult its `Homepage <https://www.cwepr.de/>`_.


Docstring format
----------------

The Docstring format used within the code of the cwEPR package is "NumPy". For convenience, set your IDE accordingly.

For PyCharm, the settings can be found in ``Preferences`` > ``Tools`` > ``Python Integrated Tools``. Here, you find a section "Docstrings" where you can select the Docstring format from a number of different formats.


Unittests and test driven development
-------------------------------------

Developing the cwEPR package code should be done test-driven wherever possible. The tests reside in the ``tests`` directory in the respective subpackage directory (see above).

Tests should be written using the Python :mod:`unittest` framework. Make sure that tests are independent of the respective local environment and clean up afterwards (using appropriate ``teardown`` methods).


Setting up the documentation build system
-----------------------------------------

The documentation is built using `Sphinx <https://sphinx-doc.org/>`_, `Python <https://python.org/>`_. Building requires using a shell, for example ``bash``.


To install the necessary Python dependencies, create a virtual environment, e.g., with ``virtualenv <environment>``, and activate it afterwards with ``<environment>/bin/activate``. Then install the dependencies using ``pip``:


.. code-block:: bash

    pip install sphinx
    pip install sphinx-rtd-theme


To build the documentation:

    * Activate the virtual environment where the necessary dependencies are installed in.
    * ``cd`` to ``docs/``, then run ``make html``. (To clean previously built documentation, run ``make clean`` first).


Static code analysis with Prospector
------------------------------------

Static code analysis can be performed using `Prospector <http://prospector.landscape.io/en/master/>`_. First, install the necessary tools into the virtual environment created for the cwEPR package:


.. code-block:: bash

    pip install prospector[all]
    pip install prospector[with_pyroma]


The optional arguments ensure that all necessary dependencies are installed as well.

Afterwards, simply run Prospector from a terminal from within your project root:


.. code-block:: bash

    prospector


It will display the results of the static code analysis within the terminal. Settings can be changed in the ``.prospector.yaml`` file in the project root, but please be very careful changing settings here. Often, it is better to (temporarily) silence warnings in the code itself.

For better readability, the prospector output can get printed into a file. The text output is the most human-readable in my opinion.


.. code-block:: bash

    prospector -o text:prospector-out.txt



