"""ExperimentalDataset (Container for experimental data and respective metadata)"""


import aspecd.metadata

import cwepr.io
import cwepr.metadata


class ExperimentalDataset(aspecd.dataset.ExperimentalDataset):
    """Set of data uniting all relevant information.

    The unity of numerical and metadata is indispensable for the
    reproducibility of data and is possible by saving all information available
    for one set of measurement data in a single instance of this class.
    """

    def __init__(self):
        super().__init__()
        self.metadata = cwepr.metadata.DatasetMetadata()


class DatasetFactory(aspecd.dataset.DatasetFactory):
    """Implementation of the dataset factory for recipe driven evaluation"""

    def __init__(self):
        super().__init__()
        self.importer_factory = cwepr.io.ImporterFactory()

    @staticmethod
    def _create_dataset(source=''):
        """Return cwepr dataset.

        Parameters
        ----------
        source : :class:`str`
            string describing the source of the dataset

            May be a filename or path, a URL/URI, a LOI, or similar

        Returns
        -------
        dataset : :class:`cwepr.dataset.ExperimentalDataset`
            Dataset object for cwepr package

        """
        return cwepr.dataset.ExperimentalDataset()
