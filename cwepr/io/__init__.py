"""
Subpackage for IO.

Generally, for each file format, the importer resides in a separate module.
The import statements below should *only* import the respective classes.

Currently, in addition to modules for the individual data file formats,
there are a series of more general modules:

* errors

  Error classes used throughout the other modules

* general

  General classes such as the GeneralImporter that will become InfofileMixin

* factory

  Factory classes, currently the DatasetImporterFactory

* exporter

  Exporters, currently only an ASCII exporter


"""

from .factory import DatasetImporterFactory
from .magnettech import MagnettechXmlImporter
from .exporter import ASCIIExporter
from .txt_file import TxtImporter