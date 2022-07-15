import aspecd.io
import numpy as np


class AmericanImporter(aspecd.io.DatasetImporter):

    def __init__(self, source=None):
        super().__init__(source=source)
        self._raw_data = None

    def _import(self):
        self._clean_filenames()
        self._get_raw_data()
        self._import_data()
        self._create_axis()

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
        center_field_mT = self._raw_data[1]/10
        number_points = int(self._raw_data[2])
        sweep_width_mT = self._raw_data[0]/10
        axis = np.linspace(center_field_mT-sweep_width_mT/2,
                           center_field_mT+sweep_width_mT/2,
                           num=number_points)
        assert(axis[0] == center_field_mT-sweep_width_mT/2)
        self.dataset.data.axes[0].values = axis
