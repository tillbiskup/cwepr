=========
Use Cases
=========

The following use cases provide detailed hands-on examples of how to use the cwepr package for processing and analysing cw-EPR data. The cases range from simply plotting the data as recorded to complex tasks such as power and modulation amplitude sweeps and analysis of rotation patterns.

Familiarity with the underlying concepts of :doc:`recording <cwepr/recording>`, :doc:`processing <cwepr/processing>` and :doc:`analysing <cwepr/analysis>` cw-EPR data is assumed. If this is not the case, have a look at the respective sections of the short :doc:`cw-EPR primer <cwepr/index>`.

For each of the use cases, it is assumed that you have the cwepr package and all its prerequisites installed, best in a local Python virtual environment. Besides that, many of the use cases can be followed using the sample data available in the ``tests`` directory of the source code hosted, *e.g.*, on `GitHub <https://github.com/tillbiskup/cwepr/>`_.


First overview of a spectrum
============================

Usually, the first thing you need to do after recording data is to have a look at them. While you can and will mostly do that immediately after the measurement using the spectrometer control software, it comes in quite handy to have a graphical representation stored somewhere, perhaps in an (electronic) lab notebook.

These are the ingredients necessary to get a graphical representation of your data that will end as a file on your hard drive:

  * dataset
  * plotter
  * plot saver

Of course, you can do all that from a Python command line::

  import cwepr.dataset
  import cwepr.plotting

  source = "path/to/saved/data"
  figure_file = "path/to/file/to/save/plot/to"

  dataset_factory = cwepr.dataset.DatasetFactory()
  dataset = dataset_factory.get_dataset(source)

  plotter = cwepr.plotting.SimpleSpectrumPlotter()
  plotter = dataset.plot(plotter)
  saver = cwepr.plotting.Saver(filename=figure_file)
  plotter.save(saver)


However, you could as well write a recipe (actually, a YAML file) doing the same for you:

.. code-block:: yaml

    default_package: cwepr

    datasets:
      - path/to/saved/data

    tasks:
      -
        kind: plotting
        type: SimpleSpectrumPlotter
        properties:
          filename: path/to/file/to/save/plot/to


Now, the only thing left to do is to get that recipe cooked and the results served. There are two general ways how to achieve that: programmatically from within Python, or a simple call from the command-line.

From within Python, you would first create an instance of the :class:`aspecd.tasks.ChefDeService` class and afterwards call its :meth:`aspecd.tasks.ChefDeService.serve` method to get the desired results::

    import aspecd.tasks
    chef_de_service = aspecd.tasks.ChefDeService
    chef_de_service.serve('<your_recipe_name>.yaml')

And from a terminal, you could simply type:

.. code-block:: bash

    serve <your_recipe_name>.yaml

Both will automatically ensure the correct DatasetFactory to be loaded, provided you didn't forget to set the ``default_package`` directive, as shown in the recipe above.

After all, using recipes is highly recommended for most users, and as you will normally need to get your result in some representation anyway, having a plot or other representation as (final) output is a very sensible idea.

Frequency and field correction
==============================


Normalising spectra (maximum, amplitude, area)
==============================================


Comparing multiple spectra
==========================


Power sweep analysis
====================


Modulation sweep analysis
=========================


Rotation pattern analysis
=========================


