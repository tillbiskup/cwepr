import unittest
import os

import cwepr.io.american_format
import cwepr.dataset


ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class MyTestCase(unittest.TestCase):

    def setUp(self):
        source = os.path.join(ROOTPATH, 'testdata/Pyrene')
        self.importer = cwepr.io.american_format.AmericanImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_class_exists(self):
        pass

    def test_txt_file_imported(self):
        self.dataset.import_from(self.importer)
        self.assertTrue(self.importer._raw_data.all())

    def test_extract_data(self):
        self.dataset.import_from(self.importer)
        self.assertTrue(self.dataset.data.data.all())

    def test_data_has_all_points(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(int(self.importer._raw_data[2]),
                         len(self.dataset.data.data))

    def test_axis_exists_with_meaningful_values(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(int(self.importer._raw_data[2]),
                         len(self.dataset.data.axes[0].values))
        self.assertNotEqual(0, self.dataset.data.axes[0].values[0])


        import matplotlib.pyplot as plt
        plt.plot(self.dataset.data.axes[0].values,
                 self.dataset.data.data)
        plt.show()