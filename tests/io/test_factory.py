import shutil
import tempfile
import unittest
import os

import cwepr.exceptions
import cwepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestDatasetImporterFactory(unittest.TestCase):
    def test_error_message_no_matching_file_pair(self):
        source = os.path.join(ROOTPATH, 'testdata',
                              'test-magnettech.xml').replace('xml', 'test')
        importer = cwepr.dataset.DatasetFactory()
        with self.assertRaises(cwepr.exceptions.UnsupportedDataFormatError) \
                as error:
            importer.get_dataset(source=source)
        self.assertIn('No file format was found', error.exception.message)

    def test_goniometer_importer_gets_correct_files(self):
        source = os.path.join(ROOTPATH, 'testdata', 'magnettech-goniometer/')
        importer = cwepr.dataset.DatasetFactory().importer_factory
        importer.get_importer(source=source)
        self.assertEqual('GoniometerSweep', importer.data_format)

    def test_goniometer_importer_does_not_recognise_empty_directory(self):
        with tempfile.TemporaryDirectory() as empty_folder:
            importer = cwepr.dataset.DatasetFactory().importer_factory
            with self.assertRaises(cwepr.exceptions.UnsupportedDataFormatError):
                importer.get_importer(source=empty_folder)

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
            with self.assertRaises(cwepr.exceptions.UnsupportedDataFormatError):
                importer.get_importer(source=new_source)

    def test_factory_cuts_filename(self):
        source = os.path.join(ROOTPATH, 'testdata', 'test-magnettech.xml')
        factory = cwepr.dataset.DatasetFactory()
        importer_factory = factory.importer_factory
        importer_factory.get_importer(source=source)
        root_source, _ = os.path.splitext(source)
        self.assertEqual(root_source, importer_factory.source)
