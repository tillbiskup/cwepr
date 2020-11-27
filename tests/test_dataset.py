"""Tests for datasets."""

import unittest

from cwepr import dataset
import os

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestDataset(unittest.TestCase):
    def setUp(self):
        self.dataset = dataset.ExperimentalDataset()

    def test_instantiate_class(self):
        pass


class TestImport(unittest.TestCase):
    pass


class TestDatasetFactory(unittest.TestCase):
    def setUp(self):
        pass

    def test_dataset_factory(self):
        source = os.path.join(ROOTPATH, "io/testdata/test-bes3t-1D-fieldsweep")
        factory = dataset.DatasetFactory()
        ds = factory.get_dataset(source=source)
        assert(type(ds) == dataset.ExperimentalDataset)
