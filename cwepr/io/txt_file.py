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
import numpy as np

import aspecd.io


class TxtImporter(aspecd.io.DatasetImporter):
    """Simple importer for txt files containing data.

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
        self.source = self.source + self.extension
        raw_data = np.loadtxt(self.source, delimiter='\t')
        self.dataset.data.data = raw_data[:, 1]
        self.dataset.data.axes[0].values = raw_data[:, 0]

    def _create_metadata(self):
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'


class CsvImporter(aspecd.io.DatasetImporter):
    """Importer for simple csv imports with different delimiters."""

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.extension = '.csv'

    def _import(self):
        self._read_data()

    def _read_data(self):
        with open(self.source + self.extension) as csv_file:
            # noinspection PyTypeChecker
            raw_data = np.loadtxt(csv_file, delimiter=';', skiprows=3)
            self.dataset.data.data = raw_data[:, 1]
            self.dataset.data.axes[0].values = raw_data[:, 0]

    def _create_metadata(self):
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'
