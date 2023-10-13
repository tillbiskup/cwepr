import os
import unittest

import cwepr.io
import cwepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestTxtImporter(unittest.TestCase):
    def test_import(self):
        source = os.path.join(ROOTPATH, 'testdata/noisy_data')
        importer = cwepr.io.TxtImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)

    def test_import_metadata(self):
        source = os.path.join(ROOTPATH, 'testdata/noisy_data')
        importer = cwepr.io.TxtImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
        self.assertTrue(dataset.data.axes[0].unit)


class TestCsvImporter(unittest.TestCase):
    def test_import(self):
        source = os.path.join(ROOTPATH, 'testdata/noisy_data.txt')
        importer = cwepr.io.CsvImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)

    def test_file_extension(self):
        source = os.path.join(ROOTPATH, 'testdata/noisy_data.txt')

    def test_import_metadata(self):
        source = os.path.join(ROOTPATH, 'testdata/noisy_data.txt')
        importer = cwepr.io.CsvImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
        self.assertTrue(dataset.data.axes[0].unit)
