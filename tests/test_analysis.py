import os
from unittest import TestCase

import aspecd.dataset
import numpy as np

import cwepr.analysis
import cwepr.dataset
import cwepr.io.magnettech
import unittest

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-bes3t-1D-fieldsweep')
        importer = cwepr.io.bes3t.BES3TImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(importer)

    def test_field_correction_value(self):
        analysator = cwepr.analysis.FieldCorrectionValue()
        analysator.parameters['standard'] = 'dpph'
        analysator = self.dataset.analyse(analysator)
        self.assertTrue(analysator.parameters['mw_frequency'])
        self.assertTrue(analysator._g_correct == 2.0036)
        self.assertEqual(np.float64, type(analysator.result))

    def test_polynomial_baseline_fitting(self):
        analysator = cwepr.analysis.PolynomialBaselineFitting()
        analysator = self.dataset.analyse(analysator)
        self.assertEqual(np.ndarray, type(analysator.result))

    def test_area_under_curve(self):
        analysator = cwepr.analysis.AreaUnderCurve()
        analysator = self.dataset.analyse(analysator)
        self.assertEqual(np.float64, type(analysator.result))

    def test_linewidth_peak_to_peak(self):
        analysator = cwepr.analysis.LinewidthPeakToPeak()
        analysator = self.dataset.analyse(analysator)
        self.assertEqual(np.float64, type(analysator.result))

    def test_linewidth_fwhm(self):
        analysator = cwepr.analysis.LinewidthFWHM()
        analysator = self.dataset.analyse(analysator)
        self.assertEqual(np.float64, type(analysator.result))

    def test_snr(self):
        analysator = cwepr.analysis.SignalToNoiseRatio()
        analysator = self.dataset.analyse(analysator)
        self.assertEqual(np.float64, type(analysator.result))


class TestAmplitude(unittest.TestCase):
    def setUp(self):
        self.analysator = cwepr.analysis.Amplitude()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.data = np.sin(np.linspace(0, 2 * np.pi, num=500))

    def test_instantiate_class(self):
        cwepr.analysis.Amplitude()

    def test_has_appropriate_description(self):
        self.assertIn('amplitude', self.analysator.description.lower())

    def test_get_amplitude_1d_dataset(self):
        self.dataset.data.data = self.data
        analysis = self.dataset.analyse(self.analysator)
        self.assertAlmostEqual(2, analysis.result, 4)
        self.assertEqual(np.float64, type(analysis.result))

    def test_get_amplitude_2d_dataset(self):
        self.dataset.data.data = np.transpose(np.tile(self.data, (4, 1)))
        analysis = self.dataset.analyse(self.analysator)
        np.testing.assert_almost_equal(analysis.result, 2, decimal=4)
        self.assertEqual(np.ndarray, type(analysis.result))


class TestAmplitudeVsPower(unittest.TestCase):
    def setUp(self):
        self.analysator = cwepr.analysis.AmplitudeVsPower()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        data = np.sin(np.linspace(0, 2 * np.pi, num=500))
        self.dataset.data.data = np.transpose(np.tile(data, (4, 1)))
        self.dataset.data.axes[1].values = np.array([10, 5, 2.5, 1.25, 0.6125,
                                                     0.305])
        self.dataset.data.axes[1].unit = 'mW'

    def test_instantiate_class(self):
        cwepr.analysis.AmplitudeVsPower()

    def test_has_description(self):
        self.assertNotIn('abstract', self.analysator.description.lower())

    def test_calculate_dataset(self):
        analysis = self.dataset.analyse(self.analysator)
        self.assertEqual(2, len(analysis.result.data.axes))
        self.assertEqual(len(np.sqrt(self.dataset.data.axes[1].values)),
                         len(analysis.result.data.axes[0].values))
        self.assertEqual('sqrt(mW)', analysis.result.data.axes[0].unit)

    def test_returns_ascending_x_axis(self):
        analysis = self.dataset.analyse(self.analysator)
        self.assertGreater(analysis.result.data.axes[0].values[1] -
                           analysis.result.data.axes[0].values[0], 0)


class TestPolynomialFitOnData(unittest.TestCase):
    def setUp(self):
        self.analysator = cwepr.analysis.PolynomialFitOnData()
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_instantiate_class(self):
        cwepr.analysis.PolynomialFitOnData()

    def test_has_description(self):
        self.assertNotIn('abstract', self.analysator.description.lower())

    def test_fit_returns_coefficients(self):
        self.dataset.data.data = np.linspace(1, 21)
        self.dataset.data.axes[0].values = np.linspace(1, 11)
        analysis = self.dataset.analyse(self.analysator)
        self.assertTrue(all(analysis.result))

    def test_fit_only_takes_first_points(self):
        self.dataset.data.data = np.concatenate([np.linspace(1, 5, num=5),
                                                 np.linspace(5.1, 6.1, num=5)])
        self.dataset.data.axes[0].values = np.linspace(1, 10, num=10)
        analysis = self.dataset.analyse(self.analysator)
        self.assertAlmostEqual(1, analysis.result[0])

    def test_fit_does_second_order(self):
        self.dataset.data.axes[0].values = np.linspace(1, 10, num=10)
        self.dataset.data.data = 4 * self.dataset.data.axes[0].values ** 2
        self.analysator.parameters['order'] = 2
        analysis = self.dataset.analyse(self.analysator)
        self.assertAlmostEqual(4, analysis.result[0])

    def test_fit_can_return_calculated_dataset(self):
        self.dataset.data.data = np.concatenate([np.linspace(1, 5, num=5),
                                                 np.linspace(5.1, 6.1, num=5)])
        self.dataset.data.axes[0].values = np.linspace(1, 10, num=10)
        self.analysator.parameters['return_type'] = 'dataset'
        analysis = self.dataset.analyse(self.analysator)
        self.assertEqual(aspecd.dataset.CalculatedDataset,
                         type(analysis.result))
        self.assertEqual(self.dataset.data.data.shape[0],
                         len(self.dataset.data.axes[0].values))

    def test_adds_origin_point(self):
        self.dataset.data.data = np.linspace(2, 21)
        self.dataset.data.axes[0].values = np.linspace(2, 11)
        self.analysator.parameters['add_origin'] = True
        self.dataset.analyse(self.analysator)
        self.assertIn(0, self.dataset.data.data)


class TestPtpVsModAmp(TestCase):
    def setUp(self):
        self.analysator = cwepr.analysis.PtpVsModAmp()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        data = np.sin(np.linspace(0, 2*np.pi))
        self.dataset.data.data = np.tile(data, (4, 1))

    def test_instantiate_class(self):
        cwepr.analysis.PtpVsModAmp()

    def test_has_description(self):
        self.assertNotIn('abstract', self.analysator.description.lower())

    def test_perform_task(self):
        analysis = self.dataset.analyse(self.analysator)
        self.assertEqual(aspecd.dataset.CalculatedDataset,
                         type(analysis.result))