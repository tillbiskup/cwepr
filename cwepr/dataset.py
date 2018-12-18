"""Dataset (Container for experimental data and respective metadata)"""


import aspecd
import aspecd.metadata
from aspecd.metadata import MetadataMapper

import cwepr.importers as importers
import cwepr.metadata


class Dataset(aspecd.dataset.Dataset):
    """Set of data uniting all relevant information.

    The unity of numerical and metadata is indispensable for the
    reproducibility of data and is possible by saving all information
    available for one set of measurement data in a single instance of
    this class.

    """
    def __init__(self):
        super().__init__()
        self.metadata_modifications = list()
        self.metadata = cwepr.metadata.DatasetMetadata()

    def import_from_file(self, filename, set_format=None):
        """Import data and metadata for a given filename.

        The appropriate importer automatically checks whether
        data and metadata files exist, matching a single format

        After loading the info file and parameter file the data
        from the info file is automatically added to the metadata.

        Some keys have to be renamed to match the nomenclature used.

         Parameters
         ----------
         filename : 'str'
             Path including the filename but not the extension.

         set_format: 'str'
             Format of the data and metadata. If none is set the
             importer tries to automatically determine the format.
         """

        importer = importers.ImporterEPRGeneral(source=filename,
                                                set_format=set_format)
        self.data = super().import_from(importer=importer)
        metadata = self._import_metadata(importer=importer)
        metadata_mapper = aspecd.metadata.MetadataMapper()
        metadata_mapper.metadata = metadata[0]
        metadata_mapper.mappings = [
            ["GENERAL", "combine_items", [["Date start", "Time start"],
                                          "Start", " "]],
            ["GENERAL", "combine_items", [["Date end", "Time end"],
                                          "End", " "]],
            ["", "rename_key", ["GENERAL", "measurement"]],
            ["", "rename_key", ["TEMPERATURE", "temperature_control"]],
                                    ]
        metadata_mapper.map()
        self.metadata.from_dict(metadata_mapper.metadata)
        dsc_data_mapped = self.map_dsc(metadata[1])
        for data_part in dsc_data_mapped:
            self.metadata.from_dict(data_part)
        self.metadata.magnetic_field.calculate_values()
        self.metadata.magnetic_field.gauss_to_millitesla()

    def map_dsc(self, dsc_data):
        dsc_mapper = aspecd.metadata.MetadataMapper()
        mapped_data = []
        for n in range(len(dsc_data)):
            dsc_mapper.metadata = dsc_data[n]
            if n == 0:
                mapped_data.append(self.map_descriptor(dsc_mapper))
            if n == 1:
                mapped_data.append(self.map_standard(dsc_mapper))
            if n == 2:
                mapped_data.append(self.map_device(dsc_mapper))
        return mapped_data

    @staticmethod
    def map_descriptor(mapper):
        mapper.mappings = [
            ["Data Ranges and Resolutions:", "rename_key", ["XPTS", "step_count"]],
            ["Data Ranges and Resolutions:", "rename_key", ["XMIN", "field_min"]],
            ["Data Ranges and Resolutions:", "rename_key", ["XWID", "field_width"]],
            ["", "rename_key", ["Data Ranges and Resolutions:", "magnetic_field"]]
                            ]
        mapper.map()
        return mapper.metadata

    @staticmethod
    def map_standard(mapper):
        return mapper.metadata

    @staticmethod
    def map_device(mapper):
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
        importer : ????
        ????

        Raises
        ----------
        MissingImporterError :
            Raised, when no importer is provided

        """
        if not importer:
            raise aspecd.dataset.MissingImporterError("No importer provided")
        return importer.import_metadata()

