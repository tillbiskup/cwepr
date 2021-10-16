import os
import unittest

import cwepr.dataset
import cwepr.io

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestBES3TImporter(unittest.TestCase):
    def setUp(self):
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.sources = ('testdata/ESP', 'testdata/EMX-winEPR.par',
                        'testdata/winepr.par')
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

    @unittest.skip
    def test_import_with_1D_dataset(self):
        importer = cwepr.io.esp_winepr.ESPWinEPRImporter(source=self.source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.axes[0].unit)
        self.assertFalse(self.dataset.data.axes[1].unit)
