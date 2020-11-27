"""
Importer for the Bruker BES3T format.

The Bruker BES3T format gets used by newer Bruker EPR spectrometers, namely
those running with either Xepr or Xenon.

The basic file format is comparably well documented, and it exists in at
least two different versions in the wild: 1.3 and 2.0.

But beware: The device-specific layer is *not* documented, at least not
according to a Bruker EPR Application Scientist. Hence, informed guessing is
necessary for those parts of the file, and it is not clear whether they are
similarly versioned as the basic format.
"""

import collections
import glob
import os
import re

import cwepr.metadata
import numpy as np

import aspecd.annotation
import aspecd.infofile
import aspecd.metadata
import aspecd.io
import aspecd.utils

import cwepr.dataset
from cwepr.io.errors import ExperimentTypeError
from cwepr.io.general import GeneralImporter


class BES3TImporterOld(GeneralImporter):
    """Importer for the Bruker BES3T format.

    The Bruker BES3T format consists of at least two files, a data file with
    extension "DTA" and a descriptor file with extension "DSC". In case of
    multidimensional data, depending on the additional axes, additional data
    files will be written, similarly to the case where the X axis is not
    equidistant (at least the BES3T specification allows this situation).

    """

    def __init__(self, source=None):
        # Dirty fix: Cut file extension
        if source.endswith((".DSC", ".DTA", ".YGF")):
            source = source[:-4]
        super().__init__(source=source)
        self._infofile = aspecd.infofile.Infofile()

    def _import(self):
        """Import data file in BES3T format.

        The data is checked for plausibility; if values are too large or too
        small the byte order is changed.

        Returns
        -------
        raw_data: :class:`numpy.array`
            Raw numerical data in processable form.

        """
        self._import_data()
        metadata = self._import_metadata()
        self._map_metadata_and_check_for_overrides(metadata)
        self._modify_field_values()
        self._fill_axes()

    def _import_data(self):
        complete_filename = self.source + ".DTA"
        raw_data = np.fromfile(complete_filename, dtype='>f8')
        self.dataset.data.data = raw_data

    def _import_metadata(self):
        """Import parameter file in BES3T format and user created info file.

        Returns
        -------
        processed_param_data: :class:`dict`
            Parsed data from the source parameter file.

        """
        self._load_infofile()
        with open(self.source + ".DSC") as file:
            raw_param_data = file.read()
        dsc_file_parser = ParserDSC()
        parsed_param_data = dsc_file_parser.parse_dsc(raw_param_data)
        return [self._infofile.parameters, parsed_param_data]

    def _load_infofile(self):
        infofile_name = glob.glob(''.join([self.source, '.info']))
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    @staticmethod
    def plausible_intensity_values(array):
        """Check imported values for plausibility.

        Check whether the values imported are plausible, i.e. not extremely
        high or low.

        .. note::
            In case of a wrong byte order the values observed can reach 10**300
            and higher. The threshold of what is considered plausible is,
            so far, rather arbitrary.

        Parameters
        ----------
        array: :class:`numpy.array`
            Array to check the values of.

        """
        for value in array:
            if value > 10 ** 40 or value < 10 ** -40:
                return False
        return True

    def _fill_axes(self):
        """Add an x axis to the data.

        The y (intensity) values (coming from the actual data file) are used as
        already present. The x (field) values are created from the field data
        in the metadata.

        Both sets are combined and transformed into a numpy array.
        """
        field_points = []
        for step_index in range(
                self.dataset.metadata.magnetic_field.step_count):
            field_points.append(
                self.dataset.metadata.magnetic_field.start.value +
                self.dataset.metadata.magnetic_field.step_width.value *
                step_index)
        field_data = np.array(field_points)
        self.dataset.data.axes[0].values = field_data
        self.dataset.data.axes[0].quantity = "magnetic field"
        self.dataset.data.axes[0].unit = "mT"
        self.dataset.data.axes[1].quantity = "intensity"


class ParserDSC:
    """Parser for a DSC parameter file belonging to the BES3T format."""

    def parse_dsc(self, file_content):
        r"""Main method for parsing a DSC file.

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
        headline, stripped of the first two characters (\*\t) as key and the
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
                    final_delimiter = \
                        (delimiter_width - param_count) * delimiter
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
             ["XMIN", "start"]],
            ["Data Ranges and Resolutions:", "rename_key",
             ["XWID", "sweep_width"]],
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


class BES3TImporter(aspecd.io.DatasetImporter):
    """Importer for the Bruker BES3T format.

    The Bruker BES3T format consists of at least two files, a data file with
    extension "DTA" and a descriptor file with extension "DSC". In case of
    multidimensional data, additional data files will be written (e.g.
    with extension ".YGF"), similarly to the case where the X axis is not
    equidistant (at least the BES3T specification allows this situation).

    This importer aims to take the parameters from the standard parameter
    layer if available, because it is given in SI units and is documented.

    """

    def __init__(self, source=None):
        # Dirty fix: Cut file extension
        if source.endswith((".DSC", ".DTA", ".YGF")):
            source = source[:-4]
        super().__init__(source=source)
        self.load_infofile = True
        # private properties
        self._infofile = aspecd.infofile.Infofile()
        self._dsc_dict = dict()
        self._mapper_filename = 'dsc_keys.yaml'
        self._is_two_dimensional = False
        self._dimensions = []
        self._file_encoding = ''
        self._points = int()

    def _import(self):
        self._extract_metadata_from_dsc()  # To get dimension information
        self._check_experiment()
        self._set_dataset_dimension()
        self._get_file_encoding()

        if self.load_infofile and self._infofile_exists():
            self._load_infofile()
            self._map_infofile()

        self._import_data()
        self._map_dsc_into_dataset()  # Needed for axes
        self._fill_axes()

        self._ensure_common_units()

    def _import_data(self):
        complete_filename = self.source + ".DTA"
        raw_data = np.fromfile(complete_filename, dtype=self._file_encoding)
        self._dimensions.reverse()
        raw_data = np.reshape(raw_data, self._dimensions)
        self.dataset.data.data = raw_data

    def _set_dataset_dimension(self):
        for key in ('XPTS', 'YPTS'):
            if key in self._dsc_dict.keys():
                self._dimensions.append(int(self._dsc_dict[key]))
        if len(self._dimensions) == 2:
            self._is_two_dimensional = True

    def _get_file_encoding(self):
        encodings = {
            'BIG': '>f8',
            'LIT': '<f8'
        }
        self._file_encoding = encodings[self._dsc_dict['BSEQ']]

    def _infofile_exists(self):
        if self._get_infofile_name() and os.path.exists(
                self._get_infofile_name()[0]):
            return True
        else:
            print('No infofile found for dataset %s, import continued without '
                  'infofile.' % os.path.split(self.source)[1])

    def _extract_metadata_from_dsc(self):
        dsc_filename = self.source + '.DSC'
        with open(dsc_filename, 'r') as file:
            lines = file.read().splitlines()

        for line in lines:
            if not (line.startswith(('*', '#', '.')) or line == ''):
                if '\'' in line:
                    line = line.replace('\'', '')
                line = line.split(maxsplit=1)
                key = line[0]
                if len(line) > 1:
                    value = line[1]
                else:
                    value = ''
                if re.match(r'^[+-]?[0-9.]+([eE][+-]?[0-9]*)?$', value):
                    value = float(value)
                self._dsc_dict[key] = value

    def _map_dsc_into_dataset(self):
        yaml_file = aspecd.utils.Yaml()
        rootpath = os.path.split(os.path.abspath(__file__))[0]
        yaml_file.read_from(os.path.join(rootpath, self._mapper_filename))
        metadata_dict = {}
        metadata_dict = self._traverse(yaml_file.dict,
                                       metadata_dict)
        self._points = int(metadata_dict['magnetic_field'].pop('step_count'))
        self.dataset.metadata.from_dict(metadata_dict)

    def _traverse(self, dict_, metadata_dict):
        for key, value in dict_.items():
            if isinstance(value, dict):
                metadata_dict[key] = {}
                self._traverse(value, metadata_dict[key])
            elif value in self._dsc_dict.keys():
                metadata_dict[key] = self._dsc_dict[value]
        return metadata_dict

    def _fill_axes(self):
        self._get_magnetic_field_axis()
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = self._dsc_dict['XUNI']

        if self._is_two_dimensional:
            self.dataset.data.axes[1].values = \
                np.fromfile(self.source + '.YGF', dtype=self._file_encoding)
            self.dataset.data.axes[1].quantity = self._dsc_dict['YNAM']
            self.dataset.data.axes[1].unit = self._dsc_dict['YUNI']

    def _get_magnetic_field_axis(self):
        # Abbreviations:
        start = self.dataset.metadata.magnetic_field.start.value
        points = self._points
        sweep_width = self.dataset.metadata.magnetic_field.sweep_width.value
        # because Bruker confounds number of steps and points
        stop = start + sweep_width - (sweep_width/(points+1))
        # Set axis
        magnetic_field_axis = np.linspace(start, stop, points)
        assert len(magnetic_field_axis) == points, \
            'Length of magnetic field and step count differ'
        # set more values in dataset
        self.dataset.metadata.magnetic_field.stop.value = stop
        self.dataset.data.axes[0].values = magnetic_field_axis
        self.dataset.metadata.magnetic_field.step_width.value = \
            sweep_width / points

    def _load_infofile(self):
        """Import infofile and parse it."""
        infofile_name = self._get_infofile_name()
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    def _get_infofile_name(self):
        return glob.glob(''.join([self.source.strip(), '.info']))

    def _assign_comment_as_annotation(self):
        comment = aspecd.annotation.Comment()
        comment.comment = self._infofile.parameters['COMMENT']
        self.dataset.annotate(comment)

    def _map_metadata(self, infofile_version):
        """Bring the metadata into a unified format."""
        mapper = \
            cwepr.metadata.MetadataMapper(version=infofile_version,
                                          metadata=self._infofile.parameters)
        mapper.map()
        self.dataset.metadata.from_dict(mapper.metadata)

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info['version']
        self._map_metadata(infofile_version)
        self._assign_comment_as_annotation()

    def _ensure_common_units(self):
        """Transform selected values and units to common units.

        Because of information are doubled from the infofile and the
        DSC-file, some units are wrong and are corrected manually here.
        """
        # microwave frequency
        if self.dataset.metadata.bridge.mw_frequency.value > 50:
            self.dataset.metadata.bridge.mw_frequency.value /= 1e9
            self.dataset.metadata.bridge.mw_frequency.unit = 'GHz'
        # microwave power
        if self.dataset.metadata.bridge.power.value < 0.001:
            self.dataset.metadata.bridge.power.value *= 1e3
            self.dataset.metadata.bridge.power.unit = 'mW'
        # magnetic field objects
        objects_ = ('start', 'stop', 'sweep_width', 'step_width')
        for object_ in objects_:
            magnetic_field_object = getattr(
                self.dataset.metadata.magnetic_field, object_)
            if magnetic_field_object.unit == 'G':
                magnetic_field_object.value /= 10
                magnetic_field_object.unit = 'mT'
            setattr(
                self.dataset.metadata.magnetic_field, object_,
                magnetic_field_object)
        self.dataset.data.axes[0].values /= 10
        self.dataset.data.axes[0].unit = 'mT'
        # modulation frequency
        if self.dataset.metadata.signal_channel.modulation_frequency.value > \
                100:
            self.dataset.metadata.signal_channel.modulation_frequency.value \
                /= 1e3
            self.dataset.metadata.signal_channel.modulation_frequency.unit = \
                'kHz'

    def _check_experiment(self):
        if self._dsc_dict['EXPT'] != 'CW':
            raise ExperimentTypeError(message='Experiment seems not to be a '
                                              'cw-Experiment.')

