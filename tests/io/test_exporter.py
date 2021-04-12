import collections
import os
import unittest
import cwepr.io.exporter
import cwepr.dataset


class TestMetadataExporter(unittest.TestCase):
    def setUp(self):
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.filename = ''

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_metadata_dict_is_dict(self):
        export = cwepr.io.exporter.MetadataExporter()
        self.assertIsInstance(export.metadata_dict, collections.OrderedDict)

    def test_file_exists_with_default_filename_after_export(self):
        export = cwepr.io.exporter.MetadataExporter()
        export.dataset = self.dataset
        self.dataset.export_to(export)
        self.filename = export.filename
        self.assertTrue(os.path.exists(export.filename))

    def test_file_exists_with_custom_filename_after_export(self):
        export = cwepr.io.exporter.MetadataExporter()
        export.dataset = self.dataset
        export.filename = self.filename = 'my_filename.yaml'
        self.dataset.export_to(export)
        self.assertTrue(os.path.exists(export.filename))

    def test_file_exists_with_custom_filename_wo_extension_after_export(self):
        export = cwepr.io.exporter.MetadataExporter()
        export.dataset = self.dataset
        export.filename = 'my_filename'
        self.dataset.export_to(export)
        self.filename = export.filename
        self.assertTrue(os.path.exists('my_filename.yaml'))


if __name__ == '__main__':
    unittest.main()
