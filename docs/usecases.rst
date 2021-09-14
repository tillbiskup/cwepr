=========
Use cases
=========

This section provides a few ideas of how basic operation of the cwepr package may look like. It focusses on **recipe-driven data analysis** as its user-friendly interface that does not require the spectroscopist to know anything about programming and allows to fully focus on the actual data processing and analysis.

As a user, you write "recipes" in form of human-readable YAML files telling the application which tasks to perform on what datasets. This allows for fully unattended, automated and scheduled processing of data, eventually including simulation and fitting. At the same time, it allows you to analyse the data without need for actual programming.

Actually, there are two steps to recipe-driven data analysis:

* Writing a recipe, specifying what tasks shall be performed to which datasets.

* Serving the recipe by typing a single command on the terminal.

To give you a first example, here is a short recipe, followed by the command you need to issue in the terminal:


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

The details of what happens here with this recipe will be detailed below, but it should nevertheless be pretty self-explaining. Suppose you have saved this recipe to a YAML file named ``my-first-recipe.yaml``. Then the only thing you need to do to actually "serve" the recipe and get the figure created is issuing the following command in a terminal:

.. code-block:: bash

    serve my-first-recipe.yaml

If you wonder where the command ``serve`` comes from: This gets installed when you install the cwepr Python package (or, to be exact, by installing its dependency, the ASpecD package). Hence, it may only be available from within a Python virtual environment if you installed cwepr this way (what is generally preferrable for Python packages).


Anatomy of a recipe
===================

Recipes always consist of two major parts: A list of datasets to operate on, and a list of tasks to be performed on the datasets. Of course, you can specify for each task on which datasets it should be performed, and if possible, whether it should be performed on each dataset separately or combined. The latter is particularly interesting for representations (e.g., plots) consisting of multiple datasets, or analysis steps spanning multiple datasets.

Therefore, in a recipe that is basically a YAML file, you will always find three keys on the highest level: ``datasets``, ``tasks``, and at the very top, the statement ``default_package: cwepr`` telling that you are using the cwepr package. There are, however, a few additional (optional) keys that may appear on the highest level, setting such things as the default source directory for datasets and the default output directory for figures and reports. A recipe written as history from cooking another recipe will additionally automatically contain information on the system and versions of the software packages used.

For more details and a `more thorough introduction to recipe-driven analysis <https://docs.aspecd.de/usecases.html>`_, have a look at the documentation of the underlying `ASpecD framework <https://docs.aspecd.de/usecases.html>`_. Here, we will focus on the most basic aspects of processing and analysing cw-EPR data.


Importing datasets
==================

The first step in analysing data is to import them. In terms of recipe-driven data analysis, you only need to specify a unique identifier for your dataset, usually (for the time being) a (relative or absolute) path to a file accessible from your file system.

.. code-block:: yaml

    datasets:
      - /path/to/my/first/dataset
      - /path/to/my/second/dataset


At the same time, the paths are used to refer to the datasets internally within the recipe. Such references are frequently used if you want to perform a task not for all datasets, but only a subset of the datasets specified on top of a recipe. If you say now that always having to provide the full path to a dataset is error-prone and not user-friendly, stay tuned and continue reading: we got you covered.

A few comments on the syntax: ``datasets:`` is the key on the highest level, and the trailing colon ``:`` marks it as key (for a dictionary or associative array). The datasets are given as a list, using the leading minus ``-``. Whether you use tabs or spaces for indentation does not matter, as long as the indentation within one block is consistent. If you're not familiar with the YAML syntax, it is highly recommended to have a look on one of the many resources available online.

Additionally, you can set IDs and labels for the datasets and even import datasets from other packages. For details, again, you are referred to the `documentation of the ASpecD framework <https://docs.aspecd.de/usecases.html>`_.


Operating on datasets
=====================

Different operations can be performed on datasets, and the cwepr package distinguishes between processing and analysis tasks, for starters. The first will operate directly on the data of the dataset, alter them accordingly, and result in an altered dataset. The second will operate on the data of a dataset as well, but return an independent result, be it a scalar, a vector, or even a (new) dataset.

Operations on datasets are defined within the ``tasks:`` block of a recipe, like so:

.. code-block:: yaml

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


You can see already the general structure of how to define a task as well as a number of important aspects. Tasks are items in a list, hence the prepending ``-``. Furthermore, for each task, you need to provide both, kind and type. Usually, the "kind" is identical to the (cwepr) module the respective class used to perform the task is located in, such as "processing". There are, however, special cases where you need to be more specific, as in cases of plots (more later). The "type" always refers to the class name of the object eventually used to perform the task.

Another aspect shown already in the example above is how to set properties for the individual tasks using the "properties" keyword. Which properties you can set depends on the particular type of task and can be found in the API documentation. In the example given above, you set the "parameters" property of the :obj:`cwepr.processing.FrequencyCorrection` and :obj:`cwepr.processing.BaselineCorrection` objects.

So what did we actually do here with our two datasets loaded? For both datasets, we performed a frequency correction to account for the different microwave frequencies used during data recording by using the :class:`cwepr.processing.FrequencyCorrection` class, and afterwards, we performed a baseline correction using the :class:`cwepr.processing.BaselineCorrection` class to get rid of any drifts and offsets in the data. These two very basic processing steps are what you usually need to do for cw-EPR data prior to further process and analyse them, let alone plot them. Of course, if you were only ever interested in a single dataset, a frequency correction would not strictly be necessary, but as soon as you compare datasets, this is mandatory.

There is much more you can do with tasks, such as applying a task only to a subset of the datasets loaded or storing the results in variables to be accessed later. Again, we ask you to have a look at the `documentation of the ASpecD framework <https://docs.aspecd.de/usecases.html>`_ for these more advanced features.


Can we see something?
=====================

One of the strengths of recipe-driven data analysis is that it can run fully unattended in the background or on some server even not having any graphical display attached. However, data analysis always yields some results we would like to look at. The easiest way to achieve this is to create graphical representations of your results. Therefore, the clearcut answer to the question is: Yes, we can (see something).

The importance of graphical representations for data processing and analysis cannot be overestimated. Hence, a typical use case is to generate plots of a dataset following individual processing steps. As recipes work in a non-interactive mode, saving these plots to files is a prerequisite. The most simple and straight-forward graphical representation for cw-EPR data preprocessed in the way shown above would be defined in a recipe as follows:

.. code-block:: yaml

    tasks:
      - kind: singleplot
        type: SinglePlotter1D
        properties:
          filename:
            - first-dataset.pdf
            - second-dataset.pdf

This will create a simple plot of the two one-dimensional datasets loaded using default settings and store the result to the files ``first-dataset.pdf`` and ``second-dataset.pdf``. As long as the list of datasets the plotter is employed for matches the number of filenames provided, everything should work smoothly.

Of course, there is a lot more to plotting (actually, plotting is probably one of the most complicated tasks one can imagine), and you can not only choose between a list of diverse plotters, but control the appearance of each individual plot in great detail. Furthermore, you may be interested in specifying an output directory for all the plots, not to get lost in zillions of files automatically created, or even in automatically saving plots without specifying filenames.

As always, all this and more can be found in the `documentation of the ASpecD framework <https://docs.aspecd.de/usecases.html>`_ and in the documentation of the individual plotter classes in the :mod:`cwepr.plotting` module. Even better, thanks to the modular nature of the ASpecD framework and the packages building upon it, such as the cwepr package, you can use all the functionality provided by the ASpecD framework.

Of course, the examples shown above only scratch on the very surface of what is possible, but they should give you an idea how working with the cwepr package looks like -- and why it is fun. Always remember: The cwepr package is there to make processing and analysing cw-EPR data as easy, simple, and convenient as possible, while bringing **reproducibility** to a complete new level. It is up to you to use the tools at your hand in new and creative ways for the best of science.
