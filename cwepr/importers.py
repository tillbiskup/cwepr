"""Importers (Preparing raw data for processing)

This importer is used for raw data provided in the Bruker BES3T data format.
"""


import os.path
import numpy as np


import aspecd.io


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class UnsupportedDataFormatError(Error):
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


class NoMatchingFilePairError(Error):
    """Exception raised when no pair of a data and parameter files
    is found where the extensions match a single format.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ImporterEPRGeneral(aspecd.io.Importer):
    """Importer super class that determines the correct
    specialized importer for a format.

     Attributes
    ----------
    setformat
        The format of the data to import. Is set manually or
        determined automatically.
    importers_for_formats
        Map of the specialized importers for different formats.

    Raises
    ------
    UnsupportedDataFormatError
        Raised if a format is set but does not match any of the
        supported formats
    NoMatchingFilePairError
        Raised if no pair of files matching any one supported format
        can be found. Currently only Bruker BES3T is supported.

    """
    supported_formats = {"BES3T": [".DTA", ".DSC"]}

    def __init__(self, setformat=None, source=None):
        super().__init__(source=source)
        self.setformat=setformat
        self.importers_for_formats = {"BES3T": ImporterBES3T}

    def _import(self):
        """Call the correct importer for the data format set.
        If no format is set it is automatically determined
        from the given filename.

        Raises
        ------
        UnsupportedDataFormatError
            Raised if a format is set but does not match any of
            the supported formats
            """
        if self.setformat is None:
            self.setformat = self._find_format()
        else:
            if self.setformat not in self.importers_for_formats.keys():
                raise UnsupportedDataFormatError(("""The following format 
                is not supported: """+self.setformat))
        special_importer = self.importers_for_formats[
            self.setformat](source=self.source)
        return special_importer.import_into(self.dataset)

    def _find_format(self):
        """Determine the format of the given filename by checking
        if a data and metadata file matching any supported
        format are present.

        Raises
        ------
        NoMatchingFilePairError
            Raised if no pair of files matching any one supported
            format can be found. Currently only Bruker BES3T
            is supported.

        """
        for k, v in self.supported_formats.items():
            if os.path.isfile((self.source+v[0])) and os.path.isfile(
                (self.source+v[1])
            ):
                return k
        else:
            raise NoMatchingFilePairError("""No file pair matching a single
            format was found for path: """+self.source)


class ImporterBES3T(aspecd.io.Importer):
    """Specialized Importer for the BES3T format."""

    def __init__(self, source=None):
        super().__init__(source=source)

    def _import(self):
        """Import data file in BES3T format.

        The data is checked for plausibility; if values are
        too large or too small the byte order is changed.

        Returns
        ------
        raw_data: 'numpy.array'
        Raw numerical data in processable form.
        """
        complete_filename = self.source+".DTA"
        raw_data = np.fromfile(complete_filename)
        print(raw_data)
        if not self._are_values_plausible(raw_data):
            raw_data=raw_data.byteswap()
        print(raw_data)
        return raw_data

    @staticmethod
    def _are_values_plausible(array):
        """Check whether the values imported are plausible, i.e.
        not extremely high or low.

        Note: In case of a wrong byteorder the values observed can
        reach 10**300 and higher. The threshold of what is considered
        plausible is, so far, rather arbitrary.

        Parameters
        ------
        array: 'numpy.array'
        Array to check the values of.
        """
        for v in array:
            if v > 10**4 or v < 10**-10:
                return False
        return True
