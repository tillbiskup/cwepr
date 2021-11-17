import os
import unittest

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
