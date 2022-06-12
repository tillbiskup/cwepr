import os
import unittest

import matplotlib
import numpy as np

from aspecd.plotting import Saver

import cwepr.plotting
import cwepr.dataset
import cwepr.io.magnettech

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestGoniometerSweepPlotter(unittest.TestCase):
    def setUp(self):
        self.filename = 'goniometertest.pdf'
        source = os.path.join(ROOTPATH, 'io/testdata/magnettech-goniometer/')
        self.importer = cwepr.io.magnettech.GoniometerSweepImporter(
            source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(self.importer)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_plotter_does_not_fail(self):
        plotter = cwepr.plotting.GoniometerSweepPlotter()
        plotter.dataset = self.dataset
        plotter.properties.axes.xlim = [337.5, 339]
        saver = Saver()
        saver.filename = self.filename
        self.dataset.plot(plotter)
        plotter.save(saver)


class TestSinglePlotter1D(unittest.TestCase):

    def setUp(self):
        self.plotter = cwepr.plotting.SinglePlotter1D()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'
        self.dataset.data.axes[1].unit = 'V'
        self.plotter.dataset = self.dataset

    def test_has_g_axis_parameter(self):
        self.assertTrue('g-axis' in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertIn('g\\ value',
                      secondary_axes[0].get_xaxis().get_label().get_text())


class TestSinglePlotter2D(unittest.TestCase):

    def setUp(self):
        self.plotter = cwepr.plotting.SinglePlotter2D()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random([5, 5])
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'time'
        self.dataset.data.axes[1].unit = 's'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.data.axes[2].unit = 'V'
        self.plotter.dataset = self.dataset

    def test_has_g_axis_parameter(self):
        self.assertTrue('g-axis' in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertIn('g\\ value',
                      secondary_axes[0].get_xaxis().get_label().get_text())


class TestSinglePlotter2DStacked(unittest.TestCase):

    def setUp(self):
        self.plotter = cwepr.plotting.SinglePlotter2DStacked()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random([5, 5])
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'time'
        self.dataset.data.axes[1].unit = 's'
        self.dataset.data.axes[2].quantity = 'intensity'
        self.dataset.data.axes[2].unit = 'V'
        self.plotter.dataset = self.dataset

    def test_has_g_axis_parameter(self):
        self.assertTrue('g-axis' in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertIn('g\\ value',
                      secondary_axes[0].get_xaxis().get_label().get_text())


class TestMultiPlotter1D(unittest.TestCase):

    def setUp(self):
        self.plotter = cwepr.plotting.MultiPlotter1D()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'
        self.dataset.data.axes[1].unit = 'V'
        self.plotter.datasets = [self.dataset]

    def test_has_g_axis_parameter(self):
        self.assertTrue('g-axis' in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertIn('g\\ value',
                      secondary_axes[0].get_xaxis().get_label().get_text())


class TestMultiPlotter1DStacked(unittest.TestCase):

    def setUp(self):
        self.plotter = cwepr.plotting.MultiPlotter1DStacked()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.data.data = np.random.random(5)
        self.dataset.data.axes[0].quantity = 'magnetic field'
        self.dataset.data.axes[0].unit = 'mT'
        self.dataset.data.axes[1].quantity = 'intensity'
        self.dataset.data.axes[1].unit = 'V'
        self.plotter.datasets = [self.dataset]

    def test_has_g_axis_parameter(self):
        self.assertTrue('g-axis' in self.plotter.parameters)

    def test_g_axis_adds_secondary_axis(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertTrue(secondary_axes)

    def test_g_axis_has_correct_label(self):
        self.plotter.parameters['g-axis'] = True
        self.plotter.plot()
        secondary_axes = [
            child for child in self.plotter.ax.get_children()
            if isinstance(child, matplotlib.axes._secondary_axes.SecondaryAxis)
        ]
        self.assertIn('g\\ value',
                      secondary_axes[0].get_xaxis().get_label().get_text())
