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

import glob
import os
import re

import numpy as np

import aspecd.annotation
import aspecd.infofile
import aspecd.metadata
import aspecd.io
import aspecd.utils

import cwepr.metadata
import cwepr.exceptions


class BES3TImporter(aspecd.io.DatasetImporter):
    """Importer for the Bruker BES3T format.

    The Bruker BES3T format consists of at least two files, a data file with
    extension "DTA" and a descriptor file with extension "DSC". In case of
    multidimensional data, additional data files will be written (e.g.
    with extension ".YGF"), similarly to the case where the X axis is not
    equidistant (at least the BES3T specification allows this situation).

    This importer aims to take the parameters from the standard parameter
    layer if available, because it uses SI units and is documented.

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self.load_infofile = True
        # private properties
        self._infofile = aspecd.infofile.Infofile()
        self._dsc_dict = dict()
        self._mapper_filename = 'dsc_keys.yaml'
        self._is_two_dimensional = False
        self._dimensions = []
        self._file_encoding = ''

    def _import(self):
        self._clean_filenames()
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

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith((".DSC", ".DTA", ".YGF")):
            self.source = self.source[:-4]

    def _import_data(self):
        complete_filename = self.source + ".DTA"
        raw_data = np.fromfile(complete_filename, dtype=self._file_encoding)
        raw_data = np.reshape(raw_data, self._dimensions)
        if self._is_two_dimensional:
            raw_data = raw_data.T
        self.dataset.data.data = raw_data

    def _set_dataset_dimension(self):
        for key in ('YPTS', 'XPTS'):
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
        print('No infofile found for dataset %s, import continued without '
              'infofile.' % os.path.split(self.source)[1])
        return False

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
        metadata_dict = self._traverse(yaml_file.dict, metadata_dict)
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
        self.dataset.data.axes[-1].quantity = 'intensity'

        if self._is_two_dimensional:
            self.dataset.data.axes[1].values = \
                np.fromfile(self.source + '.YGF', dtype=self._file_encoding)
            self.dataset.data.axes[1].quantity = self._dsc_dict['YNAM']
            self.dataset.data.axes[1].unit = self._dsc_dict['YUNI']

    def _get_magnetic_field_axis(self):
        # Abbreviations:
        start = self.dataset.metadata.magnetic_field.start.value
        points = int(self.dataset.metadata.magnetic_field.points)
        sweep_width = self.dataset.metadata.magnetic_field.sweep_width.value
        # because Bruker confounds number of steps and points
        stop = start + sweep_width - (sweep_width / (points + 1))
        # Set axis
        magnetic_field_axis = np.linspace(start, stop, points)
        assert len(magnetic_field_axis) == points, \
            'Length of magnetic field and number of points differ'
        assert len(magnetic_field_axis) == self.dataset.data.data.shape[0], \
            'Length of magnetic field and size of data differ'
        # set more values in dataset
        self.dataset.metadata.magnetic_field.stop.value = stop
        self.dataset.data.axes[0].values = magnetic_field_axis

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
        mapper = aspecd.metadata.MetadataMapper()
        mapper.version = infofile_version
        mapper.metadata = self._infofile.parameters
        mapper.recipe_filename = 'cwepr@metadata_mapper_cwepr.yaml'
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
        objects_ = ('start', 'stop', 'sweep_width')
        for object_ in objects_:
            magnetic_field_object = getattr(
                self.dataset.metadata.magnetic_field, object_)
            if magnetic_field_object.unit == 'G':
                magnetic_field_object.value /= 10
                magnetic_field_object.unit = 'mT'
            setattr(
                self.dataset.metadata.magnetic_field, object_,
                magnetic_field_object)
        # axes
        self.dataset.data.axes[0].values /= 10
        self.dataset.data.axes[0].unit = 'mT'
        # modulation frequency
        if self.dataset.metadata.signal_channel.modulation_frequency.value > \
                100:
            self.dataset.metadata.signal_channel.modulation_frequency.value \
                /= 1e3
            self.dataset.metadata.signal_channel.modulation_frequency.unit = \
                'kHz'
        self.dataset.metadata.signal_channel.modulation_amplitude.value *= 1e3
        self.dataset.metadata.signal_channel.modulation_amplitude.unit = 'mT'

    def _check_experiment(self):
        if self._dsc_dict['EXPT'] != 'CW':
            raise cwepr.exceptions.ExperimentTypeError(
                message='Experiment seems not to be a cw-Experiment.'
            )
