"""Dataset (Container for experimental data and respective metadata)"""

import os.path

import aspecd

import cwepr.importers as importers


class Dataset(aspecd.dataset.Dataset):
    """

    """
    def __init__(self):
        super().__init__()

    def import_from_file(self, filename, setformat=None):
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

        self.data = super().import_from(
            importers.ImporterEPRGeneral(source=filename,
                                         setformat=setformat))


#dts = Dataset()
#path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
#dts.import_from_file((path+"/Messdaten/1_No1-dunkel"))

