"""Dataset (Container for experimental data and respective metadata)"""


import aspecd


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

    def import_from_file(self, filename, set_format=None):
        """Import data and metadata for a given filename.

        The appropriate importer automatically checks whether
        data and metadata files exist, matching a single format

         Parameters
         ----------
         filename : 'str'
             Path including the filename but not the extension.

         setformat: 'str'
             Format of the data and metadata. If none is set the
             importer tries to automatically determine the format.
         """

        importer = importers.ImporterEPRGeneral(source=filename,
                                                set_format=set_format)
        self.data = super().import_from(importer=importer)
        self.metadata = self._import_metadata(importer=importer)

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
        return importer.import_metadata
