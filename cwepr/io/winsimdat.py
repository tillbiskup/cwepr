"""
Importer for a text file format connected to the WinSim 2002 programs.

For details of WinSim 2002 (sometimes spelled WinSIM), see its
documentation available online from the NIH website:

  * https://www.niehs.nih.gov/research/resources/software/tox-pharm/tools/

Note that WinSim 2002 seems to consist of modules for both, simulating
cw-EPR data as well as for spectrometer control. Furthermore, a series of
file formats has been created for this software, the most important being
a binary format (lmb) and obviously a stripped-down text format with
basically no metadata at all.

The text file format dealt with here is a rather simple file format with
four header lines and only the intensities stored, but actually no
metadata at all. Therefore, using this file format is strongly discouraged
without having all important parameters and details saved otherwise in (
preferably machine-readable) form.

"""

import aspecd.io
import numpy as np


class WinSimDatImporter(aspecd.io.DatasetImporter):
    """
    Importer for WinSim dat (text) files.

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
        self._assert_units()
        self._assert_some_metadata()

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

    def _assert_units(self):
        self.dataset.data.axes[0].unit = 'mT'

    def _assert_some_metadata(self):
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


