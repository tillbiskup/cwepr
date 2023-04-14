"""
Importer for the Magnettech XML format.

Magnettech spectrometers can write data to either XML or CSV files.
Currently, only the XML file format is supported. Generally each individual
scan gets saved into its own file, but the averaged data stored in an
additional file with ``_result`` suffixed to its base name.

Two-dimensional datasets, be it from modifying microwave power (power
sweep), modulation amplitude, or goniometer angle, are stored as well in
individual files per second parameter. Additionally, if you perform multiple
averages per parameter value (microwave power, modulation amplitude, goniometer
angle, ...) you will end up with directories for each of these and again
additionally a file with the averaged data.

A slight complication with the way Magnettech spectrometers obtain their
data is the rather high magnetic field sampling frequency (typically 10^4
points) and the non-equidistant field axis. The latter is unique for each
individual measurement in terms of the number of points, grid, and start and
end value. Despite the field range set in the software, the spectrometer
typically records the spectra slightly broader.

For two-dimensional datasets, all this means that the data for the
individual traces have to be interpolated to a common axis before a
two-dimensional matrix can be constructed. As the microwave frequency is
recorded for each individual trace, a frequency correction can be applied
beforehand.

Currently, one-dimensional datasets, angular-dependent measurements
(goniometer sweeps) as well as amplitude sweeps can be imported. Implementing
importers for other types of two-dimensional datasets is planned for the future.

"""
import base64
import glob
import logging
import os
import re
import struct
import xml.etree.ElementTree as et

import dateutil.parser
import numpy as np

import aspecd.annotation
import aspecd.infofile
import aspecd.io
import aspecd.metadata
import aspecd.processing

import cwepr.dataset
import cwepr.metadata
import cwepr.processing
import cwepr.exceptions

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class MagnettechXMLImporter(aspecd.io.DatasetImporter):
    """Import cw-EPR raw data from the Magnettech benchtop spectrometer.

    Magnettech provides a XML-file with the results. Specialities of this
    format are existing and will be briefly explained: The data is encoded in
    hex numbers, and the *y* axis consists of 10 times more points than the
    *y* axis. Therefore, an interpolation is needed to expand the axis to the
    necessary amount of points.


    Attributes
    ----------
    root: :class:`str`
        path of the root directory

    full_filename: :class:`str`
        Filename with file extension

    load_infofile: :class:`bool`
        Skips import of infofile if set to False.

    xml_metadata: :class:`dict`
        Metadata from xml file, eventually imported to metadata.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        # public properties
        self.root = None
        self.full_filename = ''
        self.load_infofile = True
        self.xml_metadata = {}
        self.parameters['data_curve_type'] = 'MW_Absorption'
        self.parameters['axis_curve_type'] = 'BField'
        # private properties
        self._infofile = aspecd.infofile.Infofile()
        self._data_curve = None
        self._axis_curve = None
        self._bfrom = float()
        self._bto = float()
        self._xvalues = None
        self._yvalues = None
        self._infofile = aspecd.infofile.Infofile()

    def _import(self):
        self._clean_up_filename()
        self._get_xml_root_element()

        self._choose_data_source()
        self._get_raw_data()
        self._create_x_axis()
        self._extract_metadata_from_xml()  # Is needed for cutting data

        self._cut_data()
        self._hand_data_to_dataset()

        # First import metadata from infofile, then override hand-written
        # information by metadata from xml-file. The order matters.
        if self.load_infofile and self._infofile_exists():
            self._load_infofile()
            self._map_infofile()
        self._map_metadata_from_xml()
        self._map_dates()

    def _clean_up_filename(self):
        if self.source:
            if self.source.endswith('.xml'):
                self.full_filename = self.source
                self.source = self.source[:-4]
            else:
                self.full_filename = self.source + '.xml'

    def _get_xml_root_element(self):
        """Get the root object/name of the xml document."""
        if not self.source:
            raise cwepr.exceptions.MissingPathError('No path provided')
        if not os.path.exists(self.full_filename):
            raise FileNotFoundError('XML file not found.')
        self.root = et.parse(self.full_filename).getroot()

    def _choose_data_source(self):

        for curve in self.root[0][0][1]:
            if self.parameters['data_curve_type'] == curve.attrib['YType']:
                self._data_curve = curve
            if self.parameters['axis_curve_type'] == curve.attrib['YType']:
                self._axis_curve = curve

    def _get_raw_data(self):
        self._xvalues = \
            self._convert_base64string_to_np_array(self._axis_curve.text)
        self._yvalues = \
            self._convert_base64string_to_np_array(self._data_curve.text)

    @staticmethod
    def _convert_base64string_to_np_array(string):
        # Split string at "=" and add the delimiter afterwards again
        tmpdata = [x + "=" for x in string.split("=") if x]
        # Decode and unpack list of strings
        data = [struct.unpack('d', base64.b64decode(x)) for x in tmpdata]
        data = [i[0] for i in data]
        return np.asarray(data)

    def _create_x_axis(self):
        b_field_x_offset = float(self._axis_curve.attrib['XOffset'])
        b_field_x_slope = float(self._axis_curve.attrib['XSlope'])
        mw_abs_x_offset = float(self._data_curve.attrib['XOffset'])
        mw_abs_x_slope = float(self._data_curve.attrib['XSlope'])

        mw_x = mw_abs_x_offset + \
               np.linspace(0, len(self._yvalues) - 1, num=len(self._yvalues)) \
               * mw_abs_x_slope
        b_field_x = b_field_x_offset + \
                    np.linspace(0, len(self._xvalues) - 1,
                                num=len(self._xvalues)) * b_field_x_slope
        self._xvalues = np.interp(mw_x, b_field_x, self._xvalues)

    def _extract_metadata_from_xml(self):
        # NOTE: Order of these statements is crucial not to overwrite values!
        xml_metadata = self.root[0][0][0].attrib
        xml_metadata.update(self.root[0][0].attrib)
        for childnode in self.root[0][0][0][0]:
            if 'Unit' in childnode.attrib:
                xml_metadata[childnode.attrib['Name']] = \
                    {'value': childnode.text, 'unit': childnode.attrib['Unit']}
            else:
                xml_metadata[childnode.attrib['Name']] = childnode.text
        self.xml_metadata = xml_metadata

    def _cut_data(self):
        self._get_magnetic_field_range()
        mask = (self._xvalues > self._bfrom) & (self._xvalues < self._bto)
        self._xvalues = self._xvalues[mask]
        self._yvalues = self._yvalues[mask]

    def _get_magnetic_field_range(self):
        """Get magnetic field range from preprocessed XML data."""
        if not isinstance(self.xml_metadata['Bfrom'], dict):
            self.xml_metadata['Bfrom'] = \
                {'value': self.xml_metadata['Bfrom'], 'unit': 'mT'}
            self.xml_metadata['Bto'] = \
                {'value': self.xml_metadata['Bto'], 'unit': 'mT'}
        self._bfrom = float(self.xml_metadata['Bfrom']['value'])
        self._bto = float(self.xml_metadata['Bto']['value'])

    def _hand_data_to_dataset(self):
        self.dataset.data.data = self._yvalues
        self.dataset.data.axes[0].values = self._xvalues
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[1].unit = 'mV'
        self.dataset.data.axes[1].quantity = 'intensity'

    def _infofile_exists(self):
        if self._get_infofile_name() and os.path.exists(
                self._get_infofile_name()[0]):
            return True
        print(f'No infofile found for dataset {os.path.split(self.source)[1]},'
              f' import continued without infofile.')
        return False

    def _load_infofile(self):
        """Import infofile and parse it."""
        infofile_name = self._get_infofile_name()
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    def _get_infofile_name(self):
        return glob.glob(self.source + '.info')

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

    def _map_metadata_from_xml(self):
        self.dataset.metadata.temperature_control.temperature.value = \
            float(self.xml_metadata['Temperature']) + 273.15
        self.dataset.metadata.temperature_control.temperature.unit = 'K'
        if self.xml_metadata['Type'] == 'single':
            self.dataset.metadata.experiment.type = \
                self.xml_metadata['KineticMode']
        else:
            self.dataset.metadata.experiment.type = self.xml_metadata['Type']
        self.dataset.metadata.signal_channel.accumulations = \
            self.xml_metadata['MeasurementCount']
        self.dataset.metadata.experiment.variable_parameter = \
            self.xml_metadata['XDatasource']
        self.dataset.metadata.spectrometer.from_dict({
            'model': self.xml_metadata['Device'],
            'software': self.xml_metadata['SWV']})
        self.dataset.metadata.magnetic_field.start.from_string(
            self._dict_to_string(self.xml_metadata['Bfrom']))
        self.dataset.metadata.magnetic_field.stop.from_string(
            self._dict_to_string(self.xml_metadata['Bto']))
        self.dataset.metadata.magnetic_field.sweep_width.value = \
            float(self.xml_metadata['Bto']['value']) - \
            float(self.xml_metadata['Bfrom']['value'])
        self.dataset.metadata.magnetic_field.sweep_width.unit = \
            self.xml_metadata['Bfrom']['unit']
        self.dataset.metadata.magnetic_field.points = \
            len(self.dataset.data.axes[0].values)
        self.dataset.metadata.magnetic_field.field_probe_type = 'Hall'
        self.dataset.metadata.magnetic_field.field_probe_model = 'builtin'
        if self._xvalues[-1] - self._xvalues[0] > 0:
            self.dataset.metadata.magnetic_field.sequence = 'up'
        else:
            self.dataset.metadata.magnetic_field.sequence = 'down'
        self.dataset.metadata.magnetic_field.controller = 'builtin'
        self.dataset.metadata.magnetic_field.power_supply = 'builtin'
        self.dataset.metadata.bridge.model = 'builtin'
        self.dataset.metadata.bridge.controller = 'builtin'
        self.dataset.metadata.bridge.power.from_string(self._dict_to_string(
            self.xml_metadata['MicrowavePower']))
        self.dataset.metadata.bridge.detection = 'mixer'
        self.dataset.metadata.bridge.frequency_counter = 'builtin'
        self.dataset.metadata.bridge.mw_frequency.value = \
            float(self.xml_metadata['MwFreq'])
        self.dataset.metadata.bridge.mw_frequency.unit = 'GHz'
        self.dataset.metadata.bridge.q_value = \
            float(self.xml_metadata['QFactor'])
        self.dataset.metadata.signal_channel.model = 'builtin'
        self.dataset.metadata.signal_channel.modulation_amplifier = 'builtin'
        self.dataset.metadata.signal_channel.accumulations = \
            int(self.xml_metadata['Accumulations'])
        self.dataset.metadata.signal_channel.modulation_frequency.from_string(
            self._dict_to_string(self.xml_metadata['ModulationFreq']))
        self.dataset.metadata.signal_channel.modulation_amplitude.from_string(
            self._dict_to_string(self.xml_metadata['Modulation']))
        self.dataset.metadata.signal_channel.phase.value = \
            float(self.xml_metadata['Phase'])
        self.dataset.metadata.probehead.model = 'builtin'
        self.dataset.metadata.probehead.coupling = 'critical'

    def _map_dates(self):
        self.dataset.metadata.measurement.start = dateutil.parser.parse(
            self.xml_metadata['Timestamp'])
        end = dateutil.parser.parse(self.root.attrib['Timestamp'])
        diff = self.dataset.metadata.measurement.start.tzinfo
        self.dataset.metadata.measurement.end = end.astimezone(diff)
        assert (self.dataset.metadata.measurement.start <
                self.dataset.metadata.measurement.end)

    @staticmethod
    def _dict_to_string(dict_):
        return dict_['value'] + ' ' + dict_['unit']


class GoniometerSweepImporter(aspecd.io.DatasetImporter):
    """Import-angular dependent data from Magnettech benchtop spectrometer.

    .. note::
        Metadata are only taken from the infofile, ignoring the (much likely
        more accurate) xml-file metadata.

    Attributes
    ----------
    load_infofile: :class:`bool`
        Skips import of infofile if set to False.

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.filenames = None
        self.load_infofile = True
        self._infofile = aspecd.infofile.Infofile()
        self._data = None
        self._angles = []

    def _import(self):
        self._get_filenames()
        self._sort_filenames()
        self._import_all_spectra_to_list()
        self._bring_axes_to_same_values()
        self._hand_data_to_dataset()

        self._fill_axes()
        self._get_metadata()

    def _get_filenames(self):
        if not os.path.exists(self.source):
            raise FileNotFoundError
        self.filenames = glob.glob(os.path.join(self.source, '*[0-9]dg*.xml'))

    def _sort_filenames(self):

        def sort_key(string=''):
            num = string.split('gon_')[1]
            num = num.split('dg')[0]
            return int(num)

        self.filenames = sorted(self.filenames, key=sort_key)

    def _import_all_spectra_to_list(self):
        self._data = []
        # import all files without infofile
        for num, filename in enumerate(self.filenames):
            filename = filename[:-4]  # remove extension
            importer = cwepr.io.MagnettechXMLImporter(source=filename)
            importer.load_infofile = False
            self._data.append(cwepr.dataset.ExperimentalDataset())
            self._data[num].import_from(importer)
            self._angles.append(float(importer.xml_metadata['GonAngle']))
            # bring all measurements to the frequency of the first
            if num > 0:
                freq_correction = cwepr.processing.FrequencyCorrection()
                freq_correction.parameters['frequency'] = \
                    self._data[0].metadata.bridge.mw_frequency.value
                self._data[num].process(freq_correction)

        for idx, angle in enumerate(self._angles):
            if angle > 359:
                self._angles[idx] = 0

    def _bring_axes_to_same_values(self):
        extract_range = aspecd.processing.CommonRangeExtraction()
        extract_range.datasets = self._data
        extract_range.process()

    def _interpolation_to_same_number_of_points(self, interpolate, num):
        interpolate.parameters['points'] = len(self._data[0].data.data)
        self._data[num].process(interpolate)

    def _hand_data_to_dataset(self):
        my_array = np.ndarray((len(self._data[0].data.data), len(self._data)))
        self.dataset.data.data = my_array
        for num, set_ in enumerate(self._data):
            self.dataset.data.data[:, num] = set_.data.data

    def _fill_axes(self):
        self._fill_field_axis()
        self._fill_angle_axis()

    def _fill_field_axis(self):
        self.dataset.data.axes[0] = self._data[0].data.axes[0]

    def _fill_angle_axis(self):
        self.dataset.data.axes[1].values = np.asarray(self._angles)
        self.dataset.data.axes[1].unit = 'degree'
        self.dataset.data.axes[1].quantity = 'goniometer angle'

    def _get_metadata(self):
        """Import metadata from infofile.

        .. note::
            Currently, the metadata are only taken from the infofile.
            All information from the xml-file are completely ignored.

        """
        if self.load_infofile and self._infofile_exists():
            self._load_infofile()
            self._map_infofile()

    def _infofile_exists(self):
        if self._get_infofile_name() and os.path.exists(
                self._get_infofile_name()[0]):
            return True
        print(f'No infofile found for dataset '
              f'{os.path.split(self.source)[1]}, import continued without '
              f'infofile.')
        return False

    def _load_infofile(self):
        """Import infofile and parse it."""
        infofile_name = self._get_infofile_name()
        if not infofile_name:
            raise FileNotFoundError('Infofile not found')
        self._infofile.filename = infofile_name[0]
        self._infofile.parse()

    def _get_infofile_name(self):
        if self.source.endswith('/'):
            folder_path = os.path.split(self.source)[0]
            return glob.glob(folder_path + '.info')
        return glob.glob(self.source + '.info')

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
        self._convert_values_to_strings()

    def _map_infofile(self):
        """Bring the metadata to a given format."""
        infofile_version = self._infofile.infofile_info['version']
        self._map_metadata(infofile_version)
        self._assign_comment_as_annotation()

    def _convert_values_to_strings(self):
        def _convert_(value):
            if isinstance(value, str):
                match = re.match(r'[\d+.]', value)
                if match:
                    value = float(value)
            return value

        # ugly but works
        self.dataset.metadata.signal_channel.accumulations = \
            _convert_(self.dataset.metadata.signal_channel.accumulations)
        self.dataset.metadata.bridge.q_value = \
            _convert_(self.dataset.metadata.bridge.q_value)


class AmplitudeSweepImporter(aspecd.io.DatasetImporter):
    """Import modulation amplitude sweep data from a Magnettech Spectrometer.

    The provided XML raw files are read and brought to an unified axis;

    .. note::
        Different to the GoniometerSweepImporter, metadata is only taken from
        the XML source file, ignoring the additional information from the
        infofile.

    Attributes
    ----------
    filenames: :class:`list`
        Filenames of raw XML-files for an amplitude sweep. Is normally
        created automatically from the ``parameters['source']`` directory.


    Examples
    --------
    The amplitude sweep is read in simply with:

    .. code-block:: yaml

       datasets:
        - source: amplitude-sweep-data
          id: amplitude-sweep

    .. versionadded:: 0.4

    """

    def __init__(self, source=''):
        super().__init__(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.filenames = None
        self._data = []
        self._amplitude_list = []
        self._amplitudes = []

    def _import(self):
        self._get_filenames()
        self._sort_filenames()
        self._import_all_spectra_to_list()
        self._bring_axes_to_same_values()
        self._check_amplitudes_and_put_into_list_as_axis()
        self._hand_data_to_dataset()

        self._fill_axes()
        self._import_collected_metadata()

    def _get_filenames(self):
        if not os.path.exists(self.source):
            raise FileNotFoundError
        if not self.filenames:
            self.filenames = glob.glob(os.path.join(self.source, '*mod*.xml'))

    def _sort_filenames(self):

        def sort_key(string=''):
            num = string.split('mod_')[1]
            num = num.split('mT')[0]
            return int(num)

        self.filenames = sorted(self.filenames, key=sort_key)

    def _import_all_spectra_to_list(self):
        # import all files without infofile
        for num, filename in enumerate(self.filenames):
            filename = filename[:-4]  # remove extension
            importer = cwepr.io.MagnettechXMLImporter(source=filename)
            importer.load_infofile = False
            self._data.append(cwepr.dataset.ExperimentalDataset())
            self._data[num].import_from(importer)
            self._amplitudes.append(
                self._data[num].metadata.signal_channel.modulation_amplitude)

            # bring all measurements to the frequency of the first
            if num > 0:
                freq_correction = cwepr.processing.FrequencyCorrection()
                freq_correction.parameters['frequency'] = \
                    self._data[0].metadata.bridge.mw_frequency.value
                self._data[num].process(freq_correction)

    def _bring_axes_to_same_values(self):
        extract_range = aspecd.processing.CommonRangeExtraction()
        extract_range.datasets = self._data
        extract_range.process()

    def _check_amplitudes_and_put_into_list_as_axis(self):
        for amplitude in self._amplitudes:
            if amplitude.unit == 'G':
                amplitude.value /= 10
                amplitude.unit = 'mT'
            self._amplitude_list.append(amplitude.value)

    def _hand_data_to_dataset(self):
        my_array = np.ndarray((len(self._data[0].data.data), len(self._data)))
        self.dataset.data.data = my_array
        for num, set_ in enumerate(self._data):
            self.dataset.data.data[:, num] = set_.data.data

    def _fill_axes(self):
        self._fill_field_axis()
        self._fill_amplitude_axis()

    def _fill_field_axis(self):
        self.dataset.data.axes[0] = self._data[0].data.axes[0]

    def _fill_amplitude_axis(self):
        self.dataset.data.axes[1].values = np.asarray(self._amplitude_list)
        self.dataset.data.axes[1].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'modulation amplitude'

    def _import_collected_metadata(self):
        self._import_fixed_metadata()
        self._import_variable_metadata()
        self._import_variable_metadata()
        self._import_date_time_metadata()

    def _import_fixed_metadata(self):
        self.dataset.metadata.experiment.type = \
            self._data[0].metadata.experiment.type
        self.dataset.metadata.experiment.variable_parameter = 'Modulation ' \
                                                              'Amplitude'
        self.dataset.metadata.signal_channel.accumulations = \
            self._data[0].metadata.experiment.runs
        self.dataset.metadata.spectrometer = self._data[0].metadata.spectrometer
        self.dataset.metadata.magnetic_field.start.from_string(
            ("{:.4f}".format(self.dataset.data.axes[0].values[0])) + ' ' +
            self._data[0].metadata.magnetic_field.start.unit)
        self.dataset.metadata.magnetic_field.stop.from_string(
            ("{:.4f}".format(self.dataset.data.axes[0].values[-1])) + ' ' +
            self._data[0].metadata.magnetic_field.stop.unit)
        self.dataset.metadata.magnetic_field.sweep_width.value = \
            self.dataset.metadata.magnetic_field.stop.value - \
            self.dataset.metadata.magnetic_field.start.value
        self.dataset.metadata.magnetic_field.sweep_width.unit = \
            self.dataset.metadata.magnetic_field.stop.unit
        self.dataset.metadata.magnetic_field.points = \
            len(self.dataset.data.axes[0].values)
        self.dataset.metadata.magnetic_field.field_probe_type = 'Hall'
        self.dataset.metadata.magnetic_field.field_probe_model = 'builtin'
        if self.dataset.data.axes[0].values[-1] - \
                self.dataset.data.axes[0].values[0] > 0:
            self.dataset.metadata.magnetic_field.sequence = 'up'
        else:
            self.dataset.metadata.magnetic_field.sequence = 'down'
        self.dataset.metadata.magnetic_field.controller = 'builtin'
        self.dataset.metadata.magnetic_field.power_supply = 'builtin'
        self.dataset.metadata.bridge.model = 'builtin'
        self.dataset.metadata.bridge.controller = 'builtin'
        self.dataset.metadata.bridge.power = self._data[0].metadata.bridge.power
        self.dataset.metadata.bridge.detection = 'mixer'
        self.dataset.metadata.bridge.frequency_counter = 'builtin'
        self.dataset.metadata.bridge.mw_frequency = \
            self._data[0].metadata.bridge.mw_frequency
        self.dataset.metadata.signal_channel.model = 'builtin'
        self.dataset.metadata.signal_channel.modulation_amplifier = 'builtin'
        self.dataset.metadata.signal_channel.accumulations = \
            self._data[0].metadata.signal_channel.accumulations
        self.dataset.metadata.signal_channel.modulation_frequency = \
            self._data[0].metadata.signal_channel.modulation_frequency
        self.dataset.metadata.signal_channel.phase.value = \
            self._data[0].metadata.signal_channel.phase.value
        self.dataset.metadata.probehead.model = 'builtin'
        self.dataset.metadata.probehead.coupling = 'critical'

    def _import_variable_metadata(self):
        temperatures = []
        qfactors = []
        for _, dataset_ in enumerate(self._data):
            temperatures.append(
                dataset_.metadata.temperature_control.temperature.value)
            qfactors.append(
                dataset_.metadata.bridge.q_value)
        temperature = self._average_and_check_for_deviation(temperatures)
        qfactor = self._average_and_check_for_deviation(qfactors)

        self.dataset.metadata.temperature_control.temperature.value = \
            temperature
        self.dataset.metadata.temperature_control.temperature.unit = \
            self._data[0].metadata.temperature_control.temperature.unit
        self.dataset.metadata.bridge.q_value = qfactor

    @staticmethod
    def _average_and_check_for_deviation(list_of_values, offset_range=0.1):
        value = np.average(list_of_values)
        value_range = max(list_of_values) - min(list_of_values)
        if value_range > offset_range * value:
            logger.warning('Value deviation is more than 10 % of the value '
                           'itself. Please check the measurement conditions.')
        # TODO: Check that logging is working with ASpecD
        # TODO: implement offset range in parameters, make this method
        #  non-static?
        return value

    def _import_date_time_metadata(self):
        starts = []
        ends = []
        for _, dataset_ in enumerate(self._data):
            starts.append(
                dataset_.metadata.measurement.start)
            ends.append(
                dataset_.metadata.measurement.end)

        self.dataset.metadata.measurement.start = \
            min(starts).strftime("%Y-%m-%d %H:%M:%S")
        self.dataset.metadata.measurement.end = \
            max(ends).strftime("%Y-%m-%d %H:%M:%S")
