import shutil
import tempfile
import unittest
import os

import aspecd.io

import cwepr.dataset
import cwepr.exceptions
import cwepr.io

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestDatasetImporterFactory(unittest.TestCase):
    def setUp(self):
        self.factory = cwepr.io.DatasetImporterFactory()

    def test_instantiate_class(self):
        pass

    def test_goniometer_importer_gets_correct_files(self):
        source = os.path.join(ROOTPATH, 'testdata', 'magnettech-goniometer/')
        importer = cwepr.dataset.DatasetFactory().importer_factory
        importer.get_importer(source=source)
        self.assertEqual('GoniometerSweep', importer.data_format)

    def test_goniometer_importer_does_not_import_inconsistent_data(self):
        source = os.path.join(ROOTPATH, 'testdata', 'magnettech-goniometer/')
        with tempfile.TemporaryDirectory() as tmpdir:
            new_source = os.path.join(tmpdir, 'new')
            shutil.copytree(source, new_source)
            list_element = os.listdir(new_source)[2]
            source_name = os.path.join(new_source, list_element)
            target_name = os.path.join(new_source, 'fake_name')
            os.rename(source_name, target_name)
            importer = cwepr.dataset.DatasetFactory().importer_factory
            importer.get_importer(source=new_source)
            self.assertNotEqual('MagnettechXML', importer.data_format)

    def test_factory_cuts_filename(self):
        source = os.path.join(ROOTPATH, 'testdata', 'test-magnettech.xml')
        factory = cwepr.dataset.DatasetFactory()
        importer_factory = factory.importer_factory
        importer_factory.get_importer(source=source)
        root_source, _ = os.path.splitext(source)
        self.assertEqual(root_source, importer_factory.source)

    def test_with_adf_extension_returns_adf_importer(self):
        source = 'test.adf'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, aspecd.io.AdfImporter)
