"""Dataset (Container for experimental data and respective metadata)"""


import aspecd
import aspecd.metadata


import cwepr.importers as importers


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
        metadata_mapper.mappings = [["GENERAL", "rename_key",
                                     ["Date start", "date_start"]],
                                    ["GENERAL", "rename_key",
                                     ["Date end", "date_end"]],
                                    ["GENERAL", "rename_key",
                                     ["Time start", "time_start"]],
                                    ["GENERAL", "rename_key",
                                     ["Time end", "date_end"]],
                                    ["", "rename_key",
                                     ["GENERAL", "measurement"]],
                                    ["", "rename_key",
                                     ["TEMPERATURE", "temperature_control"]],
                                    ]
        metadata_mapper.map()
        self.metadata.from_dict(metadata_mapper.metadata)
        print(self.metadata.to_dict())

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

