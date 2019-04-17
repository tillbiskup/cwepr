"""Tests for datasets."""

import unittest

from cwepr import dataset
import os


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.Dataset()

    def test_instantiate_class(self):
        pass


class TestImport(unittest.TestCase):
    def setUP(self):
        pass

    def test_import_dataset(self):
        path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        dts = dataset.Dataset()
        dts.import_from_file((path + "/Messdaten/1_No1-dunkel"))


class TestDatasetFactory(unittest.TestCase):
    def setUp(self):
        pass

    def test_dataset_factory(self):
        path = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/Messdaten/1_No1-dunkel"
        factory = dataset.DatasetFactory()
        ds = factory.get_dataset(source=path)
        assert(type(ds) == dataset.Dataset)
