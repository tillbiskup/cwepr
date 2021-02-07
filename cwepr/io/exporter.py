"""Exporters for datasets.

.. note::
    not tested.

"""

import numpy as np
import aspecd.io
import aspecd.utils


class ASCIIExporter(aspecd.io.DatasetExporter):
    """Export a dataset in ASCII format.

    Exports the complete dataset to an ASCII file. At the same time, the
    respective metadata is exported into a YAML file using the functionality
    provided by aspecd. Metadata residing there as an object of the class
    :class:`numpy.ndarray` are converted into lists.
    """

    def __init__(self):
        super().__init__()

    def _export(self):
        """Export the dataset's numeric data and metadata."""
        file_name_data = self.target + ".txt"
        file_name_meta = self.target + ".yaml"
        np.savetxt(file_name_data, self.dataset.data.data, delimiter=",")
        metadata_writer = aspecd.utils.Yaml()
        metadata = self._get_and_prepare_metadata()
        metadata_writer.dict = metadata
        metadata_writer.write_to(filename=file_name_meta)

    def _get_and_prepare_metadata(self):
        """Prepare the dataset's metadata to be imported.

        Transforms the metadata to a dict and subsequently transforms all
        instances of :class:`numpy.ndarray` by transforming them into lists.

        Returns
        -------
        metadata_prepared: :class:`dict`
            transformed metadata

        """
        metadata = self.dataset.metadata.to_dict()
        metadata_prepared = self._ndarrays_to_list_recursively(metadata)
        return metadata_prepared

    def _ndarrays_to_list_recursively(self, dictionary):
        """Transforms instances of :class:`numpy.array` from a given dict.

        Numpy arrays are not easily convertible into a yaml-file and are
        therefore transformed to lists.
        This is a cascaded method and thus also works on nested dicts.

        Parameters
        ----------
        dictionary: :class:`dict`
            Dictionary to relieve of arrays.

        Returns
        -------
        dictionary: :class:`dict`
            Dictionary relieved of arrays.

        """
        for key, value in dictionary.items():
            if isinstance(value, dict):
                dictionary[key] = self._ndarrays_to_list_recursively(value)
            if isinstance(value, np.ndarray):
                dictionary[key].to_list()
        return dictionary