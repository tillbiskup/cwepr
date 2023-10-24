import os
import unittest

import numpy as np

import cwepr.io
import cwepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestCsvImporter(unittest.TestCase):

    def setUp(self):
        self.filename = 'testdata.csv'
        self.data = np.random.random([5, 2])

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_testdata(self):
        with open(self.filename, 'w+', encoding="utf8") as file:
            for row in self.data:
                file.write(f"{row[0]}, {row[1]}\n")

    def test_import(self):
        source = self.filename
        self.create_testdata()
        importer = cwepr.io.CsvImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)

    def test_import_metadata(self):
        source = self.filename
        self.create_testdata()
        importer = cwepr.io.CsvImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
        self.assertTrue(dataset.data.axes[0].unit)


class TestTxtImporter(unittest.TestCase):

    def setUp(self):
        self.filename = 'testdata.csv'
        self.data = np.random.random([5, 2])

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def create_testdata(self, delimiter=" ", separator="."):
        with open(self.filename, 'w+', encoding="utf8") as file:
            for row in self.data:
                file.write(f"{row[0]}{delimiter}{row[1]}\n".replace('.',
                                                                    separator))

    def test_import(self):
        source = self.filename
        self.create_testdata()
        importer = cwepr.io.TxtImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)

    def test_import_with_delimiters(self):
        source = self.filename
        for delimiter in (',', '\t', ';', ' '):
            with self.subTest(delimiter=delimiter):
                self.create_testdata(delimiter=delimiter)
                importer = cwepr.io.TxtImporter(source=source)
                importer.parameters['delimiter'] = delimiter
                dataset = cwepr.dataset.ExperimentalDataset()
                dataset.import_from(importer)
                np.testing.assert_array_equal(self.data[:, 1],
                                              dataset.data.data)

    def test_import_with_separators(self):
        source = self.filename
        for separator in (',',  '.'):
            with self.subTest(separator=separator):
                self.create_testdata(separator=separator)
                importer = cwepr.io.TxtImporter(source=source)
                importer.parameters['separator'] = separator
                dataset = cwepr.dataset.ExperimentalDataset()
                dataset.import_from(importer)
                np.testing.assert_array_equal(self.data[:, 1],
                                              dataset.data.data)

    def test_import_with_file_extensions(self):
        source = self.filename
        for extension in ('.csv',  '.txt', '.dat', '.xyz', '.d', '.data', ''):
            with self.subTest(extension=extension):
                self.filename = self.filename.replace('.csv', extension)
                self.create_testdata()
                importer = cwepr.io.TxtImporter(source=source)
                dataset = cwepr.dataset.ExperimentalDataset()
                dataset.import_from(importer)
                np.testing.assert_array_equal(self.data[:, 1],
                                              dataset.data.data)

    def test_import_with_skip_rows(self):
        source = self.filename
        for skiprows in range(0, 4):
            with self.subTest(skiprows=skiprows):
                self.create_testdata()
                importer = cwepr.io.TxtImporter(source=source)
                importer.parameters['skiprows'] = skiprows
                dataset = cwepr.dataset.ExperimentalDataset()
                dataset.import_from(importer)
                np.testing.assert_array_equal(self.data[skiprows:, 1],
                                              dataset.data.data)

    def test_import_metadata(self):
        source = os.path.join(ROOTPATH, 'testdata/noisy_data.txt')
        importer = cwepr.io.TxtImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
        self.assertTrue(dataset.data.axes[0].unit)
