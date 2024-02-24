"""
Input and output (IO) of information from and to the persistence layer.


.. _sec-supported_file_formats:

Supported file formats
======================

Currently, a number of more or less well-known and widely used EPR file
formats are supported:

===========================  =============  ==========================
Format                       Extensions     Module
===========================  =============  ==========================
Bruker ESP and EMX           par, spc       :mod:`cwepr.io.esp_winepr`
Bruker BES3T                 DSC, DTA       :mod:`cwepr.io.bes3t`
Magnettech (now Bruker) XML  xml            :mod:`cwepr.io.magnettech`
NIEHS PEST                   lmb, exp, dat  :mod:`cwepr.io.niehs`
---------------------------  -------------  --------------------------
Generic text file            txt            :mod:`cwepr.io.txt_file`
===========================  =============  ==========================

For further details, you may have a look at the module documentation of the
individual importer.


General usage
=============

A normal user of the cwepr package will not need to interact explicitly and
directly with the importers, as they are using recipe-driven data analysis.
See the :doc:`use cases section <../usecases>` for an introduction. Here,
importing data is a matter of specifying a list of datasets:

.. code-block:: yaml

    datasets:
      - /path/to/my/first/dataset
      - /path/to/my/second/dataset

The cwepr package will take care of finding the correct importer for you,
thanks to using the :cwepr.io.factory.DatasetImporterFactory` class.

Nevertheless, sometimes you would like to have a bit more control over the
imported datasets, directly setting IDs for referring to the individual
datasets from within the recipe and a label that would show up, *i.a.*,
in the legend of plots:

.. code-block:: yaml

    datasets:
      - source: /path/to/my/first/dataset
        label: cool dataset
        id: data
      - source: /path/to/my/second/dataset
        label: resonator background
        id: background

It should be quite obvious what happens here. Nevertheless, a bit of an
explanation:

* The list of paths got transformed into a list of dictionaries, if you
  like, *i.e.*, key--value pairs, for each dataset.

* The path to the file needs to be given as ``source`` attribute.

* The ``label`` attribute allows to set a label used, *i.a.*, in figure
  legends.

* The ``id`` allows to set a short, memorable name for the dataset you can
  use to refer to it from within the recipe. This is quite useful
  particularly with longer and more complicated paths.


In rare cases, you may have the need of explicitly controlling the importer
used to import your data, and perhaps provide some additional parameters to
the importer as well. Typical use cases would be importing text files:

.. code-block:: yaml

    datasets:
      - source: eprdata.txt
        importer_parameters:
            delimiter: '\t'
            separator: ','
            skiprows: 3
            comments: '%'

Here, the delimiter between columns is the tabulator, the decimal
separator the comma, the first three lines are skipped by default as well
as every line starting with a percent character, as this is interpreted as
comment.

A frequent use case is importing simulations that were carried out with
EasySpin. A MATLAB excerpt for saving the simulated spectrum might look
as follows:


.. code-block:: matlab

    [B_sim_iso, Spc_sim_iso] = garlic(Sys, Exp);

    data = [B_sim_iso', Spc_sim_iso'];
    writematrix(data, 'Simulated-spectrum')


Read in the simulated spectrum with:

.. code-block:: yaml

    datasets:
      - source: Simulated-spectrum.txt
        id: simulation
        importer: TxtImporter
        importer_parameters:
            delimiter: ','


Have a look at the documentation of the individual importer modules,
as well as the documentation of the ASpecD module: :mod:`aspecd.io`.


Metadata
========

Data without context, read: metadata, are usually useless. Hence,
it is strongly recommended to provide appropriate metadata for your EPR
data. Have a look at the :doc:`section on metadata <../metadata>` in the
general user documentation of the cwepr package.


.. important::

    All importers implemented in the cwepr package should automatically read
    Infofiles if they are present. Hence, this is a comparably easy and
    straight-forward way to collect metadata during data acquisition in a
    machine-readable way and to have those metadata accessible from within
    the cwepr package.


Organisation
============

Generally, for each file format (or class of formats), the importer resides
in a separate module. This is due to the rather complicated nature of some
importers (or, more exactly, the underlying file format). For details of
the available importers, have a look at the :ref:`supported file formats
section <sec-supported_file_formats>` above.

In addition to modules for the individual data file formats, there are a
series of more general modules:

* :mod:`cwepr.io.factory`

  Factory classes, currently the DatasetImporterFactory

* :mod:`cwepr.io.exporter`

  Exporters, currently only an ASCII exporter


"""

# The import statements below should *only* import the respective classes.
from .factory import DatasetImporterFactory
from .magnettech import (
    MagnettechXMLImporter,
    GoniometerSweepImporter,
    AmplitudeSweepImporter,
    PowerSweepImporter,
)
from .txt_file import CsvImporter, TxtImporter
from .bes3t import BES3TImporter
from .esp_winepr import ESPWinEPRImporter
from .niehs import NIEHSDatImporter, NIEHSLmbImporter, NIEHSExpImporter
from .exporter import ASCIIExporter, MetadataExporter
