"""
Subpackage for IO.

Generally, for each file format (or class of formats), the importer resides
in a separate module.

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

In addition to modules for the individual data file formats, there are a
series of more general modules:

* factory

  Factory classes, currently the DatasetImporterFactory

* exporter

  Exporters, currently only an ASCII exporter


"""

# The import statements below should *only* import the respective classes.
from .factory import DatasetImporterFactory
from .magnettech import MagnettechXMLImporter, GoniometerSweepImporter
from .txt_file import TxtImporter
from .bes3t import BES3TImporter
from .esp_winepr import ESPWinEPRImporter
from .niehs import NIEHSDatImporter, NIEHSLmbImporter, NIEHSExpImporter
from .exporter import ASCIIExporter, MetadataExporter
