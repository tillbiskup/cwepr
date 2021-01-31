"""
Factory classes.

Currently, there is only one factory class:

  * :class:`cwepr.io.factory.DatasetImporterFactory`

    Class necessary in context of recipe-driven data analysis

"""


import os.path

import aspecd.io

from cwepr.io.bes3t import BES3TImporter
from cwepr.io.magnettech import MagnettechXmlImporter, GoniometerSweepImporter
from cwepr.io.txt_file import TxtImporter
from cwepr.io.errors import NoMatchingFilePairError


class DatasetImporterFactory(aspecd.io.DatasetImporterFactory):
    """Factory for creating importer objects based on the source provided.

    Currently, the data formats are distinguished by their file extensions.

    """

    def __init__(self):
        super().__init__()
        self.supported_formats = {"BES3T": [".DTA", ".DSC"],
                                  "Magnettech": [".xml"],
                                  "Txt": [".txt"]}
        self.importers_for_formats = {"BES3T": BES3TImporter,
                                      "Magnettech": MagnettechXmlImporter,
                                      "Txt": TxtImporter}
        self.data_format = None

    def _get_importer(self, source):
        """Main method returning the importer instance.

        Call the correct importer for the data format set. If no format is set,
        it is automatically determined from the given filename.

        Raises
        ------
        UnsupportedDataFormatError
            Raised if a format is set but does not match any of the supported
            formats

        """
        if os.path.isdir(source):
            return GoniometerSweepImporter(source=source)
        self.data_format = self._find_format(source)
        special_importer = self.importers_for_formats[
            self.data_format](source=source)
        return special_importer

    def _find_format(self, source):
        """Find out the format of the given file.

        Determine the format of the given filename by checking if a data and
        metadata file matching any supported format are present.

        Determination is performed by checking if files with the correct name
        and extension are present.

        Raises
        ------
        NoMatchingFilePairError
            Raised if no source format doesn't match a supported format

        """
        for file_format, extensions in self.supported_formats.items():
            file_exists = []
            for extension in extensions:
                file_exists.append(os.path.isfile(source + extension))
            if all(file_exists):
                return file_format
        msg = ["No file format was found for path: " + source]
        raise NoMatchingFilePairError(message=msg)
