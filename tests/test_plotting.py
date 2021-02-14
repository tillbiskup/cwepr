import os
import unittest

import aspecd.plotting
import cwepr.plotting
import cwepr.dataset
import cwepr.io.magnettech

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestPlotters(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/test-magnettech.xml')
        self.importer = cwepr.io.magnettech.MagnettechXmlImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(self.importer)


class TestGoniometerSweepPlotter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/magnettech-goniometer/')
        self.importer = cwepr.io.magnettech.GoniometerSweepImporter(
            source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(self.importer)

    def test_plotter_does_not_fail(self):
        plotter = cwepr.plotting.GoniometerSweepPlotter()
        self.dataset.plot(plotter)


class TestNewGoniometerPlotter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/magnettech-goniometer/')
        self.importer = cwepr.io.magnettech.GoniometerSweepImporter(
            source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()
        self.dataset.import_from(self.importer)

    def test_plotter_does_not_fail(self):
        plotter = cwepr.plotting.NewGoniometerPlotter()
        saver = cwepr.plotting.Saver()
        saver.filename = 'goniometertest.pdf'
        self.dataset.plot(plotter)
        plotter.save(saver)


class TestAspecdPlotters(unittest.TestCase):
    # Just some tests to test ASpecD with real data
    def setUp(self):
        source = os.path.join(ROOTPATH, 'io/testdata/magnettech-goniometer/')
        importer = cwepr.dataset.DatasetFactory()
        self.dataset1d = importer.get_dataset(source=source)

    def test_aspecd_single_plotter_2d(self):
        plotter = aspecd.plotting.SinglePlotter2D()
        #plotter.type = 'contour'
        self.dataset1d.plot(plotter)
        saver = cwepr.plotting.Saver()
        saver.filename = 'aspecd_singleplot_2d.pdf'
        plotter.save(saver)
        print(self.dataset1d.data.axes[1].values)
