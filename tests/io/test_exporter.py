import collections
import os
import unittest
import cwepr.io.exporter
import cwepr.dataset


class TestMetadataExporter(unittest.TestCase):
    def setUp(self):
        self.export = cwepr.io.exporter.MetadataExporter()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.filename = ''

    def tearDown(self):
        if os.path.exists(self.export.filename):
            os.remove(self.export.filename)

    def test_metadata_dict_is_dict(self):
        self.assertIsInstance(self.export.metadata_dict, collections.OrderedDict)

    def test_file_exists_with_default_filename_after_export(self):
        self.export.dataset = self.dataset
        self.dataset.export_to(self.export)
        self.assertTrue(os.path.exists(self.export.filename))

    def test_file_exists_with_custom_filename_after_export(self):
        self.export.dataset = self.dataset
        self.export.filename = 'my_filename.yaml'
        self.dataset.export_to(self.export)
        self.assertTrue(os.path.exists(self.export.filename))

    def test_file_exists_with_custom_filename_wo_extension_after_export(self):
        self.export.dataset = self.dataset
        self.export.filename = 'my_filename'
        self.dataset.export_to(self.export)
        self.assertTrue(os.path.exists('my_filename.yaml'))

    def test_metadata_get_cleaned_from_empty_values(self):
        self.dataset.metadata.bridge.mw_frequency.value = 9.5
        self.dataset.metadata.bridge.mw_frequency.unit = 'GHz'
        self.export.dataset = self.dataset
        self.export.filename = 'my_filename'
        self.dataset.export_to(self.export)
        goal_dict = {
            'bridge': {
                'mw_frequency': {
                    'value': 9.5,
                    'unit': 'GHz',
                }
            }
        }
        self.assertDictEqual(goal_dict, self.export.metadata_dict)
