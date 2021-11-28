"""
Factory classes.

Currently, there is only one factory class:

  * :class:`cwepr.io.factory.DatasetImporterFactory`

    Factory for creating importer objects based on the source provided.

    This class is necessary in context of recipe-driven data analysis and
    allows to automatically import data in all supported formats without
    need to explicitly provide either the file format or an importer.

"""
import os.path

import aspecd.io
from aspecd.utils import object_from_class_name


class DatasetImporterFactory(aspecd.io.DatasetImporterFactory):
    """Factory for creating importer objects based on the source provided.

    Currently, the data formats are distinguished by their file extensions.

    If the source string does not match any of the importers handled by this
    module, the standard importers from the ASpecD framework are checked.
    See the documentation of the :class:`aspecd.io.DatasetImporterFactory`
    base class for details.

    Attributes
    ----------
    supported_formats : :class:`dict`
        Dictionary who's keys correspond to the base name of the respective
        importer (*i.e.*, without the suffix "Importer") and who's values are a
        list of file extensions to detect the correct importer.

    data_format : :class:`str`
        Name of the format that has been detected.

    """

    def __init__(self):
        super().__init__()
        self.supported_formats = {"BES3T": [".DTA", ".DSC"],
                                  "ESPWinEPR": [".spc", ".par"],
                                  "MagnettechXML": [".xml"],
                                  "Txt": [".txt"],
                                  "Csv": [".csv"]}
        self.data_format = None

    def _get_importer(self):
        """Main method returning the importer instance.

        Call the correct importer for the data format set. If no format is set,
        it is automatically determined from the given filename.

        .. note::

            For developers: The actual class name is automatically generated
            from the file format detected and afterwards an object from this
            class created using :func:`aspecd.utils.object_from_class_name`.
            Thus, cyclic imports are prevented.

        Raises
        ------
        UnsupportedDataFormatError
            Raised if a format is set but does not match any of the supported
            formats

        """
        self._cut_file_extension_if_necessary()
        if os.path.isdir(self.source) and self._directory_contains_gon_data():
            self.data_format = 'GoniometerSweep'
            importer = \
                object_from_class_name('cwepr.io.GoniometerSweepImporter')
            importer.source = self.source
            return importer
        self.data_format = self._find_format()
        importer = None
        if self.data_format:
            importer = object_from_class_name(
                ".".join(["cwepr", "io", self.data_format + "Importer"]))
            importer.source = self.source
        return importer

    def _cut_file_extension_if_necessary(self):
        for end_ in [extension for sublist in self.supported_formats.values()
                     for extension in sublist]:
            if self.source.endswith(end_):
                self.source = self.source[:-len(end_)]

    def _find_format(self):
        """Find out the format of the given file.

        Determine the format of the given filename by checking if a data and
        metadata file matching any supported format are present.

        Determination is performed by checking if files with the correct name
        and extension are present.
        """
        detected_format = None
        for file_format, extensions in self.supported_formats.items():
            file_exists = []
            for extension in extensions:
                file_exists.append(os.path.isfile(self.source + extension))
            if all(file_exists):
                detected_format = file_format
        return detected_format

    def _directory_contains_gon_data(self):
        check_gon_filenames = []
        if not os.listdir(self.source):
            return False
        for element in os.listdir(self.source):
            if 'gon' in element:
                check_gon_filenames.append(True)
            else:
                check_gon_filenames.append(False)
        if all(check_gon_filenames):
            return True
        return False
