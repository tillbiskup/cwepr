"""
The US National Institute of Environmental Health Sciences (NIEHS) provides
a collection of public epr software tools, abbreviated PEST. With those
software tools comes a collection of file formats used internally,
both binary and text-based.

For a general overview of PEST, see its homepage:

* https://www.niehs.nih.gov/research/resources/software/tox-pharm/tools/

All these file formats have in common that they contain rather few
metadata. Therefore, it is highly recommended that users provide metadata by
other means, at best in machine-readable format. One possibility would be
to use infofiles, as described in the respective :mod:`aspecd.infofile`
module.


Overview of file formats
========================

The PEST homepage provides an overview of the different file formats
available, for details see:

* https://www.niehs.nih.gov/research/resources/software/tox-pharm/tools/pest/

For convenience, the most important information is provided below:

==============  ============================================================
File extension  Description
==============  ============================================================
     .lmb       NIEHS exclusive binary format
     .exp       ASCII text format with various different realisations
     .dat       ASCII HP-PC interchange format
==============  ============================================================

Just to make things easier, the lmb format exists in two flavours,
with extensions ".lmb" and ".sim", the latter for simulated spectra.

Equally, the ASCII experimental spectra can exist in a plethora of
variations, according to the official documentation: with and without
header, with one or two columns, and with the first column being
magnetic field (in Gauss), time (in seconds), or g value. Interestingly
enough, though, the accepted input format is always two columns with
first column interpreted as magnetic field values.


Module documentation
====================

"""
import struct

import numpy as np

import aspecd.io
import aspecd.annotation


class NIEHSDatImporter(aspecd.io.DatasetImporter):
    """
    Importer for NIEHS PEST dat (text) files.

    The text file format dealt with here is a rather simple file format
    with four header lines and only the intensities stored, but actually
    no metadata at all. An example is given below:

    .. code-block:: text

        ESRFILE
        50
        3359.27
        8192
        -12.234
           -5.48376
           -2.22887
           0.284066
           -0.698693


    The first four lines have special meanings and are referred to as
    "header", the following lines (up to the end of the file) are the actual
    intensity values of the stored EPR spectrum.

    =======  ==============================================================
    Content  Description
    =======  ==============================================================
    ESRFILE  Identifier of the file type
    50       scan range in Gauss (here: 50 G)
    3359.27  center field in Gauss (here: 3359.27 G)
    8192     number of data points (here: 8192) - usually a power of two
    =======  ==============================================================

    As mentioned above, all following lines contain just the intensity
    values. Therefore, the importer needs to reconstruct the field axis
    from the center field and scan range values provided. No further
    metadata (such as microwave frequency) are available, therefore,
    the spectra usually cannot be analysed appropriately unless the
    missing information is provided by other means.


    .. note::
        Due to the lack of any metadata of this format, the resulting
        dataset is quite limited in its metadata. Only the axes measures
        and units are added (by informed guessing). Therefore, you are
        highly encouraged to provide the lacking metadata by other means.


    .. versionadded:: 0.3

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self._raw_data = None
        self._raw_metadata = {}

    def _import(self):
        self._clean_filenames()
        self._get_raw_data()
        self._import_data()
        self._create_axis()
        self._assign_units()
        self._assign_some_metadata()

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith((".dat", ".DAT")):
            self.source = self.source[:-4]

    def _get_raw_data(self):
        complete_filename = self.source + ".dat"
        self._raw_data = np.loadtxt(complete_filename, skiprows=1)

    def _import_data(self):
        self.dataset.data.data = self._raw_data[3:]

    def _create_axis(self):
        self._raw_metadata['center_field_mT'] = center_field_mT =  \
            self._raw_data[1]/10
        self._raw_metadata['number_points'] = number_points = int(
            self._raw_data[2])
        self._raw_metadata['sweep_width_mT'] = sweep_width_mT = \
            self._raw_data[0]/10
        self._raw_metadata['start'] = center_field_mT-sweep_width_mT/2
        self._raw_metadata['stop'] = center_field_mT+sweep_width_mT/2
        axis = np.linspace(center_field_mT-sweep_width_mT/2,
                           center_field_mT+sweep_width_mT/2,
                           num=number_points)
        assert(axis[0] == center_field_mT-sweep_width_mT/2)
        self.dataset.data.axes[0].values = axis

    def _assign_units(self):
        self.dataset.data.axes[0].unit = 'mT'

    def _assign_some_metadata(self):
        self.dataset.metadata.magnetic_field.start.value = self._raw_metadata[
            'start']
        self.dataset.metadata.magnetic_field.stop.value = self._raw_metadata[
            'stop']
        self.dataset.metadata.magnetic_field.points = self._raw_metadata[
            'number_points']
        self.dataset.metadata.magnetic_field.sweep_width.value = \
            self._raw_metadata['sweep_width_mT']
        self.dataset.metadata.magnetic_field.sweep_width.unit = \
            self.dataset.metadata.magnetic_field.start.unit = \
            self.dataset.metadata.magnetic_field.stop.unit = 'mT'


class NIEHSLmbImporter(aspecd.io.DatasetImporter):
    """
    Importer for NIEHS PEST lmb (binary) files.

    .. todo::
        Assign further metadata. Note that some metadata are entered
        manually, and therefore, parsing values with units with or without
        space between value and unit can be quite tricky.


    .. versionadded:: 0.3

    """

    def __init__(self, source=None):
        super().__init__(source=source)
        self._raw_data = None
        self._file_format = None
        self._parameters = {}
        self._metadata = {}
        self._position = 0
        self._comment = []

    def _import(self):
        self._clean_filenames()
        self._get_raw_data()
        self._detect_file_format()
        self._read_and_assign_parameters()
        self._read_data()
        self._read_comments_and_metadata()
        self._create_axis()
        self._assign_comment()
        self._assign_metadata()

    def _clean_filenames(self):
        # Dirty fix: Cut file extension
        if self.source.endswith((".lmb", ".sim")):
            self.source = self.source[:-4]

    def _get_raw_data(self):
        filename = self.source + ".lmb"
        with open(filename, 'rb') as file:
            self._raw_data = file.read()

    def _detect_file_format(self):
        self._file_format = self._raw_data[:4].decode('utf-8')

    def _read_and_assign_parameters(self):
        parameters = []
        self._position = 4
        MAX_PAR = 20
        for idx in range(MAX_PAR):
            parameters.append(
                struct.unpack('f', self._raw_data[
                                   self._position:self._position + 4])[0])
            # print(parameters[idx])
            self._position += 4
        # Note: Only assign those parameters necessary in the given context
        self._parameters = {
            "sweep_width": parameters[0] / 10,
            "center_field": parameters[1] / 10,
            "npoints": int(parameters[2]),
            "scan_time": parameters[9],
        }

    def _read_data(self):
        data = []
        for idx in range(int(self._parameters["npoints"])):
            data.append(
                struct.unpack('f', self._raw_data[
                                   self._position:self._position + 4])[0])
            self._position += 4
        self.dataset.data.data = np.asarray(data)

    # noinspection GrazieInspection
    def _read_comments_and_metadata(self):
        COMMENT_SIZE = 60
        self._comment = [self._raw_data[
                   self._position:self._position + COMMENT_SIZE].decode(
            'utf-8').replace('\x00', '').strip()]
        self._position += COMMENT_SIZE

        STR_NUM = 20
        STR_SIZE = 12
        strings = []
        for idx in range(STR_NUM):
            strings.append(self._raw_data[
                           self._position:self._position + STR_SIZE].decode(
                'utf-8').replace('\x00', '').strip())
            self._position += STR_SIZE

        if self._file_format == 'ESR2':
            for idx in range(2):
                self._comment.append(
                    self._raw_data[
                    self._position:self._position + COMMENT_SIZE].decode(
                        'utf-8').replace('\x00', '').strip())
                self._position += COMMENT_SIZE

        # Only those metadata of interest are mapped
        # Note: The first nine parameters are input MANUALLY, never trust em.
        self._metadata = {
            "modulation_amplitude": strings[1],
            "modulation_frequency": strings[2],
            "time_constant": strings[3],
            "receiver_gain": float(strings[4]),
            "mw_power": strings[7],
            "mw_frequency": strings[8],
            "date": strings[9],
            "time": strings[10],
            "n_scans": int(strings[12]),
            "temperature": strings[13],
        }

    def _create_axis(self):
        self._parameters['start'] = \
            self._parameters['center_field'] \
            - self._parameters['sweep_width'] / 2
        self._parameters['stop'] = \
            self._parameters['center_field'] \
            + self._parameters['sweep_width'] / 2
        axis = np.linspace(self._parameters['start'],
                           self._parameters['stop'],
                           num=self._parameters['npoints'])
        self.dataset.data.axes[0].values = axis
        self.dataset.data.axes[0].unit = 'mT'

    def _assign_comment(self):
        comment_annotation = aspecd.annotation.Comment()
        comment_annotation.comment = self._comment
        self.dataset.annotate(comment_annotation)

    def _assign_metadata(self):
        self.dataset.metadata.magnetic_field.start.value = \
            self.dataset.data.axes[0].values[0]
        self.dataset.metadata.magnetic_field.stop.value = \
            self.dataset.data.axes[0].values[-1]
        self.dataset.metadata.magnetic_field.sweep_width.value = \
            self._parameters["sweep_width"]
        self.dataset.metadata.magnetic_field.start.unit = \
            self.dataset.metadata.magnetic_field.stop.unit = \
            self.dataset.metadata.magnetic_field.sweep_width.unit = "mT"
        self.dataset.metadata.signal_channel.accumulations = \
            self._metadata["n_scans"]
