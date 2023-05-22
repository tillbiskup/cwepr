import datetime
import glob
import os
import re
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

    def test_import_with_incorrect_iso_datetime_writes_correct_datetime(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech.xml')
        mytime = datetime.datetime.fromisoformat(
            '2020-11-18T16:56:04.771146+01:00')
        with tempfile.TemporaryDirectory() as testdir:
            new_source = os.path.join(testdir, 'test-wo-infofile')
            shutil.copyfile(source, new_source + '.xml')
            importer = cwepr.io.magnettech.MagnettechXMLImporter(
                source=new_source)
            self.dataset.import_from(importer)
        imported_start_time = self.dataset.metadata.measurement.start
        self.assertAlmostEqual(mytime, imported_start_time)

    def test_with_file_extension(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech.xml')
        importer = cwepr.io.magnettech.MagnettechXMLImporter(source=source)
        self.dataset.import_from(importer)

    def test_comment_gets_written(self):
        source = os.path.join(ROOTPATH, 'testdata/test-magnettech.xml')
        importer = cwepr.io.magnettech.MagnettechXMLImporter(source=source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.annotations)

    def test_import_with_second_harmonic_imports_first(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-second-harmonic')
        self.importer.source = source
        self.dataset.import_from(self.importer)
        self.assertEqual(self.importer._data_curve.attrib['Name'],
                         'MWAbsorption (1st harm.)')

    def test_check_on_other_source_file_versions(self):
        files = glob.glob('testdata/magnettech-various-formats/*')
        for file in files:
            self.importer.source = file
            try:
                self.dataset.import_from(self.importer)
            except TypeError:
                print(f'File {file} not imported')
                continue
            self.assertIsInstance(self.dataset.data.data, np.ndarray)
            self.assertTrue(self.dataset.metadata.temperature_control.temperature)


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

    def test_import_with_no_infofile_continues(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-goniometer')
        with tempfile.TemporaryDirectory() as testdir:
            new_source = os.path.join(testdir, 'test-wo-infofile')
            shutil.copytree(source, new_source)
            importer = cwepr.io.magnettech.GoniometerSweepImporter(
                source=new_source)
            self.dataset.import_from(importer)


class TestAmplitudeSweepImporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-amplitude')
        self.amplitude_importer = \
            cwepr.io.magnettech.AmplitudeSweepImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def instantiate_class(self):
        pass

    def test_has_import_method(self):
        self.assertTrue(hasattr(self.amplitude_importer, '_import'))
        self.assertTrue(callable(self.amplitude_importer._import))

    def test_source_path_doesnt_exist_raises(self):
        source = 'foo/'
        importer = cwepr.io.magnettech.AmplitudeSweepImporter(source=source)
        with self.assertRaises(FileNotFoundError):
            self.dataset.import_from(importer)

    def test_sort_filenames_returns_sorted_list(self):
        self.amplitude_importer._get_filenames()
        self.amplitude_importer._sort_filenames()
        sorted_list = self.amplitude_importer.filenames
        nums = []
        for filename in sorted_list:
            num = filename.split('mod_')[1]
            nums.append(num.split('mT')[0])
        for x in range(len(nums)-1):
            self.assertGreater(int(nums[x+1])-int(nums[x]), 0)

    def test_has_import_all_data_to_list_method(self):
        self.assertTrue(hasattr(self.amplitude_importer,
                                '_import_all_spectra_to_list'))
        self.assertTrue(callable(
            self.amplitude_importer._import_all_spectra_to_list))

    def test_amplitudes_all_in_mT(self):
        self.dataset.import_from(self.amplitude_importer)
        for item in self.amplitude_importer._amplitudes:
            self.assertTrue(item.unit == 'mT')

    def test_amplitude_list_exists_of_floats(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertTrue(all([type(x) == float for x in
                             self.amplitude_importer._amplitude_list]))

    def test_import_data_fills_dataset(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertNotEqual(0, self.dataset.data.data.size)

    def test_raw_data_is_different_before_and_after_range_extraction(self):
        self.amplitude_importer._get_filenames()
        self.amplitude_importer._sort_filenames()
        self.amplitude_importer._import_all_spectra_to_list()
        before = self.amplitude_importer._data[1].data.axes[0].values
        self.amplitude_importer._bring_axes_to_same_values()
        after = self.amplitude_importer._data[1].data.axes[0].values
        self.assertFalse(np.array_equal(before, after))

    def test_raw_data_have_same_length(self):
        self.amplitude_importer._get_filenames()
        self.amplitude_importer._sort_filenames()
        self.amplitude_importer._import_all_spectra_to_list()
        self.amplitude_importer._bring_axes_to_same_values()
        self.assertTrue(np.array_equal(
            self.amplitude_importer._data[0].data.axes[0].values,
            self.amplitude_importer._data[-1].data.axes[0].values))

    def test_data_and_filenames_have_same_lengths(self):
        # Check whether all data has been imported correctly and was moved
        # entirely to the final self.dataset.
        self.dataset.import_from(self.amplitude_importer)
        self.assertEqual(len(self.amplitude_importer.filenames),
                         self.amplitude_importer.dataset.data.data.shape[1])

    def test_second_axis_has_correct_values(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertListEqual(
            list(self.amplitude_importer.dataset.data.axes[1].values),
            self.amplitude_importer._amplitude_list)

    def test_all_datasets_have_same_frequency(self):
        self.dataset.import_from(self.amplitude_importer)
        frequencies = np.array([])
        for set_ in self.amplitude_importer._data:
            frequencies = np.append(frequencies,
                                    set_.metadata.bridge.mw_frequency.value)
        self.assertAlmostEqual(max(frequencies), min(frequencies))

    def test_amplitude_imports_with_slash_at_source(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-amplitude/')
        importer = cwepr.io.magnettech.AmplitudeSweepImporter(
            source=source)
        self.dataset.import_from(importer)

    def test_fixed_values_are_imported_to_metadata(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertTrue(self.dataset.metadata.spectrometer.model)
        self.assertTrue(self.dataset.metadata.spectrometer.software)

    def test_q_value_is_averaged(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertTrue(self.dataset.metadata.bridge.q_value)

    def test_time_start_is_imported_in_readable_format(self):
        self.dataset.import_from(self.amplitude_importer)
        start = self.dataset.metadata.measurement.start
        self.assertTrue(start)
        rex = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        self.assertTrue(rex.match(start))

    def test_time_end_is_imported_in_readable_format(self):
        self.dataset.import_from(self.amplitude_importer)
        end = self.dataset.metadata.measurement.end
        self.assertTrue(end)
        rex = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        self.assertTrue(rex.match(end))


class TestPowerSweepImporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-power')
        self.power_importer = \
            cwepr.io.magnettech.PowerSweepImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def instantiate_class(self):
        pass

    def test_has_import_method(self):
        self.assertTrue(hasattr(self.power_importer, '_import'))
        self.assertTrue(callable(self.power_importer._import))

    def test_source_path_doesnt_exist_raises(self):
        source = 'foo/'
        importer = cwepr.io.magnettech.PowerSweepImporter(source=source)
        with self.assertRaises(FileNotFoundError):
            self.dataset.import_from(importer)

    def test_sort_filenames_returns_sorted_list(self):
        self.power_importer._get_filenames()
        self.power_importer._sort_filenames()
        sorted_list = self.power_importer.filenames
        nums = []
        for filename in sorted_list:
            num = filename.split('pow_')[1]
            nums.append(num.split('mW')[0])
        for x in range(len(nums)-1):
            self.assertGreater(int(nums[x+1])-int(nums[x]), 0)

    def test_has_import_all_data_to_list_method(self):
        self.assertTrue(hasattr(self.power_importer,
                                '_import_all_spectra_to_list'))
        self.assertTrue(callable(
            self.power_importer._import_all_spectra_to_list))

    def test_power_all_in_mW(self):
        self.dataset.import_from(self.power_importer)
        for item in self.power_importer._power:
            self.assertTrue(item.unit == 'mW')

    def test_power_list_exists_of_floats(self):
        self.dataset.import_from(self.power_importer)
        self.assertTrue(all([type(x) == float for x in
                             self.power_importer._power_list]))

    def test_import_data_fills_dataset(self):
        self.dataset.import_from(self.power_importer)
        self.assertNotEqual(0, self.dataset.data.data.size)

    def test_raw_data_is_different_before_and_after_range_extraction(self):
        self.power_importer._get_filenames()
        self.power_importer._sort_filenames()
        self.power_importer._import_all_spectra_to_list()
        before = self.power_importer._data[1].data.axes[0].values
        self.power_importer._bring_axes_to_same_values()
        after = self.power_importer._data[1].data.axes[0].values
        self.assertFalse(np.array_equal(before, after))

    @unittest.skip
    def test_raw_data_have_same_length(self):
        self.power_importer._get_filenames()
        self.power_importer._sort_filenames()
        self.power_importer._import_all_spectra_to_list()
        self.power_importer._bring_axes_to_same_values()
        self.assertTrue(np.array_equal(
            self.power_importer._data[0].data.axes[0].values,
            self.power_importer._data[-1].data.axes[0].values))

    def test_data_and_filenames_have_same_lengths(self):
        # Check whether all data has been imported correctly and was moved
        # entirely to the final self.dataset.
        self.dataset.import_from(self.power_importer)
        self.assertEqual(len(self.power_importer.filenames),
                         self.power_importer.dataset.data.data.shape[1])

    def test_second_axis_has_correct_values(self):
        self.dataset.import_from(self.power_importer)
        self.assertListEqual(
            list(self.power_importer.dataset.data.axes[1].values),
            self.power_importer._power_list)

    def test_all_datasets_have_same_frequency(self):
        self.dataset.import_from(self.power_importer)
        frequencies = np.array([])
        for set_ in self.power_importer._data:
            frequencies = np.append(frequencies,
                                    set_.metadata.bridge.mw_frequency.value)
        self.assertAlmostEqual(max(frequencies), min(frequencies))

    def test_power_imports_with_slash_at_source(self):
        source = os.path.join(ROOTPATH, 'testdata/magnettech-power/')
        importer = cwepr.io.magnettech.PowerSweepImporter(
            source=source)
        self.dataset.import_from(importer)

    def test_fixed_values_are_imported_to_metadata(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertTrue(self.dataset.metadata.spectrometer.model)
        self.assertTrue(self.dataset.metadata.spectrometer.software)

    def test_q_value_is_averaged(self):
        self.dataset.import_from(self.amplitude_importer)
        self.assertTrue(self.dataset.metadata.bridge.q_value)

    def test_time_start_is_imported_in_readable_format(self):
        self.dataset.import_from(self.amplitude_importer)
        start = self.dataset.metadata.measurement.start
        self.assertTrue(start)
        rex = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        self.assertTrue(rex.match(start))

    def test_time_end_is_imported_in_readable_format(self):
        self.dataset.import_from(self.amplitude_importer)
        end = self.dataset.metadata.measurement.end
        self.assertTrue(end)
        rex = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        self.assertTrue(rex.match(end))
