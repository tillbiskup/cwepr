"""Importers (Preparing raw data for processing)

Currently, the only specialized importer works for the Bruker BES3T format.
"""


import os.path
import numpy as np
import collections as col


import aspecd.io
import aspecd.infofile
import aspecd.metadata
import aspecd.utils

from cwepr.utils import are_values_plausible


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
    """Exception raised when no user created info file is found.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ImportMetadataOnlyError(Error):
    """Exception raised when import of metadata is attempted
    without importing experimental data first and no importer
    has been initialized.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ExperimentTypeError(Error):
    """Exception raised when the data provided does not correspond
    to a continuous wave experiment or the experiment type cannot be
    determined.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ImporterEPRGeneral(aspecd.io.DatasetImporter):
    """Importer super class that determines the correct
    specialized importer for a format.

     Attributes
    ----------
    data_format
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

    def __init__(self, data_format=None, source=None):
        super().__init__(source=source)
        self.data_format = data_format
        self.importers_for_formats = {"BES3T": ImporterBES3T}
        self.special_importer = None

    def _import(self):
        """Call the correct importer for the data format set.
        If no format is set, it is automatically determined
        from the given filename.

        Raises
        ------
        UnsupportedDataFormatError
            Raised if a format is set but does not match any of
            the supported formats
            """
        if self.data_format is None:
            self.data_format = self._find_format()
        else:
            if self.data_format not in self.importers_for_formats.keys():
                raise UnsupportedDataFormatError(("""The following format 
                is not supported: """+self.data_format))
        self.special_importer = self.importers_for_formats[
            self.data_format](source=self.source)
        self.special_importer.import_into(self.dataset)

    def import_metadata(self):
        """Import metadata from user made info file and device
        parameter file.

        Raises
        ------
        MissingInfoFileError
            Raised if no user made info file is provided.
        ImportMetadataOnlyError
            Raised when no format specific importer is initialized.
            This should happen and only happen, when the method is
            called without first importing the experimental data,
            because :meth:'_import' creates an instance of a
            format specific importer.

        """
        if not os.path.isfile((self.source + ".info")):
            raise MissingInfoFileError("No info file provided")
        if not self.special_importer:
            raise ImportMetadataOnlyError(("""No format specific importer"
                was available as metadata import was attempted. This 
                probably happened due to not importing experimental data
                first."""))
        info_data = self._import_infofile((self.source + ".info"))
        param_data = self.special_importer.import_metadata()
        return [info_data, param_data]

    def _find_format(self):
        """Determine the format of the given filename by checking
        if a data and metadata file matching any supported
        format are present.

        Determination is performed by checking if files with the correct name
        and extension are present.

        Raises
        ------
        NoMatchingFilePairError
            Raised if no pair of files matching any one supported
            format can be found. Currently only Bruker BES3T format
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

    @staticmethod
    def _import_infofile(filename):
        """Import and parse user made info file using the method
        provided by ASpecD.

        Returns
        ------
        infofile_data: 'dict'
        Parsed data from the info file.
        """
        infofile_data = aspecd.infofile.parse(filename)
        return infofile_data


class ImporterBES3T(aspecd.io.DatasetImporter):
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
        if not are_values_plausible(raw_data):
            raw_data = raw_data.byteswap()
        self.dataset.data.data = raw_data

    def import_metadata(self):
        """Import parameter file in BES3T format and
        user created info file.

        Returns
        ------
        processed_param_data: 'dict'
        Parsed data from the source parameter file.
        """

        file_param = open(self.source+".DSC")
        raw_param_data = file_param.read()
        dsc_file_parser = ParserDSC()
        parsed_param_data = dsc_file_parser.parse_dsc(raw_param_data)
        return parsed_param_data


class ParserDSC:
    """Parser for a *.DSC parameter file belonging to the BES3T
    format."""

    def parse_dsc(self, file_content):
        """Main method for parsing a *.DSC file into its
        three parts and each of the three parts into a dictionary

        Parameters
        ------
        file_content: 'str'
        Content of a complete *.DSC file.

        Returns
        ------
        three_parts_processed: 'list'
        The three parts of the file, each represented by a dictionary
        containing pairs of keys (parameter names) and values
        (parameter values) The dictionaries of part one and three are
        additionally subdivided based on headlines.
        """
        three_parts = self._get_three_parts(file_content)
        three_parts_processed = list()
        three_parts_processed.append(self._create_dict_p1p3(
            self._subdivide_part1(three_parts[0]), "\t"
        ))
        three_parts_processed.append(self._create_dict_part2(
            self._subdivide_part2(three_parts[1])
        ))
        three_parts_processed.append(self._create_dict_p1p3(
            self._subdivide_part3(three_parts[2]), " ",
            delimiter_width=19
        ))
        three_parts_processed = self.add_units(three_parts_processed)
        return three_parts_processed

    @staticmethod
    def add_units(parsed_dsc_data):
        """Adds the units to the data values concerning the field.

        Parameters
         ---------
         parsed_dsc_data: 'dict'
         Original data.


        Returns
        -------
        Data with units added.
        """
        parsed_dsc_data[0]["Data Ranges and Resolutions:"]["XMIN"] += " Gs"
        parsed_dsc_data[0]["Data Ranges and Resolutions:"]["XWID"] += " Gs"
        return parsed_dsc_data

    @staticmethod
    def _make_dict_without_structure(processed_file):
        """Make a dictionary containing all information
        at the same level, not divided by headlines and sub-headlines
        for easier mapping

        .. Todo:: Find out, if this method is actually used.

        Parameters
        ------
        processed_file: 'list'
        Content of a complete *.DSC file in processed form, i.e. with
        headlines and sub-headlines.

        Returns
        ------
        dict_without_headlines: 'dict'
        Dictionary of all key-value pairs belonging to any
        headline or sub-headline, all on the same level. 
        """
        dict_without_structure = col.OrderedDict()
        for content in processed_file[0].values():
            for title, entry in content.items():
                dict_without_structure[title] = entry
        for title, entry in processed_file[1]:
            dict_without_structure[title] = entry
        for content in processed_file[2].values():
            for title, entry in content.items():
                dict_without_structure[title] = entry
        return dict_without_structure

    @staticmethod
    def _get_three_parts(file_content):
        """Split a *.DSC file into three parts (Descriptor
        Information, Standard Parameter Layer and Device
        Specific Layer).

        The file is split at the second and third headline which
        start with convenient markers.

        Parameters
        ------
        file_content: 'str'
        Content of a complete *.DSC file.

        Returns
        ------
        three_parts: 'list'
        The three parts of the file.
        """
        three_parts = list()
        first_split = file_content.split("#SPL")
        three_parts.append(first_split[0])
        second_split = first_split[1].split("#DSL")
        three_parts.extend(second_split)
        return three_parts

    @staticmethod
    def _subdivide_part1(part1):
        """Pre process the first part ("Descriptor Information")
         of a *.DSC file.

        The crude string is split into subdivisions; the delimiter
        employed allows to detect the different headlines made up
        of three lines starting with asterisks, the center line
        containing additional text.

        Each subdivision is then transformed into a dict entry
        with the headline, stripped of the first two characters
        (*\t) as key and the remaining information as value.
        Lines containing an asterisk only are removed.

        Parameters
        ------
        part1: 'str'
        Raw first part of a file.

        Returns
        ------
        part1_clean: 'dict'
        All subdivisions from the file with headlines as keys
        and list of lines as values; lines devoid of information
        removed.
        """
        lines = part1.split("\n")
        part1_clean = col.OrderedDict()
        current_subpart = list()
        for line in lines:
            if "*" in line and "*\t" not in line:
                continue
            if "*\t" in line and current_subpart != list():
                part1_clean[current_subpart[0][2:]] = current_subpart[1:]
                current_subpart = list()
            current_subpart.append(line)
        part1_clean[current_subpart[0][2:]] = current_subpart[1:]
        return part1_clean

    @staticmethod
    def _create_dict_p1p3(p1p3_split, delimiter, delimiter_width=0):
        """Create a dict from the first part ("Descriptor Information")
        or third part ("Device Specific Layer") of a *.DSC file.

        For every subdivision. lines are split at tabs. The method
        accounts for lines containing only a parameter name with no
        corresponding value.

        Note: The format of part 3 of a *.DSC file does not work with tabs,
        but rather with with a variable number of spaces.

        Parameters
        ------
        p1p3_split: 'dict'
        Preprocessed first or third part of a file, split into
        subdivisions with the headline as key. Subdivisions split into
        lines with lines devoid of information removed.

        delimiter: 'str'
        Delimiter separating parameter name and value in one line.

        delimiter_width: 'int'
        Used to split at a variable number of spaces (could be used
        for other delimiters, too, though). The method will count
        all characters before the first delimiter character and determine
        the number of delimiter characters from the difference to the value
        of delimiter width. If set to zero a single character
        delimiter will be applied.

        Returns
        ------
        p1p3_dict: 'dict'
        Data from the input as pairs of key (subdivision name) and
        value (subdivision info). Each subdivision info is also a dict
        with keys (parameter names) and values (parameter values).
        """
        p1p3_dict = col.OrderedDict()
        for title, subpart in p1p3_split.items():
            param_dict = col.OrderedDict()
            for line in subpart:
                if delimiter_width != 0:
                    param_count = 0
                    for character in line:
                        if character != delimiter:
                            param_count += 1
                        else:
                            break
                    final_delimiter = (delimiter_width-param_count)*delimiter
                else:
                    final_delimiter = delimiter
                line_split = line.split(final_delimiter)
                if line_split[0] != "":
                    if len(line_split) == 1:
                        param_dict[line_split[0]] = ""
                    else:
                        param_dict[(line_split[0].strip())] = line_split[1]
            p1p3_dict[title] = param_dict
        return p1p3_dict

    @staticmethod
    def _subdivide_part2(part2):
        """Pre process the second part ("Standard parameter
        layer") of a *.DSC file.

        The crude string is split into lines; lines devoid of
        information (e.g. containing only an asterisk) are
        removed.

        Note: every line containing asterisks is removed as
        these appear only in headlines and as delimiters.

        Note: For reasons that will probably never be known,
        in this part, parameter names are separated from the
        values by four spaces instead of a tab.

        Parameters
        ------
        part2: 'str'
        Raw second part of a file.

        Returns
        ------
        entries_clean: 'list'
        All lines from the file part except those devoid of
        information.
        """
        entries_param = part2.split("\n")
        entries_clean = list()
        for line in entries_param:
            if "*" not in line:
                entries_clean.append(line)
        return entries_clean

    @staticmethod
    def _create_dict_part2(part2_split):
        """Create a dict from the second part ("Standard parameter
        layer") of a *.DSC file.

        Lines are split at tabs. The method accounts for lines
        containing only a parameter name with no corresponding
        value.

        Parameters
        ------
        part2_split: 'list'
        Preprocessed second part of a file, split into lines,
        with lines devoid of information already removed.

        Raises
        ------
        ExperimentTypeError:
            raised when the type of the experiment file cannot
            be determined from the parameter file or if it is
            not CW.

        Returns
        ------
        part2_dict: 'dict'
        Data from the input as pairs of key (parameter name) and
        value (parameter value).
        """
        part2_dict = col.OrderedDict()
        for line in part2_split:
            line_split = line.split("    ")
            if line_split[0] != "":
                if len(line_split) == 1:
                    part2_dict[line_split[0]] = ""
                else:
                    part2_dict[line_split[0]] = line_split[1]
        if "EXPT" not in part2_dict.keys():
            raise ExperimentTypeError("Could not determine experiment type")
        elif part2_dict["EXPT"] != "CW":
            raise ExperimentTypeError("""Experiment type is not CW according
                                      "to parameter file""")
        return part2_dict

    @staticmethod
    def _subdivide_part3(part3):
        """Pre process the third part ("Device Specific Layer")
         of a *.DSC file.

        The crude string is split into subdivisions, which start
        with a headline containing the fragment ".DVC"

        Each subdivision is then transformed into a dict entry
        with the headline, stripped of the first eight characters
        (".DVC    ") as key and the remaining information as value.
        Lines containing asterisks are removed.

        Parameters
        ------
        part3: 'str'
        Raw third part of a file.

        Returns
        ------
        subparts_clean: 'dict'
        All subdivisions from the file with headlines as keys
        and list of lines as values; lines devoid of information
        removed.
        """
        lines = part3.split("\n")
        subdivisions = col.OrderedDict()
        current_subpart = list()
        for line in lines:
            if "*" in line:
                continue
            if ".DVC" in line and current_subpart != []:
                if len(current_subpart) == 1:
                    subdivisions[current_subpart[0][9:]] = []
                else:
                    subdivisions[current_subpart[0][9:]] = current_subpart[1:]
                current_subpart.clear()
            current_subpart.append(line)
        if len(current_subpart) == 1:
            subdivisions[current_subpart[0][9:]] = []
        elif len(current_subpart) != 0:
            subdivisions[current_subpart[0][9:]] = current_subpart[1:]
        return subdivisions


class ImporterEMXandESP(aspecd.io.DatasetImporter):
    def __init__(self):
        super().__init__()


class ImporterFactoryEPR(aspecd.io.DatasetImporterFactory):
    def __init__(self):
        super().__init__()


class ExporterASCII(aspecd.io.DatasetExporter):
    """Exports the complete dataset to an ASCII file. At the same time,
    the respective metadata is exported into a YAML file using the
    functionality provided by aspecd.
    """
    def __init__(self):
        super().__init__()

    def _export(self):
        """Export the dataset's numeric data and metadata."""
        np.savetxt("Dataset", self.dataset.data.data, delimiter=",")
        file_writer = aspecd.utils.Yaml()
        metadata = self._get_and_prepare_metadata()
        file_writer.dict = metadata
        file_writer.write_to(filename="dataset_metadata")

    def _get_and_prepare_metadata(self):
        """Transforms the metadata to a dict and subsequently eliminates
        all instances of numpy.array by transforming them into lists
        (vide infra).

        Returns
        -------
        metadata_prepared: 'dict'
        transformed metadata
        """
        metadata = self.dataset.metadata.to_dict()
        metadata_prepared = self._remove_arrays(metadata)
        return metadata_prepared

    def _remove_arrays(self, dictionary):
        """Removes instances of numpy.array from a given dict that might
        interfere with the YAML functionality used for the export.

        This is a cascading method that also works on nested dicts.

        Parameters
        ----------
        dictionary: 'dict'
        Dictionary to relieve of arrays.

        Returns
        -------
        dictionary: 'dict'
        Dictionary relieved of arrays.
        """
        for k, v in dictionary.items():
            if type(v) == dict:
                dictionary[k] = self._remove_arrays(v)
            if type(v) == np.array:
                dictionary[k].to_list()
        return dictionary
