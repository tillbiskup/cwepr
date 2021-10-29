"""
Importer for the Bruker EMX and ESP format.

The Bruker EMX and ESP formats are used by older Bruker EPR spectrometers,
namely old EMX spectrometers running WinEPR and the ESP line of spectrometers.

A bit of a problem with these two formats is that they are quite similar,
but not the same. Namely the format of the file containing the data in
binary representation is completely different. The way to tell those
two formats apart is to import the ``.par`` file and look, if it contains
``DOS Format`` in the first line.

"""
import glob
import os
import re
from collections import OrderedDict
from datetime import datetime

import aspecd.io
import aspecd.infofile
import aspecd.annotation
import aspecd.metadata
import aspecd.utils
import numpy as np


class ESPWinEPRImporter(aspecd.io.DatasetImporter):

    def __init__(self, source=None):
        # Dirty fix: Cut file extension
        if source.endswith((".spc", ".par")):
            source = source[:-4]
        super().__init__(source=source)
        self.load_infofile = True
        # private properties
        self._infofile = aspecd.infofile.Infofile()
        self._par_dict = dict()
        self._mapper_filename = 'par_keys.yaml'
        self._metadata_dict: OrderedDict[()]
        #        self._is_two_dimensional = False
        #        self._dimensions = []
        self._file_encoding = ''

    def _import(self):
        self._set_defaults()
        self._read_parameter_file()
        self._import_data()

        if self.load_infofile and self._infofile_exists():
            self._load_infofile()
            self._map_infofile()

        self._map_par_file()
        self._set_metadata()
        self._get_number_of_points()
        self._ensure_common_units()
        self._fill_axes()

    def _set_defaults(self):
        default_file = aspecd.utils.Yaml()
        rootpath = os.path.split(os.path.abspath(__file__))[0]
        default_file.read_from(os.path.join(rootpath, 'par_defaults.yaml'))
        self._metadata_dict = default_file.dict

    def _read_parameter_file(self):
        par_filename = self.source + '.par'
        with open(par_filename, 'r') as file:
            lines = file.read().splitlines()

        for line in lines:
            line = line.split(maxsplit=1)
            key = line[0]
            if len(line) > 1:
                value = line[1]
            else:
                value = ''
            if re.match(r'^[+-]?[0-9.]+([eE][+-]?[0-9]*)?$', value):
                value = float(value)
            self._par_dict[key] = value

    def _import_data(self):
        complete_filename = self.source + '.spc'
        self._get_file_encoding()
        raw_data = np.fromfile(complete_filename, self._file_encoding)
        self.dataset.data.data = raw_data

    def _get_file_encoding(self):
        if ('DOS', 'Format') in self._par_dict.items():
            self._file_encoding = '<f'
        else:
            self._file_encoding = '>i4'

    def _infofile_exists(self):
        if self._get_infofile_name() and os.path.exists(
                self._get_infofile_name()[0]):
            return True
        print('No infofile found for dataset %s, import continued without '
              'infofile.' % os.path.split(self.source)[1])
        return False

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
        root_path = \
            os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
        mapper.recipe_filename = os.path.join(
            root_path, 'metadata_mapper_cwepr.yaml')
        mapper.map()
        self.dataset.metadata.from_dict(mapper.metadata)

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info['version']
        self._map_metadata(infofile_version)
        self._assign_comment_as_annotation()

    def _map_par_file(self):
        yaml_file = aspecd.utils.Yaml()
        rootpath = os.path.split(os.path.abspath(__file__))[0]
        yaml_file.read_from(os.path.join(rootpath, self._mapper_filename))
        metadata_dict = {}
        metadata_dict = self._traverse(yaml_file.dict, metadata_dict)
        aspecd.utils.copy_values_between_dicts(metadata_dict,
                                               self._metadata_dict)
        self.extract_datetime()

    def extract_datetime(self):
        start_date = datetime.strptime(self._par_dict['JDA'] + ' '+ \
                                       self._par_dict['JTM'], "%m/%d/%Y %H:%M")
        self._metadata_dict['measurement'] = {}
        self._metadata_dict['measurement']['start'] = str(start_date)

    def _set_metadata(self):
        self.dataset.metadata.from_dict(self._metadata_dict)

    def _traverse(self, dict_, metadata_dict):
        for key, value in dict_.items():
            if isinstance(value, dict):
                metadata_dict[key] = {}
                self._traverse(value, metadata_dict[key])
            elif value in self._par_dict.keys():
                metadata_dict[key] = self._par_dict[value]
        return metadata_dict

    def _ensure_common_units(self):
        """Transform selected values and units to common units.

        Because of information are doubled from the infofile and the
        par-file, some units are wrong and are corrected manually here.
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
            if object_ in ('start', 'stop'):
                if magnetic_field_object.value > 1500:
                    magnetic_field_object.unit = 'G'
                else:
                    magnetic_field_object.unit = 'mT'
            if magnetic_field_object.unit == 'G':
                magnetic_field_object.value /= 10
                magnetic_field_object.unit = 'mT'
            setattr(
                self.dataset.metadata.magnetic_field, object_,
                magnetic_field_object)

    def _fill_axes(self):
        self._get_magnetic_field_axis()
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = \
            self.dataset.metadata.magnetic_field.start.unit
        self.dataset.data.axes[-1].quantity = 'intensity'

    def _get_magnetic_field_axis(self):
        # Abbreviations:
        start = self.dataset.metadata.magnetic_field.start.value
        points = int(self.dataset.metadata.magnetic_field.points)
        sweep_width = self.dataset.metadata.magnetic_field.sweep_width.value
        # in WinEPR, Bruker takes the number of points correctly (in contrast
        # to other formats...)
        stop = start + sweep_width
        # Set axis
        magnetic_field_axis = np.linspace(start, stop, points)
        assert len(magnetic_field_axis) == points, \
            'Length of magnetic field and number of points differ'
        assert len(magnetic_field_axis) == self.dataset.data.data.shape[0], \
            'Length of magnetic field and size of data differ'
        # set more values in dataset
        self.dataset.metadata.magnetic_field.stop.value = stop
        self.dataset.data.axes[0].values = magnetic_field_axis

    def _get_number_of_points(self):
        self.dataset.metadata.magnetic_field.points = len(
            self.dataset.data.data)
