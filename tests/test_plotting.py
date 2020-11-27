import os
import unittest
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


if __name__ == '__main__':
    unittest.main()
