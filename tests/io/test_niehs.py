import unittest
import os

import cwepr.io.niehs
import cwepr.dataset


ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestNIEHSDatImporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, "testdata/Pyrene")
        self.importer = cwepr.io.niehs.NIEHSDatImporter(source=source)
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
        self.assertEqual(
            int(self.importer._raw_data[2]), len(self.dataset.data.data)
        )

    def test_axis_exists_with_meaningful_values(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(
            int(self.importer._raw_data[2]),
            len(self.dataset.data.axes[0].values),
        )
        self.assertNotEqual(0, self.dataset.data.axes[0].values[0])

    def test_axis_has_unit(self):
        self.dataset.import_from(self.importer)
        self.assertEqual("mT", self.dataset.data.axes[0].unit)

    def test_metadata_points(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(
            int, type(self.dataset.metadata.magnetic_field.points)
        )
        self.assertNotEqual(0, self.dataset.metadata.magnetic_field.points)

    def test_metadata_magnetic_field(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(
            "mT", self.dataset.metadata.magnetic_field.start.unit
        )
        self.assertNotEqual(
            0, self.dataset.metadata.magnetic_field.start.value
        )


class TestNIEHSLmbImporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(ROOTPATH, "testdata/dmpo")
        self.importer = cwepr.io.niehs.NIEHSLmbImporter(source=source)
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_class_exists(self):
        pass

    def test_extract_data(self):
        self.dataset.import_from(self.importer)
        self.assertTrue(self.dataset.data.data.all())
        self.assertGreater(len(self.dataset.data.data), 0)

        # import matplotlib.pyplot as plt
        # plt.plot(self.dataset.data.data)
        # plt.show()

    def test_axis_exists_with_meaningful_values(self):
        self.dataset.import_from(self.importer)
        self.assertEqual(
            len(self.dataset.data.data), len(self.dataset.data.axes[0].values)
        )
        self.assertTrue(self.dataset.data.axes[0].values.all())

    def test_axis_has_unit(self):
        self.dataset.import_from(self.importer)
        self.assertEqual("mT", self.dataset.data.axes[0].unit)

    def test_assign_comment(self):
        self.dataset.import_from(self.importer)
        self.assertTrue(
            self.dataset.annotations[0].annotation.content["comment"]
        )

    def test_assign_basic_metadata(self):
        self.dataset.import_from(self.importer)
        metadata = self.dataset.metadata
        self.assertTrue(metadata.magnetic_field.start.value)
        self.assertTrue(metadata.magnetic_field.start.unit)
        self.assertTrue(metadata.magnetic_field.stop.value)
        self.assertTrue(metadata.magnetic_field.stop.unit)
        self.assertTrue(metadata.magnetic_field.sweep_width.value)
        self.assertTrue(metadata.magnetic_field.sweep_width.unit)
        self.assertGreater(metadata.signal_channel.accumulations, 0)


class TestNIEHSExpImporter(unittest.TestCase):
    def setUp(self):
        self.dsv_source = os.path.join(ROOTPATH, "testdata/pow128")
        self.block_source = os.path.join(ROOTPATH, "testdata/e1-05")
        self.importer = cwepr.io.niehs.NIEHSExpImporter()
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_class_exists(self):
        pass

    def test_extract_data_with_pure_dsv_file(self):
        self.importer.source = self.dsv_source
        self.dataset.import_from(self.importer)
        self.assertTrue(self.dataset.data.data.all())
        self.assertGreater(len(self.dataset.data.data), 0)

        # import matplotlib.pyplot as plt
        # plt.plot(self.dataset.data.data)
        # plt.show()

    def test_extract_data_with_block_file(self):
        self.importer.source = self.block_source
        self.dataset.import_from(self.importer)
        self.assertTrue(self.dataset.data.data.all())
        self.assertGreater(len(self.dataset.data.data), 0)

        # import matplotlib.pyplot as plt
        # plt.plot(self.dataset.data.data)
        # plt.show()

    def test_axis_exists_with_meaningful_values(self):
        self.importer.source = self.block_source
        self.dataset.import_from(self.importer)
        self.assertEqual(
            len(self.dataset.data.data), len(self.dataset.data.axes[0].values)
        )
        self.assertTrue(self.dataset.data.axes[0].values.all())

    def test_axis_has_unit(self):
        self.importer.source = self.block_source
        self.dataset.import_from(self.importer)
        self.assertEqual("mT", self.dataset.data.axes[0].unit)

    def test_assign_comment(self):
        self.importer.source = self.block_source
        self.dataset.import_from(self.importer)
        self.assertTrue(
            self.dataset.annotations[0].annotation.content["comment"]
        )
