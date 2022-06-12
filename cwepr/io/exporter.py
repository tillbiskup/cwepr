"""Exporters for both, whole datasets as well as data alone.


Exporters
=========

There are two different general types of exporters provided: Exporters for
whole datasets i.e. data with their according metadata and exporters for data
only.

    .. warning::
        All metadata contained within a dataset (including the full history)
        are lost when exporting to plain text. Therefore, using this
        exporter will usually result in you loosing reproducibility. Hence,
        better think twice before using this exporter and use entirely on
        your own risk and only if you *really* know what you are doing (and
        why).

For further details and a comprehensive summary of data export, the reader is referred to the aspecd-documentation (:mod:`aspecd.io`).

If you want to export data to a txt-file, you might want to use the
:class:`aspecd.io.TxtExporter`.

"""
import collections
import datetime

import numpy as np
import aspecd.io
import aspecd.utils


class ASCIIExporter(aspecd.io.DatasetExporter):
    """Export a dataset in ASCII format.

    Exports the complete dataset to an ASCII file. At the same time, the
    respective metadata is exported into a YAML file using the functionality
    provided by aspecd. Metadata residing there as an object of the class
    :class:`numpy.ndarray` are converted into lists.

    A simple example for its usage looks like this:

    .. code-block:: yaml

    datasets:
      - /path/to/first/dataset
      - /path/to/second/dataset

    tasks:
      - kind: export
        type: ASCIIExporter
        properties:
          target:
            - dataset1
            - dataset2


    .. note::
        Not tested.
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


class MetadataExporter(aspecd.io.DatasetExporter):
    """Export metadata to yaml file with default name."""

    def __init__(self):
        super().__init__()
        self.metadata_dict = collections.OrderedDict()
        self.filename = ''

    def _export(self):
        if not self.filename:
            timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
            self.filename = 'metadata-' + timestamp + '.yaml'
        if not self.filename.endswith(('.yaml', '.yml')):
            self.filename = self.filename + '.yaml'
        self._write_metadata()

    def _write_metadata(self):
        self.metadata_dict = self.dataset.metadata.to_dict()
        self.metadata_dict = \
            self._remove_empty_items_recursively(dict_=self.metadata_dict)
        yaml_file = aspecd.utils.Yaml()
        yaml_file.dict = self.metadata_dict
        yaml_file.write_to(self.filename)

    def _remove_empty_items_recursively(self, dict_=None):
        tmp_dict = collections.OrderedDict()
        for key, value in dict_.items():
            if isinstance(value, dict):
                dict_[key] = \
                    self._remove_empty_items_recursively(value)
            # if magnettech has not measured the q-value it is -1
            if key == 'q_value' and value == -1:
                continue
            if dict_[key]:
                tmp_dict[key] = dict_[key]
        return tmp_dict
