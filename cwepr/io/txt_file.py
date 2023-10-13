"""
Importer for simple text and CSV files.

Despite its obvious limitations (normally no metadata, limited resolution,
large files) text or CSV files are an often-encountered exchange format and
can serve as an easy way to import data from otherwise not supported file
formats, as nearly every software to record data allows to export these data
as simple text or CSV files.

You may have a look as well at the importers provided by the ASpecD package
for similar situations, particularly :class:`aspecd.io.TxtImporter`.
"""
import io
import numpy as np

import aspecd.io


class TxtImporter(aspecd.io.DatasetImporter):
    """
    Simple importer for txt files containing data.

    Sometimes, data come from sources as a txt file only. So far, the format
    is hardcoded and should contain two columns separated by a tabulator.
    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.extension = '.txt'

    def _import(self):
        self._get_data()
        self._create_metadata()

    def _get_data(self):
        if self.source.endswith('.txt'):
            self.source = self.source[:-4]

        self.source = self.source + self.extension
        raw_data = np.loadtxt(self.source, delimiter='\t')
        self.dataset.data.data = raw_data[:, 1]
        self.dataset.data.axes[0].values = raw_data[:, 0]

    def _create_metadata(self):
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'


class CsvImporter(aspecd.io.DatasetImporter):
    """
    Importer for simple csv imports with different delimiters.

    Can import csv files as well as txt files, the latter only, if the
    extension is given in the recipe.

    As this function is used sometimes for the import of simulations that
    were made with EasySpin, the importer adds three values as metadata in
    order to get the axis label for the magnetic field axis correctly:

    * Unit of the first axis: mT

    * Quantity of the fist axis: magnetic field

    * Quantity of the second axis: intensity

    A matlab excerpt for saving the simulated spectrum might look as follows:


    .. code-block:: matlab

        [B_sim_iso, Spc_sim_iso] = garlic(Sys, Exp);

        data = [B_sim_iso', Spc_sim_iso'];
        writematrix(data, 'Simulated-spectrum')


    Read in the simulated spectrum with:

    .. code-block:: yaml

        - source: Simulated-spectrum.txt
          id: simulation
          importer: CsvImporter
          importer_parameters:
              delimiter: ','


    Attributes
    ----------
    parameters : :class:`dict`
        Parameters controlling the import

        skiprows : :class:`int`
            Number of rows to skip in text file (*e.g.*, header lines)

        delimiter : :class:`str`
            The string used to separate values.

            Default: None (meaning: whitespace)

        comments : :class:`str` | :class:`list`
            Characters or list of characters indicating the start of a comment.

            Default: #

        separator : :class:`str`
            Character used as decimal separator.

            Default: None (meaning: dot)


    .. versionchanged:: 0.4.1
        Importer can deal .txt files if explicitely given.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.extension = '.csv'
        self.parameters["skiprows"] = 1
        self.parameters["delimiter"] = None
        self.parameters["comments"] = "#"
        self.parameters["separator"] = None

    def _import(self):
        self._get_extension()
        self._read_data()
        self._create_metadata()


    def _get_extension(self):
        if self.source.endswith('.txt'):
            self.source = self.source[:-4]
            self.extension = '.txt'
        self.source += self.extension
        print(self.source)


    def _read_data(self):
        if "separator" in self.parameters:
            separator = self.parameters.pop("separator")
        else:
            separator = None
        if separator:
            with open(self.source, encoding="utf8") as file:
                contents = file.read()
            contents = contents.replace(separator, '.')
            # noinspection PyTypeChecker
            data = np.loadtxt(io.StringIO(contents), **self.parameters)
        else:
            data = np.loadtxt(self.source, **self.parameters)
        if len(np.shape(data)) > 1 and np.shape(data)[1] == 2:
            self.dataset.data.axes[0].values = data[:, 0]
            data = data[:, 1]
        self.dataset.data.data = data

    def _create_metadata(self):
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[1].quantity = 'intensity'
