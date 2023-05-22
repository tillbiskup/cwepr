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

    def test_powersweep_importer_gets_correct_files(self):
        source = os.path.join(ROOTPATH, 'testdata', 'magnettech-power/')
        importer = cwepr.dataset.DatasetFactory().importer_factory
        importer.get_importer(source=source)
        self.assertEqual('PowerSweep', importer.data_format)

    def test_goniometer_importer_does_not_import_inconsistent_data(self):
        source = os.path.join(ROOTPATH, 'testdata', 'magnettech-goniometer/')
        with tempfile.TemporaryDirectory() as tmpdir:
            new_source = os.path.join(tmpdir, 'new')
            importer = cwepr.dataset.DatasetFactory().importer_factory
            importer.get_importer(source=new_source)
            self.assertNotEqual('MagnettechXML', importer.data_format)

    def test_factory_detects_extension(self):
        source = os.path.join(ROOTPATH, 'testdata', 'test-magnettech.xml')
        factory = cwepr.dataset.DatasetFactory()
        importer_factory = factory.importer_factory
        importer_factory.get_importer(source=source)
        root_source, _ = os.path.splitext(source)
        self.assertEqual(importer_factory.data_format, 'MagnettechXML')

    def test_factory_without_extension_returns(self):
        source = os.path.join(ROOTPATH, 'testdata', 'test-magnettech')
        factory = cwepr.dataset.DatasetFactory()
        importer_factory = factory.importer_factory
        importer_factory.get_importer(source=source)
        root_source, _ = os.path.splitext(source)
        self.assertEqual(importer_factory.data_format, 'MagnettechXML')

    def test_with_adf_extension_returns_adf_importer(self):
        source = 'test.adf'
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, aspecd.io.AdfImporter)

    def test_niehsdat_file_returns_correct_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'Pyrene.dat')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, cwepr.io.NIEHSDatImporter)

    def test_niehslmb_file_returns_correct_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'dmpo.lmb')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, cwepr.io.NIEHSLmbImporter)

    def test_niehsexp_file_returns_correct_importer(self):
        source = os.path.join(ROOTPATH, 'testdata', 'e1-05.exp')
        importer = self.factory.get_importer(source=source)
        self.assertIsInstance(importer, cwepr.io.NIEHSExpImporter)
