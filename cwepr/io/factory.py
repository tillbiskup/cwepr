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
        Dictionary whose keys correspond to the base name of the respective
        importer (*i.e.*, without the suffix "Importer") and whose values are a
        list of file extensions to detect the correct importer.

    data_format : :class:`str`
        Name of the format that has been given or detected.

    .. versionchanged:: 0.4
        File extension is taken into account, so that two files with the same
        name and different extension can reside next to each other and the
        correct one is taken into account.

    """

    def __init__(self):
        super().__init__()
        self.supported_formats = {"BES3T": [".DTA", ".DSC"],
                                  "ESPWinEPR": [".spc", ".par"],
                                  "MagnettechXML": [".xml"],
                                  "NIEHSDat": [".dat"],
                                  "NIEHSLmb": [".lmb"],
                                  "NIEHSExp": [".exp"],
                                  "Txt": [".txt"],
                                  "Csv": [".csv"],
                                  }
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
        if os.path.isdir(self.source):
            if self._directory_contains_gon_data():
                self.data_format = 'GoniometerSweep'
                importer = \
                    object_from_class_name('cwepr.io.GoniometerSweepImporter')
                importer.source = self.source
                return importer
            if self._directory_contains_amplitude_sweep_data():
                self.data_format = 'AmplitudeSweep'
                importer = \
                    object_from_class_name('cwepr.io.AmplitudeSweepImporter')
                importer.source = self.source
                return importer
            if self._directory_contains_power_sweep_data():
                self.data_format = 'PowerSweep'
                importer = \
                    object_from_class_name('cwepr.io.PowerSweepImporter')
                importer.source = self.source
                return importer
        self.data_format = self._find_format()
        if self.data_format:
            importer = object_from_class_name(
                ".".join(["cwepr", "io", self.data_format + "Importer"]))
            importer.source = self.source
            return importer

    def _find_format(self):
        # detect extension
        detected_format = None
        root, file_extension = os.path.splitext(self.source)
        for file_format, extensions in self.supported_formats.items():
            file_exists = []
            if file_extension in extensions:
                for extension in extensions:
                    file_exists.append(os.path.isfile(root + extension))
                if all(file_exists):
                    detected_format = file_format
            elif not file_extension:
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

    def _directory_contains_amplitude_sweep_data(self):
        check_modamp_filenames = []
        if not os.listdir(self.source):
            return False
        for element in os.listdir(self.source):
            if 'mod' in element:
                check_modamp_filenames.append(True)
            else:
                check_modamp_filenames.append(False)
        if all(check_modamp_filenames):
            return True
        return False

    def _directory_contains_power_sweep_data(self):
        check_powersweep_filenames = []
        if not os.listdir(self.source):
            return False
        for element in os.listdir(self.source):
            if 'pow' in element:
                check_powersweep_filenames.append(True)
            else:
                check_powersweep_filenames.append(False)
        if all(check_powersweep_filenames):
            return True
        return False
