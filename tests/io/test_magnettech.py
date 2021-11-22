import os
import shutil
import tempfile
import unittest

import numpy as np

import cwepr.dataset
import cwepr.exceptions
import cwepr.io.magnettech
import cwepr.processing

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestMagnettechXmlImporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech')
        self.importer = cwepr.io.magnettech.MagnettechXMLImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_axis_dimensions_equals_one(self):
        converter = cwepr.io.magnettech.MagnettechXMLImporter()
        testdata = 'CZzAKavudEA=5HabpLDudEA='
        self.assertEqual(1, converter._convert_base64string_to_np_array(
                             testdata).ndim)

    def test_specific_fields_are_filled(self):
        self.dataset.import_from(self.importer)
        # arbitrary attributes that must have been set
        teststr = ['temperature_control.temperature.value',
                   'magnetic_field.start.unit',
                   'bridge.mw_frequency.value']
        for string_ in teststr:
            metadata_object = self.dataset.metadata
            for element in string_.split('.'):
                metadata_object = getattr(metadata_object, element)
            self.assertTrue(metadata_object)

    def test_q_value_is_float(self):
        self.dataset.import_from(self.importer)
        q_value = self.dataset.metadata.bridge.q_value
        self.assertIsInstance(q_value, float)

    def test_import_with_no_file_raises(self):
        importer = cwepr.io.magnettech.MagnettechXMLImporter()
        with self.assertRaises(cwepr.exceptions.MissingPathError):
            self.dataset.import_from(importer)

    def test_import_with_not_existing_file_raises(self):
        source = 'foo.xml'
        importer = cwepr.io.magnettech.MagnettechXMLImporter(source=source)
        with self.assertRaises(FileNotFoundError):
            self.dataset.import_from(importer)

    def test_import_with_no_infofile_continues(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech.xml')
        with tempfile.TemporaryDirectory() as testdir:
            new_source = os.path.join(testdir, 'test-wo-infofile')
            shutil.copyfile(source, new_source + '.xml')
            importer = cwepr.io.magnettech.MagnettechXMLImporter(
                source=new_source)
            self.dataset.import_from(importer)

    def test_with_file_extension(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech.xml')
        importer = cwepr.io.magnettech.MagnettechXMLImporter(source=source)
        self.dataset.import_from(importer)

    def test_comment_gets_written(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech.xml')
        importer = cwepr.io.magnettech.MagnettechXMLImporter(source=source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.annotations)


class TestGoniometerSweepImporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-goniometer')
        self.goniometer_importer = \
            cwepr.io.magnettech.GoniometerSweepImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def instantiate_class(self):
        pass

    def test_has_import_method(self):
        self.assertTrue(hasattr(self.goniometer_importer, '_import'))
        self.assertTrue(callable(self.goniometer_importer._import))

    def test_source_path_doesnt_exist_raises(self):
        source = 'foo/'
        importer = cwepr.io.magnettech.GoniometerSweepImporter(source=source)
        with self.assertRaises(FileNotFoundError):
            self.dataset.import_from(importer)

    def test_sort_filenames_returns_sorted_list(self):
        self.goniometer_importer._get_filenames()
        self.goniometer_importer._sort_filenames()
        sorted_list = self.goniometer_importer.filenames
        nums = []
        for filename in sorted_list:
            num = filename.split('gon_')[1]
            nums.append(num.split('dg')[0])
        for x in range(len(nums)-1):
            self.assertGreater(int(nums[x+1])-int(nums[x]), 0)

    def test_has_import_all_data_to_list_method(self):
        self.assertTrue(hasattr(self.goniometer_importer,
                                '_import_all_spectra_to_list'))
        self.assertTrue(callable(
            self.goniometer_importer._import_all_spectra_to_list))

    def test_angles_smaller_than_360_deg(self):
        self.dataset.import_from(self.goniometer_importer)
        self.assertTrue(all([x < 359 for x in
                             self.goniometer_importer._angles]))

    def test_import_data_fills_dataset(self):
        self.dataset.import_from(self.goniometer_importer)
        self.assertNotEqual(0, self.dataset.data.data.size)

    def test_data_and_filenames_have_same_lengths(self):
        # Check whether all data has been imported correctly and was moved
        # entirely to the final self.dataset.
        self.dataset.import_from(self.goniometer_importer)
        self.assertEqual(len(self.goniometer_importer.filenames),
                         self.goniometer_importer.dataset.data.data.shape[1])

    def test_all_datasets_have_same_frequency(self):
        self.dataset.import_from(self.goniometer_importer)
        frequencies = np.array([])
        for set_ in self.goniometer_importer._data:
            frequencies = np.append(frequencies,
                                    set_.metadata.bridge.mw_frequency.value)
        self.assertAlmostEqual(max(frequencies), min(frequencies))

    def test_goniometer_imports_with_slash_at_source(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-goniometer/')
        importer = cwepr.io.magnettech.GoniometerSweepImporter(
            source=source)
        self.dataset.import_from(importer)

    def test_q_value_is_float(self):
        self.dataset.import_from(self.goniometer_importer)
        q_value = self.dataset.metadata.bridge.q_value
        self.assertIsInstance(q_value, float)
