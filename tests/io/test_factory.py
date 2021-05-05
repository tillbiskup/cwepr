import unittest
import os

import cwepr.io.errors
import cwepr.dataset

ROOTPATH = os.path.split(os.path.abspath(__file__))[0]


class TestDatasetImporterFactory(unittest.TestCase):
    def test_error_message_no_matching_file_pair(self):
        source = os.path.join(ROOTPATH, 'testdata',
                              'test-magnettech.xml').replace('xml', 'test')
        importer = cwepr.dataset.DatasetFactory()
        with self.assertRaises(cwepr.io.errors.NoMatchingFilePairError) as error:
            dataset = importer.get_dataset(source=source)
        self.assertIn('No file format was found', error.exception.message)



if __name__ == '__main__':
    unittest.main()
