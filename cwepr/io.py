"""Importers (Preparing raw data for processing)"""

import os.path
import collections
import re

import numpy as np
import aspecd.io
import aspecd.infofile
import aspecd.metadata
import aspecd.utils
import aspecd.dataset


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class UnsupportedDataFormatError(Error):
    """Exception raised when given data format is not supported.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class NoMatchingFilePairError(Error):
    """Exception raised when no pair of data and parameter file is found.

    Data and parameter files' extensions must match a single format.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class MissingInfoFileError(Error):
    """Exception raised when no user created info file is found.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ImportMetadataOnlyError(Error):
    """Exception raised when no importer has been initialized.

    This happens when import of metadata is attempted without importing
    experimental data first.

    Attributes
    ----------
    message : :class:`str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ExperimentTypeError(Error):
    """Exception raised in case of problems with designated experiment type.

    This inlcudes to cases: 1) when the data provided does not correspond to a
    continuous wave experiment or 2) the experiment type cannot be determined.

    Attributes
    ----------
    message : `str`
        explanation of the error

    """

    def __init__(self, message=''):
        super().__init__()
        self.message = message


class GeneralImporter(aspecd.io.DatasetImporter):
    """Importer super class

    Determine the correct specialized importer for a format.

    Attributes
    ----------
    data_format
        The format of the data to import. Is set manually or determined
        automatically.
    importers_for_formats
        Map of the specialized importers for different formats.

    Raises
    ------
    UnsupportedDataFormatError
        Raised if a format is set but does not match any of the supported
        formats
    NoMatchingFilePairError
        Raised if no pair of files matching any one supported format can be
        found. Currently Bruker BES3T, EMX and ESP/ECS formats are supported.

    """

    MAPPINGS = [
        ["GENERAL", "combine_items", [["Date start", "Time start"],
                                      "Start", " "]],
        ["GENERAL", "combine_items", [["Date end", "Time end"],
                                      "End", " "]],
        ["", "rename_key", ["GENERAL", "measurement"]],
        ["", "rename_key", ["TEMPERATURE", "temperature_control"]]
    ]
    supported_formats = {"BES3T": [".DTA", ".DSC"], "Other": [".spc", ".par"]}

    def __init__(self, data_format=None, source=None):
        super().__init__(source=source)
        self.data_format = data_format
        self.importers_for_formats = {"BES3T": BES3TImporter,
                                      "Other": EMXandESPImporter}

    @staticmethod
    def import_from_file(filename):
        """Import data and metadata for a given filename.

        The appropriate importer automatically checks whether data and metadata
        files exist, matching a single format

        Parameters
        ----------
        filename : :class:`str`
            Path including the filename but not the extension.

        """
        importer_factory = ImporterFactory()
        importer = importer_factory.get_importer(source=filename)
        dataset = aspecd.dataset.Dataset()
        dataset.import_from(importer=importer)

    def _import_metadata(self):
        """Import metadata from parameter file and user made info file.

        Raises
        ------
        MissingInfoFileError
            Raised if no user made info file is provided.
        ImportMetadataOnlyError
            Raised when no format specific importer is initialized. This should
            happen and only happen, when the method is called without first
            importing the experimental data, because :meth:'_import' creates an
            instance of a format specific importer.

        """
        if not os.path.isfile((self.source + ".info")):
            raise MissingInfoFileError("No info file provided")
        info_data = self._import_infofile((self.source + ".info"))
        return info_data

    @staticmethod
    def _fill_axes(dataset):
        """Add an x axis to the data.

        The y (intensity) values (coming from the actual data file) are used as
        already present. The x (field) values are created from the field data
        in the metadata.

        Both sets are combined and transformed into a numpy array.
        """
        field_points = []
        for step_index in range(dataset.metadata.magnetic_field.step_count):
            field_points.append(
                dataset.metadata.magnetic_field.field_min.value +
                dataset.metadata.magnetic_field.step_width.value *
                step_index)
        field_data = np.array(field_points)
        dataset.data.axes[0].values = field_data
        dataset.data.axes[0].quantity = "magnetic field"
        dataset.data.axes[0].unit = "mT"
        dataset.data.axes[1].quantity = "intensity"

    def _map_metadata_and_check_for_overrides(self, metadata, dataset):
        """Perform some operations to yield the final set of metadata.

        Modifies names of metadata information as necessary, combines data from
        the infofile and the spectrometer parameter file and checks for
        possible overrides.

        Parameters
        ----------
        metadata: :class:`dict`
            Loaded metadata to use. First entry: from infofile;
            Second entry: from spectrometer parameter file.

        dataset: :class:`cwepr.dataset.Dataset`
            dataset that should be operated on

        """
        metadata_mapper = aspecd.metadata.MetadataMapper()
        metadata_mapper.metadata = metadata[0]
        metadata_mapper.mappings = self.MAPPINGS
        metadata_mapper.map()
        dataset.metadata.from_dict(metadata_mapper.metadata)
        param_data_mapped = metadata[1]
        for data_part in param_data_mapped:
            dataset.metadata.from_dict(data_part)
            self._check_for_override(metadata_mapper.metadata,
                                     data_part,
                                     dataset)

    def _check_for_override(self, data1, data2, dataset, name=""):
        """Check if metadata from info file is overridden by parameter file.

        Compare the keys in the info file dict with those in each part of the
        DSC/PAR file to find overrides. Any matching keys are considered to be
        overridden and a respective note is added to
        :attr:`cwepr.metadata.DatasetMetadata.metadata_modifications`.
        The method cascades through nested dicts returning a 'path' of the
        potential overrides. E.g., when the key 'a' in the sub dict 'b' is
        found in both dicts the path will be '/b/a'.

        Parameters
        ----------
        data1 : :class:`dict`
            Original data.

        data2: :class:`dict`
            Data that is added to the original dict.

        name: :class:`str`
            Used in the cascade to keep track of the path. This should not be
            set to anything other than the default value.

        """
        top_level = False
        for entry in list(data1.keys()):
            data1[entry.lower()] = data1.pop(entry)
        for entry in data1.keys():
            if isinstance(data1[entry], collections.OrderedDict):
                top_level = True
        for entry in data1.keys():
            if entry in data2.keys():
                if top_level:
                    if name.split("/")[-1] != entry:
                        name = ""
                    name = name + "/" + entry
                    self._check_for_override(data1[entry],
                                             data2[entry],
                                             dataset,
                                             name=name)
                else:
                    dataset.metadata.metadata_modifications.append(
                        "Possible override @ " + name + "/" + entry + ".")

    @staticmethod
    def _modify_field_values(dataset):
        """Wrapper method to get all magnetic field data in desired form.

        Fills in all variables concerning the magnetic field as appropriate
        and transforms them from gauss to millitesla.
        """
        dataset.metadata.magnetic_field.calculate_values()
        dataset.metadata.magnetic_field.gauss_to_millitesla()

    @staticmethod
    def _import_infofile(filename):
        """Use aspecd method to import user made info file.

        Returns
        -------
        infofile_data: :class:`dict`
            Parsed data from the info file.

        """
        infofile_data = aspecd.infofile.parse(filename)
        return infofile_data

    @staticmethod
    def plausible_intensity_values(array):
        """Check imported values for plausibility.

        Check whether the values imported are plausible, i.e. not extremely
        high or
        low.

        .. note::
            In case of a wrong byteorder the values observed can reach 10**300
            and higher. The threshold of what is considered plausible is,
            so far,
            rather arbitrary.

        Parameters
        ----------
        array: :class:`numpy.array`
            Array to check the values of.

        """
        for value in array:
            if value > 10 ** 40 or value < 10 ** -40:
                return False
        return True


class BES3TImporter(GeneralImporter):
    """Specialized Importer for the BES3T format."""

    def __init__(self, source=None):
        super().__init__(source=source)

    def _import(self):
        """Import data file in BES3T format.

        The data is checked for plausibility; if values are too large or too
        small the byte order is changed.

        Returns
        -------
        raw_data: :class:`numpy.array`
            Raw numerical data in processable form.

        """
        complete_filename = self.source + ".DTA"
        raw_data = np.fromfile(complete_filename)
        if not self.plausible_intensity_values(raw_data):
            raw_data = raw_data.byteswap()
        self.dataset.data.data = raw_data
        metadata = self._import_metadata()
        self._map_metadata_and_check_for_overrides(metadata, self.dataset)
        self._modify_field_values(self.dataset)
        self._fill_axes(self.dataset)

    def _import_metadata(self):
        """Import parameter file in BES3T format and user created info file.

        Returns
        -------
        processed_param_data: :class:`dict`
            Parsed data from the source parameter file.

        """
        info_data = super()._import_metadata()
        file_param = open(self.source + ".DSC")
        raw_param_data = file_param.read()
        dsc_file_parser = ParserDSC()
        parsed_param_data = dsc_file_parser.parse_dsc(raw_param_data)
        return [info_data, parsed_param_data]


class ParserDSC:
    r"""Parser for a \*.DSC parameter file belonging to the BES3T format."""

    def parse_dsc(self, file_content):
        r"""Main method for parsing a \*.DSC.

        The is split into its three parts and each of the three parts into a
        dictionary

        Parameters
        ----------
        file_content : :class:`str`
            Content of a complete \*.DSC file.

        Returns
        -------
        three_parts_processed : :class:`list`
            The three parts of the file, each represented by a dictionary
            containing pairs of keys (parameter names) and values (parameter
            values) The dictionaries of part one and three are additionally
            subdivided based on headlines.

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
        data_mapped = self._map_dsc(three_parts_processed)
        return data_mapped

    @staticmethod
    def add_units(parsed_dsc_data):
        """Adds the units to the data values concerning the field.

        Parameters
        ----------
        parsed_dsc_data: :class:`list`
            Original data.

        Returns
        -------
        parsed_dsc_data: :class:`list`
            Data with units added.

        """
        parsed_dsc_data[0]["Data Ranges and Resolutions:"]["XMIN"] += " G"
        parsed_dsc_data[0]["Data Ranges and Resolutions:"]["XWID"] += " G"
        return parsed_dsc_data

    @staticmethod
    def _get_three_parts(file_content):
        r"""Split a \*.DSC file into three parts.

        The three parts are: Descriptor Information, Standard Parameter Layer
        and Device Specific Layer.

        The file is split at the second and third headline which start with
        convenient markers.

        Parameters
        ----------
        file_content: :class:`str`
            Content of a complete \*.DSC file.

        Returns
        -------
        three_parts: :class:`list`
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
        r"""Pre process the first part of a \*.DSC file.

        First part corresponds to "Descriptor Information. The crude string is
        split into subdivisions; the delimiter employed allows to detect the
        different headlines made up of three lines starting with asterisks,
        the center line containing additional text.

        Each subdivision is then transformed into a dict entry with the
        headline, stripped of the first two characters (*\t) as key and the
        remaining information as value. Lines containing an asterisk only are
        removed.

        Parameters
        ----------
        part1: :class:`str`
            Raw first part of a file.

        Returns
        -------
        part1_clean: :class:`dict`
            All subdivisions from the file with headlines as keys and list of
            lines as values; lines devoid of information removed.

        """
        lines = part1.split("\n")
        part1_clean = collections.OrderedDict()
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
        r"""Create a dict from the first or third part () of a \*.DSC file.

        First part corresponds to "Descriptor Information, third part
        corresponds to "Device Specific Layer" For every subdivision. lines are
        split at tabs. The method accounts for lines containing only a
        parameter name with no corresponding value.

        .. note::
            The format of part 3 of a \*.DSC file does not work with tabs,
            but rather with with a variable number of spaces.

        Parameters
        ----------
        p1p3_split: :class:`dict`
            Preprocessed first or third part of a file, split into subdivisions
            with the headline as key. Subdivisions split into lines with lines
            devoid of information removed.

        delimiter: :class:`str`
            Delimiter separating parameter name and value in one line.

        delimiter_width: :class:`int`
            Used to split at a variable number of spaces (could be used for
            other delimiters, too, though). The method will count all
            characters before the first delimiter character and determine the
            number of delimiter characters from the difference to the value of
            delimiter width. If set to zero a single character delimiter will
            be applied.

        Returns
        -------
        p1p3_dict: :class:`dict`
            Data from the input as pairs of key (subdivision name) and value
            (subdivision info). Each subdivision info is also a dict with keys
            (parameter names) and values (parameter values).

        """
        p1p3_dict = collections.OrderedDict()
        for title, subpart in p1p3_split.items():
            param_dict = collections.OrderedDict()
            for line in subpart:
                if delimiter_width != 0:
                    param_count = 0
                    for character in line:
                        if character != delimiter:
                            param_count += 1
                        else:
                            break
                    final_delimiter = (delimiter_width - param_count) * \
                        delimiter
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
        r"""Pre process the second part of a \*.DSC file.

        Second part corresponds to the "Standard parameter layer" The crude
        string is split into lines; lines devoid of information (e.g.
        containing only an asterisk) are removed.

        .. note::
            every line containing asterisks is removed as these appear only
            in headlines and as delimiters.

        .. note::
            For reasons that will probably never be known, in this part,
            parameter names are separated from the values by four spaces
            instead of a tab.

        Parameters
        ----------
        part2: :class:`str`
            Raw second part of a file.

        Returns
        -------
        entries_clean: :class:`list`
            All lines from the file part except those devoid of information.

        """
        entries_param = part2.split("\n")
        entries_clean = list()
        for line in entries_param:
            if "*" not in line:
                entries_clean.append(line)
        return entries_clean

    @staticmethod
    def _create_dict_part2(part2_split):
        r"""Create a dict from the second part of a \*.DSC file.

        Second part corresponds to the "Standard parameter layer" Lines are
        split at tabs. The method accounts for lines containing only a
        parameter name with no corresponding value.

        Parameters
        ----------
        part2_split: :class:`list`
            Preprocessed second part of a file, split into lines, with lines
            devoid of information already removed.

        Raises
        ------
        ExperimentTypeError:
            raised when the type of the experiment file cannot be determined
            from the parameter file or if it is not CW.

        Returns
        -------
        part2_dict: :class:`dict`
            Data from the input as pairs of key (parameter name) and value
            (parameter value).

        """
        part2_dict = collections.OrderedDict()
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
        r"""Pre process the third part of a \*.DSC file.

        Third part corresponds to the "Device Specific Layer" The crude string
        is split into subdivisions, which start with a headline containing the
        fragment ".DVC" Each subdivision is then transformed into a dict entry
        with the headline, stripped of the first eight characters (".DVC")
        as key and the remaining information as value. Lines containing
        asterisks are removed.

        Parameters
        ----------
        part3: :class:`str`
            Raw third part of a file.

        Returns
        -------
        subparts_clean: :class:`dict`
            All subdivisions from the file with headlines as keys and list of
            lines as values; lines devoid of information removed.

        """
        lines = part3.split("\n")
        subdivisions = collections.OrderedDict()
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
        elif current_subpart:
            subdivisions[current_subpart[0][9:]] = current_subpart[1:]
        return subdivisions

    def _map_dsc(self, dsc_data):
        """Prepare data from dsc file and include it in the metadata.

        Parameters
        ----------
        dsc_data: :class:`list`
            List containing all three parts of a dsc file as dicts.

        Returns
        -------
        mapped_data: :class:`list`
            data with the necessary modifications applied to allow for addition
            to the metadata.

        """
        dsc_mapper = aspecd.metadata.MetadataMapper()
        mapped_data = []
        for data_index, data_part in enumerate(dsc_data):
            dsc_mapper.metadata = data_part
            if data_index == 0:
                mapped_data.append(self._map_descriptor(dsc_mapper))
            if data_index == 2:
                mapped_data.append(self._map_device(dsc_mapper))
        return mapped_data

    @staticmethod
    def _map_descriptor(mapper):
        """Prepare part one of the dsc file data for adding to the metadata.

        Parameters
        ----------
        mapper : :obj:`aspecd.metadata.MetadataMapper`
            metadata mapper containing the respective first part of the dsc
            file as metadata.

        """
        mapper.mappings = [
            ["Data Ranges and Resolutions:", "rename_key",
             ["XPTS", "step_count"]],
            ["Data Ranges and Resolutions:", "rename_key",
             ["XMIN", "field_min"]],
            ["Data Ranges and Resolutions:", "rename_key",
             ["XWID", "field_width"]],
            ["", "rename_key",
             ["Data Ranges and Resolutions:", "magnetic_field"]]
        ]
        mapper.map()
        return mapper.metadata

    @staticmethod
    def _map_device(mapper):
        """Prepare part three of the dsc file data for adding to the metadata.

        Parameters
        ----------
        mapper : :obj:`aspecd.metadata.MetadataMapper`
            metadata mapper containing the respective third part of the
            dsc file as metadata.

        """
        mapper.mappings = [
            ["mwBridge, 1.0", "rename_key", ["PowerAtten", "attenuation"]],
            ["", "rename_key", ["mwBridge, 1.0", "bridge"]],
            ["", "rename_key", ["signalChannel, 1.0", "experiment"]]
        ]
        mapper.map()
        return mapper.metadata


class EMXandESPImporter(GeneralImporter):
    """Specialized Importer for the BES3T format."""

    def __init__(self, source=None):
        super().__init__(source=source)

    def _import(self):
        """Import data file in EMX or ESP format.

        There is no easy way to recognize the respective format (identical
        file extensions, only the byte order differs). For this reason, the
        data is checked for plausibility; if values are too large or too
        small the byte order is changed.
        "<f" means little-endian float; ">i4" means big-endian 32-bit integer.

        Returns
        -------
        raw_data: :class:`numpy.array`
            Raw numerical data in processable form.

        """
        complete_filename = self.source + ".spc"
        datatype = np.dtype('<f')
        raw_data = np.fromfile(complete_filename, datatype)
        if not self.plausible_intensity_values(raw_data):
            datatype = np.dtype('>i4')
            raw_data = np.fromfile(complete_filename, datatype)
        self.dataset.data.data = raw_data
        metadata = self._import_metadata()
        self._map_metadata_and_check_for_overrides(metadata, self.dataset)
        self._modify_field_values(self.dataset)
        self._fill_axes(self.dataset)

    def _import_metadata(self):
        """Import parameter file in BES3T format and user created info file.

        Returns
        -------
        processed_param_data: :class:`dict`
            Parsed data from the source parameter file.

        """
        headlines = ["experiment", "spectrometer", "magnetic_field",
                     "bridge", "signal_channel", "probehead", "metadata"]
        info_data = super()._import_metadata()
        file_param = open(self.source + ".par")
        raw_param_data = file_param.read()
        par_file_parser = ParserPAR()
        parsed_param_data = par_file_parser.parse_and_map(raw_param_data)
        data_with_headlines = dict()
        for headline in headlines:
            data_with_headlines[headline] = parsed_param_data
        return [info_data, parsed_param_data]


class ParserPAR:
    r"""Parser for \*.par file belonging to the EMX and ESP/ECS formats."""

    def __init__(self):
        pass

    def parse_and_map(self, file_content):
        """Wrapper method for parsing and mapping.

        Returns
        -------
        content_mapped: :class:`dict`
            Prepared metadata

        """
        content_parsed = self._parse2(file_content)
        content_mapped = self._map_par(content_parsed)
        return content_mapped

    @staticmethod
    def _map_par(dict_):
        mapper = aspecd.metadata.MetadataMapper()
        mapper.metadata = dict_
        mapper.mappings = [
            ["", "rename_key", ["JSD", "accumulations"]],
            ["", "rename_key", ["GST", "field_min"]],
            ["", "rename_key", ["GSI", "field_width"]],
            ["", "rename_key", ["MF", "mw_frequency"]],
            ["", "rename_key", ["MP", "power"]],
            ["", "rename_key", ["RMA", "modulation_amplitude"]],
            ["", "rename_key", ["RRG", "receiver_gain"]],
            ["", "rename_key", ["RCT", "conversion_time"]],
            ["", "rename_key", ["RTC", "time_constant"]]
        ]
        mapper.map()
        return mapper.metadata

    @staticmethod
    def _parse1(file_content):
        r"""Main method for parsing a \*.par into a dictionary.

        The method `_parse2` (vide infra) does the exact same thing in a
        different manner.

        Parameters
        ----------
        file_content: :class:`str`
            Content of a complete \*.par file.

        Returns
        -------
        content_parsed: :class:`dict`

        """
        lines = file_content.split("\n")
        content_parsed = dict()
        for line in lines:
            separating_whitespace = 0
            start_counting = False
            for char in line:
                if char == " ":
                    separating_whitespace += 1
                    start_counting = True
                else:
                    if start_counting:
                        break
            line_content = line.split(" ", separating_whitespace)
            parts_to_remove = list()
            for data_index, data_value in enumerate(line_content):
                if data_value == "":
                    parts_to_remove.append(data_index)
            parts_to_remove.reverse()
            for part in parts_to_remove:
                del line_content[part]
            content_parsed[line_content[0]] = line_content[1]
        return content_parsed

    @staticmethod
    def _parse2(file_content):
        r"""Alternative for parsing a \*.par file using regular expressions.

        The method `_parse1` (vide supra) does the exact same thing in a
        different manner.

        Uses raw string to avoid confusion concerning escape sequences.

        Parameters
        ----------
        file_content: :class:`str`
            Content of a complete \*.par file.

        Returns
        -------
        content_parsed: :class:`dict`

        """
        spacing_pattern = r"[\S]+[\s]+[\S]+"
        exp_object = re.compile(spacing_pattern)
        lines = file_content.split("\n")
        content_parsed = dict()
        for line in lines:
            matching = re.search(exp_object, line)
            if matching:
                end1 = matching.start() + 1
                start2 = matching.end() - 1
                content_parsed[line[:end1]] = line[start2:]
            else:
                content_parsed[line] = ""
        return content_parsed


class ImporterFactory(aspecd.io.DatasetImporterFactory):
    """Factory that returns correct importer class for a given file."""

    supported_formats = {"BES3T": [".DTA", ".DSC"], "Other": [".spc", ".par"]}

    def __init__(self):
        super().__init__()
        self.importers_for_formats = {"BES3T": BES3TImporter,
                                      "Other": EMXandESPImporter}
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
            Raised if no pair of files matching any one supported format can be
            found. Currently only Bruker BES3T format is supported.

        """
        for key, value in self.supported_formats.items():
            if os.path.isfile((source + value[0])) and os.path.isfile(
                (source + value[1])
            ):
                return key
        msg = "No file pair matching a single format was found for path: "\
            + source
        raise NoMatchingFilePairError(message=msg)


class ASCIIExporter(aspecd.io.DatasetExporter):
    """Export a dataset in ASCII format.

    Exports the complete dataset to an ASCII file. At the same time, the
    respective metadata is exported into a YAML file using the functionality
    provided by aspecd.
    """

    def __init__(self):
        super().__init__()

    def _export(self):
        """Export the dataset's numeric data and metadata."""
        file_name_data = self.target + ".txt"
        file_name_meta = self.target + ".yaml"
        np.savetxt(file_name_data, self.dataset.data.data, delimiter=",")
        metadata_writer = aspecd.utils.Yaml()
        metadata = self._get_and_prepare_metadata()
        metadata_writer.dict = metadata
        metadata_writer.write_to(filename=file_name_meta)

    def _get_and_prepare_metadata(self):
        """Prepare the dataset's metadata to be imported.

        Transforms the metadata to a dict and subsequently eliminates all
        instances of numpy.array by transforming them into lists (vide infra).

        Returns
        -------
        metadata_prepared: :class:`dict`
            transformed metadata

        """
        metadata = self.dataset.metadata.to_dict()
        metadata_prepared = self._remove_arrays(metadata)
        return metadata_prepared

    def _remove_arrays(self, dictionary):
        """Removes instances of :class:`numpy.array` from a given dict

        Numpy arrays may interfere with the YAML functionality used for the
        export.

        .. note::
            This is a cascading method that also works on nested dicts.

        Parameters
        ----------
        dictionary: :class:`dict`
            Dictionary to relieve of arrays.

        Returns
        -------
        dictionary: :class:`dict`
            Dictionary relieved of arrays.

        """
        for key, value in dictionary.items():
            if isinstance(value, dict):
                dictionary[key] = self._remove_arrays(value)
            if isinstance(value, np.ndarray):
                dictionary[key].to_list()
        return dictionary
