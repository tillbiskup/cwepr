import copy
import os
import unittest

import aspecd.exceptions
import numpy as np

import cwepr.exceptions
import cwepr.processing
import cwepr.dataset
import cwepr.io.magnettech

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestAutomaticPhaseCorrection(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/phase-45_noise0.000')
        importer = cwepr.io.txt_file.TxtImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_analytic_signal_is_complex(self):
        apc = cwepr.processing.AutomaticPhaseCorrection()
        apc.parameters['order'] = 1
        apc.parameters['points_percentage'] = 5
        self.dataset.process(apc)
        self.assertTrue(np.iscomplex(apc._analytic_signal).all)

    def test_signal_before_and_after_differ(self):
        apc = cwepr.processing.AutomaticPhaseCorrection()
        apc.parameters['order'] = 1
        apc.parameters['points_percentage'] = 20
        dataset_old = copy.deepcopy(self.dataset)
        self.dataset.process(apc)
        self.assertTrue((dataset_old.data.data != self.dataset.data.data).all())


class TestSubtraction(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-magnettech')
        importer = cwepr.io.magnettech.MagnettechXmlImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)


class TestFrequencyCorrection(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-magnettech')
        importer = cwepr.io.magnettech.MagnettechXmlImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)
        self.corrector = cwepr.processing.FrequencyCorrection()

    def test_frequency_before_is_different_from_after(self):
        old_freq = copy.deepcopy(self.dataset.metadata.bridge.mw_frequency)
        self.corrector.parameters['frequency'] = 9.5
        self.dataset.process(self.corrector)
        new_freq = self.dataset.metadata.bridge.mw_frequency
        self.assertNotEqual(new_freq.value, old_freq.value)

    def test_magnetic_field_axis_is_different(self):
        old_field_axis = copy.deepcopy(
            self.dataset.data.axes[0].values)
        self.corrector.parameters['frequency'] = 8.
        self.dataset.process(self.corrector)
        new_field_axis = self.dataset.data.axes[0].values
        diffs = old_field_axis - new_field_axis
        conditions = (diff == 0 for diff in diffs)
        self.assertFalse(all(conditions))


class GAxisCreation(unittest.TestCase):
    def setUp(self):
        self.proc = cwepr.processing.GAxisCreation()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(100)
        self.dataset.data.axes[0].values = np.linspace(300, 400, num=100)
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.metadata.bridge.mw_frequency.value = 9.5

    def test_instantiate_class(self):
        proc = cwepr.processing.GAxisCreation()
        self.assertTrue(proc.description)

    def test_description_is_appropriate(self):
        self.assertTrue(self.proc.description)
        self.assertIn('g-axis', self.proc.description)

    def test_axis_values_differs_after(self):
        values_before = np.copy(self.dataset.data.axes[0].values)
        self.dataset.process(self.proc)
        values_after = self.dataset.data.axes[0].values
        diffs = values_before - values_after
        conditions = (diff == 0 for diff in diffs)
        self.assertFalse(all(conditions))

    def test_axis_values_are_positive_values(self):
        self.dataset.process(self.proc)
        self.assertTrue(all(self.dataset.data.axes[0].values > 0))

    def test_axis_values_have_correct_range(self):
        self.dataset.process(self.proc)
        condition = np.floor(np.log10(self.dataset.data.axes[0].values)) == 0
        self.assertTrue(all(condition))

    def test_axis_units_differ(self):
        unit_before = np.copy(self.dataset.data.axes[0].unit)
        self.dataset.process(self.proc)
        unit_after = self.dataset.data.axes[0].unit
        self.assertNotEqual(unit_before, unit_after)


class TestAxisInterpolation(unittest.TestCase):
    def setUp(self):
        self.interpolator = cwepr.processing.AxisInterpolation()

    def test_instantiate_class(self):
        pass

    def test_interpolate_returns_new_axis(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-magnettech')
        importer = cwepr.io.magnettech.MagnettechXmlImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
        old_axis = dataset.data.axes[0].values
        corrector = cwepr.processing.AxisInterpolation()
        dataset.process(corrector)
        new_axis = dataset.data.axes[0].values
        self.assertTrue(np.not_equal(new_axis, old_axis).all())


class TestNormalisationOfDerivativeToArea(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/not_noisy_data')
        importer = cwepr.io.txt_file.TxtImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_normalisation_of_derivative_to_area(self):
        area = cwepr.processing.NormalisationOfDerivativeToArea()
        self.dataset.process(area)
        self.assertEqual(float, type(area._area))
        self.assertTrue(max(self.dataset.data.data) < 1)


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/BDPA-1DFieldSweep')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_normalisation_to_receiver_gain(self):
        correction = cwepr.processing.Normalisation()
        correction.parameters['kind'] = 'receiver_gain'
        before = max(self.dataset.data.data)
        rg = 10**(self.dataset.metadata.signal_channel.receiver_gain.value /20)
        self.dataset.process(correction)
        after = max(self.dataset.data.data)
        self.assertEqual(before/rg, after)

    def test_normalisation_to_scan_number(self):
        correction = cwepr.processing.Normalisation()
        correction.parameters['kind'] = 'scan_number'
        before = max(self.dataset.data.data)
        scans = self.dataset.metadata.signal_channel.accumulations
        self.dataset.process(correction)
        after = max(self.dataset.data.data)
        self.assertEqual(before/scans, after)

    def test_normalisation_to_maximum(self):
        correction = cwepr.processing.Normalisation()
        correction.parameters['kind'] = 'max'
        before = np.max(self.dataset.data.data)
        max_ = max(self.dataset.data.data)
        self.dataset.process(correction)
        after = max(self.dataset.data.data)
        self.assertEqual(before/max_, after)

    def test_normalisation_to_minimum(self):
        correction = cwepr.processing.Normalisation()
        correction.parameters['kind'] = 'min'
        before = min(self.dataset.data.data)
        min_ = min(self.dataset.data.data)
        self.dataset.process(correction)
        after = min(self.dataset.data.data)
        self.assertEqual(before/abs(min_), after)

    def test_normalisation_with_wrong_kind_raises(self):
        # direct dependency to aspecd and tested there.
        pass


class TestBaselineCorrectionWithPolynomial(unittest.TestCase):
    def setUp(self):
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_baseline_correction_without_coefficients_works(self):
        self.dataset.data.data = np.ones(100) + 10
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        baseline_corr = cwepr.processing.BaselineCorrectionWithPolynomial()
        blc = self.dataset.process(baseline_corr)  # Only works upon a copy!
        self.assertAlmostEqual(self.dataset.data.data[5], 0)

    def test_blc_writes_coefficients(self):
        self.dataset.data.data = np.ones(100) + 10
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        baseline_corr = cwepr.processing.BaselineCorrectionWithPolynomial()
        blc = self.dataset.process(baseline_corr)  # Only works upon a copy!
        self.assertTrue(blc.parameters['coefficients'])

    def test_baseline_correction_with_unequal_no_of_points_per_side(self):
        baseline_corr = cwepr.processing.BaselineCorrectionWithPolynomial()
        self.dataset.data.data = np.r_[np.ones(5) + 5, np.ones(75), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        baseline_corr.parameters['percentage'] = [5, 20]
        blc = self.dataset.process(baseline_corr)  # Only works upon a copy!
        self.assertAlmostEqual(self.dataset.data.data[-20], 0)

    def test_baseline_correction_with_percentage_float(self):
        baseline_corr = cwepr.processing.BaselineCorrectionWithPolynomial()
        self.dataset.data.data = np.r_[np.ones(20) + 5, np.ones(60), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        baseline_corr.parameters['percentage'] = 20
        blc = self.dataset.process(baseline_corr)  # Only works upon a copy!
        self.assertAlmostEqual(self.dataset.data.data[19], 0)

    def test_baseline_correction_with_percentage_list_one_element(self):
        baseline_corr = cwepr.processing.BaselineCorrectionWithPolynomial()
        self.dataset.data.data = np.r_[np.ones(20) + 5, np.ones(60), np.ones(
            20)+5]
        self.dataset.data.axes[0].values = np.linspace(1, 100, num=100)
        baseline_corr.parameters['percentage'] = [20,]
        self.dataset.process(baseline_corr)
        self.assertAlmostEqual(self.dataset.data.data[19], 0)


class TestAveraging2DDataset(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/BDPA-2DFieldDelay')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_average_2D_dataset(self):
        avg = cwepr.processing.Averaging2DDataset()
        self.assertEqual(3, len(self.dataset.data.axes))
        self.dataset.process(avg)
        self.assertEqual(2, len(self.dataset.data.axes))

    def test_with_1D_dataset_raises(self):
        source = os.path.join(ROOTPATH, 'io/testdata/BDPA-1DFieldSweep')
        importer = cwepr.dataset.DatasetFactory()
        dataset = importer.get_dataset(source=source)
        avg = cwepr.processing.Averaging2DDataset()
        with self.assertRaises(aspecd.exceptions.NotApplicableToDatasetError):
            dataset.process(avg)


class TestSubtractVector(unittest.TestCase):
    def setUp(self):
        source1 = os.path.join(ROOTPATH, 'io/testdata/BDPA-1DFieldSweep')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset1 = importer.get_dataset(source=source1)
        source2 = os.path.join(ROOTPATH, 'io/testdata/BDPA-2DFieldDelay')
        self.dataset2 = importer.get_dataset(source=source2)
        self.vector1 = np.linspace(1, self.dataset1.data.data.shape[0],
                                   num=self.dataset1.data.data.shape[0])
        self.vector2 =  np.linspace(1, self.dataset2.data.data.shape[0],
                                   num=self.dataset2.data.data.shape[0])

    def test_subtract_vector_with_1D_dataset(self):
        subtract = cwepr.processing.SubtractVector()
        subtract.parameters['vector'] = self.vector1
        self.dataset1.process(subtract)

    def test_subtract_vector_with_2D_dataset(self):
        subtract = cwepr.processing.SubtractVector()
        subtract.parameters['vector'] = self.vector2
        before = copy.deepcopy(self.dataset2)
        self.dataset2.process(subtract)
        self.assertAlmostEqual(before.data.data[2, 5]-self.vector2[2],
                               self.dataset2.data.data[2, 5])

    def test_subtract_vector_with_wrong_dim_raises(self):
        subtract = cwepr.processing.SubtractVector()
        subtract.parameters['vector'] = self.vector2
        with self.assertRaises(cwepr.exceptions.DimensionError):
            self.dataset1.process(subtract)