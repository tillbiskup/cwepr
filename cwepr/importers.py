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

class MissingInfoFileError(Error):
    """Exception raised when user created info file is found.

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
        self.special_importer=None

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
        self.special_importer = self.importers_for_formats[
            self.setformat](source=self.source)
        return self.special_importer.import_into(self.dataset)

    def import_metadata(self):
        if not os.path.isfile((self.source + ".info")):
            raise MissingInfoFileError("No infofile provided")
        return self.special_importer.import_metadata()

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
        #print(raw_data)
        if not self._are_values_plausible(raw_data):
            raw_data=raw_data.byteswap()
        #print(raw_data)
        return raw_data

    def import_metadata(self):
        """Import parameter file in BES3T format and
        user created info file.
        """
        file_info = open(self.source+".info")
        raw_info_data = file_info.readlines()
        file_param = open(self.source+".DSC")
        raw_param_data = file_param.readlines()
        return [raw_param_data, raw_info_data]

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


class ParserDSC:
    def __init__(self):
        pass

    def parse_dsc(self, file_content):
        pass

    @staticmethod
    def _get_three_parts(file_content):
        three_parts = []
        first_split = file_content.split("#SPL")
        three_parts.append(first_split[0])
        second_split = first_split[1].split("#DSL")
        three_parts.extend(second_split)
        return three_parts

    @staticmethod
    def _subdivide_part1(desc_part):
        subparts_descriptor = desc_part.split("\n*\n")
        del(subparts_descriptor[0])
        subparts_clean = {}
        for part in subparts_descriptor:
            part_split = part.slit("\n")
            part_split_clean = []
            for line in part_split:
                if line != "*":
                    part_split_clean.append(line)
            subparts_clean[part_split_clean[0][2:]] = part_split_clean[1:]
        return subparts_clean

    @staticmethod
    def _create_dict_part1(desc_part_split):
        dict_final = {}
        for title, subpart in desc_part_split.items():
            subdict = {}
            for line in subpart:
                line_split = line.split("\t")
                if len(line_split) == 1:
                    subdict[line_split[0]] = ""
                else:
                    subdict[line_split[0]] = line_split[1]
            dict_final[title] = subdict
        return dict_final





