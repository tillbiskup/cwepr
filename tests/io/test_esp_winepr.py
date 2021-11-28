import datetime
import os
import unittest

import cwepr.dataset
import cwepr.io

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestESPWinEPRImporter(unittest.TestCase):
    def setUp(self):
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.sources = [os.path.join(ROOTPATH, path) for path in [
            'testdata/ESP', 'testdata/EMX-winEPR.par', 'testdata/winepr.par']]
        self.source = os.path.join(ROOTPATH, 'testdata/winepr.par')

    def test_imports_esp_data_correctly(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[0])
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.data[0] < 10 ** 12)

    def test_imports_winepr_data_correctly(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[1])
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.data[0] < 10 ** 12)

    def test_gets_parameter(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[0])
        self.dataset.import_from(importer)
        self.assertTrue(len(importer._par_dict.keys()) > 1)

    def test_infofile_gets_imported(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[0])
        self.dataset.import_from(importer)
        self.assertTrue(isinstance(
            self.dataset.metadata.bridge.mw_frequency.value, float))

    def test_map_par_parameters_correctly(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[0])
        self.dataset.import_from(importer)
        self.assertEqual(5.000000e+05,
                         self.dataset.metadata.signal_channel.receiver_gain
                         .value)
        self.assertAlmostEqual(339.498,
                               self.dataset.metadata.magnetic_field.start.value,
                               2)

    def test_map_par_parameters_correctly_second_dataset(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[1])
        self.dataset.import_from(importer)
        self.assertNotIn('RRG', importer._par_dict.keys())
        self.assertAlmostEqual(350.5,
                               self.dataset.metadata.magnetic_field.start.value,
                               2)

    def test_import_with_1D_dataset(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.axes[0].unit in ('G', 'mT'))
        self.assertFalse(self.dataset.data.axes[1].unit)

    def test_winepr_sets_default_values(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[2])
        self.dataset.import_from(importer)
        self.assertEqual(100, self.dataset.metadata.signal_channel
                         .modulation_frequency.value)
        self.assertEqual('kHz', self.dataset.metadata.signal_channel
                         .modulation_frequency.unit)

    def test_time_gets_imported_correctly_from_par(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[2])
        self.dataset.import_from(importer)
        date_time = datetime.datetime(2021, 10, 15, 10, 37)
        self.assertEqual(date_time, self.dataset.metadata.measurement.start)

    def test_frequency_gets_written(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.sources[2])
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.metadata.bridge.mw_frequency.value)
