import copy
import os
import random
import unittest

import aspecd.exceptions
import numpy as np

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
        apc = cwepr.processing.AutomaticPhaseCorrection(order=1,
                                                        points_percentage=5)
        self.dataset.process(apc)
        self.assertTrue(np.iscomplex(apc._analytic_signal).all)

    def test_signal_before_and_after_differ(self):
        apc = cwepr.processing.AutomaticPhaseCorrection(order=1,
                                                        points_percentage=20)
        dataset_old = copy.deepcopy(self.dataset)
        self.dataset.process(apc)
        self.assertTrue((dataset_old.data.data != self.dataset.data.data).all())


class TestSubtraction(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-magnettech')
        importer = cwepr.io.magnettech.MagnettechXmlImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_subtraction(self):
        dataset_old = copy.deepcopy(self.dataset)
        second_dataset = copy.deepcopy(self.dataset)
        second_dataset.data.data *= 0.5
        corrector = cwepr.processing.Subtraction()
        corrector.parameters['second_dataset'] = second_dataset
        self.dataset.process(corrector)
        self.assertTrue((dataset_old.data.data != self.dataset.data.data).all())

    def test_second_dataset_contains_original_axis(self):
        second_dataset = copy.deepcopy(self.dataset)
        second_dataset.data.axes[0].values += 0.5
        oldaxis = copy.copy(second_dataset.data.axes[0].values)
        corrector = cwepr.processing.Subtraction()
        corrector.parameters['second_dataset'] = second_dataset
        self.dataset.process(corrector)
        self.assertTrue(np.array_equal(second_dataset.data.axes[0].values,
                                       oldaxis))


class TestFrequencyCorrection(unittest.TestCase):
    def test_frequency_before_is_different_from_after(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-magnettech')
        importer = cwepr.io.magnettech.MagnettechXmlImporter(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)
        old_freq = copy.deepcopy(dataset.metadata.bridge.mw_frequency)
        corrector = cwepr.processing.FrequencyCorrection()
        corrector.parameters['frequency'] = 9.5
        dataset.process(corrector)
        new_freq = dataset.metadata.bridge.mw_frequency
        self.assertNotEqual(new_freq, old_freq)


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


class TestNormalisation(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/not_noisy_data')
        importer = cwepr.io.txt_file.TxtImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_normalisation_of_derivative_to_area(self):
        area = cwepr.processing.NormalisationOfDerivativeToArea()
        self.dataset.process(area)
        self.assertEqual(float, type(area.parameters['area']))


class TestNormalisationToPeakToPeakAmplitude(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/not_noisy_data')
        importer = cwepr.io.txt_file.TxtImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_normalisation_to_peak_to_peak_amplitude(self):
        ptp = cwepr.processing.NormalisationToPeakToPeakAmplitude()
        self.dataset.process(ptp)
        self.assertTrue(max(self.dataset.data.data) <= 1)


class TestNormalisationToReceiverGain(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-bes3t-1D-fieldsweep')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_normalisation_to_receiver_gain(self):
        correction = cwepr.processing.NormalisationToReceiverGain()
        before = max(self.dataset.data.data)
        rg = 10**(self.dataset.metadata.signal_channel.receiver_gain.value /20)
        self.dataset.process(correction)
        after = max(self.dataset.data.data)
        self.assertEqual(before/rg, after)


class TestBaselineCorrectionWithPolynomial(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/sinus_baseline')
        importer = cwepr.io.txt_file.TxtImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_baseline_correction_without_coefficients_works(self):
        baseline_corr = cwepr.processing.BaselineCorrectionWithPolynomial()
        blc = self.dataset.process(baseline_corr)  # Only works upon a copy!
        self.assertTrue(blc.parameters['coefficients'])


class TestSliceExtraction(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/BDPA-2DFieldDelay')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_slice_extraction(self):
        extractor = cwepr.processing.SliceExtraction()
        extractor.parameters['slice'] = 2
        self.assertFalse(extractor.result['slice_info']['value'])
        extractor = self.dataset.process(extractor)
        self.assertTrue(extractor.result['slice_info']['value'])
        
    def test_slicing_with_1D_dataset_raises(self):
        source = os.path.join(ROOTPATH, 'io/testdata/BDPA-1DFieldSweep')
        importer = cwepr.dataset.DatasetFactory()
        dataset = importer.get_dataset(source=source)
        slice_ = cwepr.processing.SliceExtraction()
        slice_.parameters['slice'] = 5
        with self.assertRaises(
                aspecd.exceptions.ProcessingNotApplicableToDatasetError):
            dataset.process(slice_)


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
        with self.assertRaises(
                aspecd.exceptions.ProcessingNotApplicableToDatasetError):
            dataset.process(avg)


class TestAlgebra(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/BDPA-2DFieldDelay')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset = importer.get_dataset(source=source)

    def test_algebra_adds(self):
        algebra = cwepr.processing.Algebra()
        algebra.parameters['kind'] = '+'
        algebra.parameters['value'] = 10
        before = copy.deepcopy(self.dataset.data.data[5, 46])
        self.dataset.process(algebra)
        after = self.dataset.data.data[5, 46]
        self.assertEqual(before+10, after)

    def test_algebra_subtracts(self):
        algebra = cwepr.processing.Algebra()
        algebra.parameters['kind'] = 'minus'
        algebra.parameters['value'] = 0.552
        before = copy.deepcopy(self.dataset.data.data[5, 729])
        self.dataset.process(algebra)
        after = self.dataset.data.data[5, 729]
        self.assertEqual(before-0.552, after)

    def test_algebra_multiply(self):
        algebra = cwepr.processing.Algebra()
        algebra.parameters['kind'] = '*'
        algebra.parameters['value'] = 4
        before = copy.deepcopy(self.dataset.data.data[5, 729])
        self.dataset.process(algebra)
        after = self.dataset.data.data[5, 729]
        self.assertEqual(before*4, after)

    def test_algebra_divide(self):
        algebra = cwepr.processing.Algebra()
        algebra.parameters['kind'] = '/'
        algebra.parameters['value'] = 2
        before = copy.deepcopy(self.dataset.data.data[5, 729])
        self.dataset.process(algebra)
        after = self.dataset.data.data[5, 729]
        self.assertEqual(before/2, after)


class TestSubtractVector(unittest.TestCase):
    def setUp(self):
        source1 = os.path.join(ROOTPATH, 'io/testdata/BDPA-1DFieldSweep')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset1 = importer.get_dataset(source=source1)
        source2 = os.path.join(ROOTPATH, 'io/testdata/BDPA-2DFieldDelay')
        self.dataset2 = importer.get_dataset(source=source2)
        self.vector1 = np.random.rand(self.dataset1.data.data.shape[0], )
        self.vector2 = np.random.rand(self.dataset2.data.data.shape[0], )

    def test_subtract_vector_with_1D_dataset(self):
        subtract = cwepr.processing.SubtractVector()
        subtract.parameters['vector'] = self.vector1
        self.dataset1.process(subtract)

    def test_subtract_vector_with_2D_dataset(self):
        subtract = cwepr.processing.SubtractVector()
        subtract.parameters['vector'] = self.vector2
        self.dataset2.process(subtract)

    def test_subtract_vector_with_wrong_dim_raises(self):
        subtract = cwepr.processing.SubtractVector()
        subtract.parameters['vector'] = self.vector2
        with self.assertRaises(cwepr.processing.DimensionError):
            self.dataset1.process(subtract)


if __name__ == '__main__':
    unittest.main()
