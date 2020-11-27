import os
import unittest

import cwepr.dataset
import cwepr.io

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


@unittest.skip('Fails gloriously')
class TestEMXandESPImporter(unittest.TestCase):
    def test_import_with_EMX_data(self):
        source = os.path.join(ROOTPATH, 'testdata/EMX-winEPR')
        importer = cwepr.io.EMXandESPImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)

    def test_import_with_ESP_data(self):
        source = os.path.join(ROOTPATH, 'testdata/ESP')
        importer = cwepr.io.EMXandESPImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
