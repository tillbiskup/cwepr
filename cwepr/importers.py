"""Importers (Preparing raw data for processing)

This importer is used for raw data provided in the Bruker BES3T data format.
"""


import aspecd.io
import numpy as np
import os.path


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
    def __init__(self, source=None):
        super().__init__(source=source)

    def _import(self):
        """"""
        complete_filename = self.source+".DTA"
        return np.fromfile(complete_filename)

