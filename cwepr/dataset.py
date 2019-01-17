"""Dataset (Container for experimental data and respective metadata)"""


import collections as col
import copy
import numpy as np

import aspecd
import aspecd.metadata

import cwepr.importers as importers
import cwepr.metadata


class Dataset(aspecd.dataset.Dataset):
    """Set of data uniting all relevant information.

    The unity of numerical and metadata is indispensable for the
    reproducibility of data and is possible by saving all information
    available for one set of measurement data in a single instance of
    this class.

    """

    mappings = [
        ["GENERAL", "combine_items", [["Date start", "Time start"],
                                      "Start", " "]],
        ["GENERAL", "combine_items", [["Date end", "Time end"],
                                      "End", " "]],
        ["", "rename_key", ["GENERAL", "measurement"]],
        ["", "rename_key", ["TEMPERATURE", "temperature_control"]]
    ]

    def __init__(self):
        super().__init__()
        self.metadata = cwepr.metadata.DatasetMetadata()

    def import_from_file(self, filename, data_format=None):
        """Import data and metadata for a given filename.

        The appropriate importer automatically checks whether
        data and metadata files exist, matching a single format

         Parameters
         ----------
         filename : 'str'
             Path including the filename but not the extension.

         data_format: 'str'
             Format of the data and metadata. If none is set the
             importer tries to automatically determine the format.
         """

        importer = importers.ImporterEPRGeneral(source=filename,
                                                data_format=data_format)
        super().import_from(importer=importer)
        metadata = self._import_metadata(importer=importer)
        self._map_metadata_and_check_for_overrides(metadata)
        self._modify_field_values()

    def _modify_field_values(self):
        self.metadata.magnetic_field.calculate_values()
        self.metadata.magnetic_field.gauss_to_millitesla()

    def _map_metadata_and_check_for_overrides(self, metadata):
        """Modifies names of metadata information as necessary, combines
        data from the INFO file and the DSC file and checks for possible
        overrides.

        Parameters
        ---------
        metadata: 'list'
            Loaded metadata to use.
        """
        metadata_mapper = aspecd.metadata.MetadataMapper()
        metadata_mapper.metadata = metadata[0]
        metadata_mapper.mappings = self.mappings
        metadata_mapper.map()
        self.metadata.from_dict(metadata_mapper.metadata)
        dsc_data_mapped = self._map_dsc(metadata[1])
        for data_part in dsc_data_mapped:
            self.metadata.from_dict(data_part)
            self._check_for_override(metadata_mapper.metadata, data_part)

    def _check_for_override(self, data1, data2, name=""):
        """Compare the keys in the info file dict with those in
        each part of the dsc file to find overrides.
        Any matching keys are considered to be overriden and
        a respective note is added to
        :attr:'cwepr.metadata.DatasetMetadata.metadata_modifications'.

        The method cascades through nested dicts returning a
        'path' of the potential overrides.
        E.g., when the key 'a' in the sub dict 'b' is found in
        both dicts the path will be '/b/a'.

        Parameters
        ----------
        data1 : 'dict'
            Original data.

        data2: 'dict'
            Data that is added to the original dict.

        name: 'str'
            Used in the cascade to keep track of the path. This should not
            be set to anything other than the default value.

        """
        toplevel = False
        for entry in list(data1.keys()):
            data1[entry.lower()] = data1.pop(entry)
        for entry in data1.keys():
            if type(data1[entry]) == col.OrderedDict:
                toplevel = True
        for entry in data1.keys():
            if entry in data2.keys():
                if toplevel:
                    if name.split("/")[-1] != entry:
                        name = ""
                    name = name + "/" + entry
                    self._check_for_override(data1[entry], data2[entry],
                                             name=name)
                else:
                    self.metadata.metadata_modifications.append(
                        "Possible override @ " + name + "/" + entry + ".")

    def _map_dsc(self, dsc_data):
        """Prepare data from dsc file and include it in the
        metadata.

        Parameters
        ----------
        dsc_data: 'list'
            List containing all three parts of a dsc file as dicts.

        Returns
        ----------
        mapped_data: 'list'
            data with the necessary modifications applied to allow
            for addition to the metadata.

        """
        dsc_mapper = aspecd.metadata.MetadataMapper()
        mapped_data = []
        for n in range(len(dsc_data)):
            dsc_mapper.metadata = dsc_data[n]
            if n == 0:
                mapped_data.append(self._map_descriptor(dsc_mapper))
            if n == 2:
                mapped_data.append(self._map_device(dsc_mapper))
        return mapped_data

    @staticmethod
    def _map_descriptor(mapper):
        """Prepare part one of the dsc file data for adding to the
        metadata.

         Parameters
         ----------
         mapper : :obj:'aspecd.metadata.MetadataMapper'
             metadata mapper containing the respective first part of the
             dsc file as metadata.
        """
        mapper.mappings = [
            ["Data Ranges and Resolutions:", "rename_key",
             ["XPTS", "step_count"]],
            ["Data Ranges and Resolutions:", "rename_key",
             ["XMIN", "field_min"]],
            ["Data Ranges and Resolutions:", "rename_key",
             ["XWID", "field_width"]],
            ["", "rename_key",
             ["Data Ranges and Resolutions:", "magnetic_field"]]
                          ]
        mapper.map()
        return mapper.metadata

    @staticmethod
    def _map_device(mapper):
        """Prepare part three of the dsc file data for adding to the
        metadata.

         Parameters
         ----------
         mapper : :obj:'aspecd.metadata.MetadataMapper'
             metadata mapper containing the respective third part of the
             dsc file as metadata.
        """
        mapper.mappings = [
            ["mwBridge, 1.0", "rename_key", ["PowerAtten", "attenuation"]],
            ["", "rename_key", ["mwBridge, 1.0", "bridge"]],
            ["", "rename_key", ["signalChannel, 1.0", "experiment"]]
                            ]
        mapper.map()
        return mapper.metadata

    @staticmethod
    def _import_metadata(importer=None):
        """Import metadata using a selected importer.

        The appropriate importer automatically checks whether
        data and metadata files exist, matching a single format

        Parameters
        ----------
        importer : 'cwepr.importers.ImporterEPRGeneral'
            Importer instance to use for the import.

        Raises
        ----------
        MissingImporterError :
            Raised, when no importer is provided

        """
        if not importer:
            raise aspecd.dataset.MissingImporterError("No importer provided")
        return importer.import_metadata()

    def fill_axes(self):
        """Add an x axis to the data.

        The y (intensity) values (coming from the actual data file) are used as
        already present. The x (field) values are created from the field data
        in the metadata.

        Both sets are combined and transformed into a numpy array.

        """
        field_points = []
        for n in range(self.metadata.magnetic_field.step_count):
            field_points.append(self.metadata.magnetic_field.field_min.value +
                                self.metadata.magnetic_field.step_width.value
                                * n)
        field_data = np.array(field_points)
        intensity_data = np.array(copy.deepcopy(self.data.data))
        complete_data = np.array([field_data, intensity_data])
        self.data.data = complete_data



