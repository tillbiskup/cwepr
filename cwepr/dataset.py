"""Dataset (Container for experimental data and respective metadata)"""


import aspecd
import cwepr.importers as importers


class UnsupportedDataFormatError(aspecd.dataset.Error):
    """Exception raised when given data format is not supported by an
    available importer.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class Dataset(aspecd.dataset.Dataset):
    """

    """
    supported_formats = {"BES3T": importers.ImporterBES3T}

    def __init__(self):
        super().__init__()

    def import_from_file(self, dataformat):
        """Import data and metadata from a given data format.

        The appropriate importer is selected automatically for
        the respective data format.

         Parameters
         ----------
         dataformat : 'str'
             Data format of the raw EPR data.
             Note: Currently, only Bruker BES3T format is supported!

         Raises
         ------
         UnsupportedDataFormatError
             Raised when given data format is not supported.

         """
        if dataformat not in self.supported_formats.keys():
            raise UnsupportedDataFormatError(message=(
                    "The data format " + dataformat + " is not supported."))
        super().import_from(self.supported_formats[dataformat])

