import os
import shutil
import tempfile
import unittest

import cwepr.dataset
import cwepr.io

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


@unittest.skip('outdated')
class TestBES3TImporterOld(unittest.TestCase):
    def test_import(self):
        source = os.path.join(ROOTPATH, 'testdata/test-bes3t-1D-fieldsweep')
        importer = cwepr.io.BES3TImporterOld(source=source)
        dataset = cwepr.dataset.ExperimentalDataset()
        dataset.import_from(importer)

    def test_import_with_extension(self):
        for extension in [".DSC", ".DTA", ".YGF"]:
            source = os.path.join(ROOTPATH,
                                  'testdata/test-bes3t-1D-fieldsweep' +
                                  extension)
            importer = cwepr.io.BES3TImporterOld(source=source)
            dataset = cwepr.dataset.ExperimentalDataset()
            dataset.import_from(importer)


class TestBES3TImporter(unittest.TestCase):
    def setUp(self):
        self.dataset = cwepr.dataset.ExperimentalDataset()

    def test_import_with_1D_dataset(self):
        source = os.path.join(ROOTPATH, 'testdata/test-bes3t-1D-fieldsweep.DSC')
        importer = cwepr.io.bes3t.BES3TImporter(source=source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.axes[0].unit)
        self.assertFalse(self.dataset.data.axes[1].unit)

    def test_import_gives_correct_units(self):
        source = os.path.join(ROOTPATH, 'testdata/BDPA-1DFieldSweep')
        importer = cwepr.io.bes3t.BES3TImporter(source=source)
        self.dataset.import_from(importer)
        self.assertAlmostEqual(0.6325,
                         self.dataset.metadata.bridge.power.value)
        self.assertEqual('mW',
                         self.dataset.metadata.bridge.power.unit)

        self.assertEqual('mT', self.dataset.metadata.magnetic_field.start.unit)
        self.assertEqual('mT',
                         self.dataset.metadata.magnetic_field.sweep_width.unit)
        self.assertTrue(self.dataset.data.axes[0].values[0] < 1000)

    def test_import_with_2D_dataset_powersweep(self):
        source = os.path.join(ROOTPATH, 'testdata/BDPA-2DFieldPower.DSC')
        importer = cwepr.io.bes3t.BES3TImporter(source=source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.axes[0].unit)
        self.assertTrue(self.dataset.data.axes[1].unit)
        self.assertTrue(self.dataset.data.axes[1].quantity)

    def test_import_with_2D_dataset_fielddelay(self):
        source = os.path.join(ROOTPATH, 'testdata/BDPA-2DFieldDelay.DSC')
        importer = cwepr.io.bes3t.BES3TImporter(source=source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.data.axes[0].unit)
        self.assertTrue(self.dataset.data.axes[1].unit)

    def test_imports_infofile(self):
        source = os.path.join(ROOTPATH, 'testdata/BDPA-2DFieldDelay.DSC')
        importer = cwepr.io.bes3t.BES3TImporter(source=source)
        self.dataset.import_from(importer)
        self.assertTrue(self.dataset.metadata.measurement.operator)

    def test_import_with_no_infofile_continues(self):
        source = os.path.join(ROOTPATH, 'testdata/BDPA-2DFieldDelay')
        with tempfile.TemporaryDirectory() as testdir:
            for extension in ('.DSC', '.DTA', '.YGF'):
                new_source = os.path.join(testdir, 'test-wo_infofile')
                shutil.copyfile(source + extension, new_source + extension)
            dataset = cwepr.dataset.ExperimentalDataset()
            importer = cwepr.io.bes3t.BES3TImporter(
                source=new_source)
            dataset.import_from(importer)
