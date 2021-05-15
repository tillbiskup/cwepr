import glob
import os
import unittest
import aspecd.tasks
import aspecd.processing
import cwepr.analysis
import cwepr.dataset
import cwepr.processing
import cwepr.report

TEST_ROOTPATH = os.path.split(os.path.abspath(__file__))[0]
MODULE_ROOTPATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print(MODULE_ROOTPATH)

class TestExperimentalDatasetLaTeXReporter(unittest.TestCase):
    def setUp(self):
        source = os.path.join(TEST_ROOTPATH, "io/testdata/test-bes3t-1D-fieldsweep")
        factory = cwepr.dataset.DatasetFactory()
        self.dataset = factory.get_dataset(source=source)
        analysator = cwepr.analysis.Amplitude()
        self.dataset.analyse(analysator)
        algebra = aspecd.processing.ScalarAlgebra()
        algebra.parameters['kind'] = '+'
        algebra.parameters['value'] = 10
        algebra.comment = 'Does this show up in the report?'
        self.dataset.process(algebra)
        self.filename = 'test.tex'
        template_ = os.path.join(
            MODULE_ROOTPATH, 'templates', 'de', 'report.tex.jinja')
        self.reporter = \
            cwepr.report.ExperimentalDatasetLaTeXReporter(template=template_,
                                                          filename=self.filename)
        self.reporter.context['dataset'] = self.dataset.to_dict()
        self.reporter.dataset = self.dataset

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.filename.replace('tex', 'pdf')):
            os.remove(self.filename.replace('tex', 'pdf'))

    def test_get_tasks(self):
        self.reporter._get_tasks_recursively(self.dataset)

    def test_reporter(self):
        self.reporter.create()
        #self.reporter.compile()


class TestPowerSweepAnalysisReport(unittest.TestCase):
    def setUp(self):
        self.recipe_filename = \
            os.path.join(TEST_ROOTPATH, 'io/testdata/power-sweep-analysis.yaml')
        self.filename = 'PowerSweepReport.tex'
        self.filename2 = 'PowerSweepAnalysis.pdf'
        template_ = os.path.join(
            MODULE_ROOTPATH, 'templates', 'de', 'power_sweep_report.tex.jinja')
        self.reporter = \
            cwepr.report.PowerSweepAnalysisReporter(template=template_,
                                                    filename=self.filename)
        self.chef = aspecd.tasks.ChefDeService()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)
        for path in glob.glob(self.recipe_filename.replace('.yaml', '-*.yaml')):
            os.remove(path)
        if os.path.exists(self.filename2):
            os.remove(self.filename2)
        #if os.path.exists(self.filename.replace('tex', 'pdf')):
         #   os.remove(self.filename.replace('tex', 'pdf'))

    def test_reporter(self):
        self.chef.serve(recipe_filename=self.recipe_filename)


class TestDokuwikiCaptionsReporter(unittest.TestCase):
    def setUp(self):
        self.filename = 'Dokuwiki-caption.txt'
        self.template_ = os.path.join(
            MODULE_ROOTPATH, 'templates', 'en', 'DokuwikiCaption.txt.jinja')
        self.reporter = cwepr.report.DokuwikiCaptionsReporter()
        self.dataset = cwepr.dataset.ExperimentalDataset()
        source = \
            os.path.join(TEST_ROOTPATH, "io/testdata/test-bes3t-1D-fieldsweep")
        factory = cwepr.dataset.DatasetFactory()
        self.dataset = factory.get_dataset(source=source)
        self.reporter.context['dataset'] = self.dataset.to_dict()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_reporter(self):
        self.reporter.filename = self.filename
        self.reporter.template = self.template_
        self.reporter.create()
        self.assertTrue(os.path.exists(self.filename))

    def test_reporter_without_template(self):
        self.reporter.filename = self.filename
        self.reporter.create()
        self.assertTrue(os.path.exists(self.filename))
