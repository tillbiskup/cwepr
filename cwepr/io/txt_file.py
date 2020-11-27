"""Functionalities to simply import a txt file containing data."""
import numpy as np

import aspecd.io
import cwepr.dataset
import cwepr.processing
import cwepr.io.errors


class TxtImporter(aspecd.io.DatasetImporter):
    """Simple importer for txt files containing data.

    Sometimes, data come from sources as a txt file only. So far, the format
    is hardcoded and should contain two columns separated by a tabulator.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def _import(self):
        self._get_data()
        self._create_metadata()

    def _get_data(self):
        self.source = self.source + '.txt'
        raw_data = np.loadtxt(self.source, delimiter='\t')
        self.dataset.data.data = raw_data[:, 1]
        self.dataset.data.axes[0].values = raw_data[:, 0]

    def _create_metadata(self):
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'
