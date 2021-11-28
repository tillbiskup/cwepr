import unittest

import numpy as np

from cwepr import utils


class TestConvertmT2g(unittest.TestCase):

    def test_values_are_positive(self):
        values = np.linspace(340, 350, 100)
        mw_freq = 9.5
        self.assertTrue(all(utils.convert_mT2g(values, mw_freq) > 0))

    def test_values_have_correct_range(self):
        values = np.linspace(340, 350, 100)
        mw_freq = 9.5
        condition = \
            (np.floor(np.log10(utils.convert_mT2g(values, mw_freq))) == 0)
        self.assertTrue(all(condition))


class TestConvertg2mT(unittest.TestCase):

    def test_values_are_positive(self):
        values = np.linspace(1.8, 4, 100)
        mw_freq = 9.5
        self.assertTrue(all(utils.convert_mT2g(values, mw_freq) > 0))

    def test_values_have_correct_range(self):
        values = np.linspace(1.8, 4, 100)
        mw_freq = 9.5
        condition = \
            (np.floor(np.log10(utils.convert_g2mT(values, mw_freq))) == 2)
        self.assertTrue(all(condition))


class TestNotZero(unittest.TestCase):

    def test_not_zero_of_zero_returns_nonzero_value(self):
        self.assertGreater(utils.not_zero(0), 0)

    def test_not_zero_of_zero_returns_np_float_resolution(self):
        self.assertEqual(np.finfo(np.float64).resolution,
                         utils.not_zero(0))

    def test_not_zero_of_positive_value_preserves_sign(self):
        self.assertGreater(utils.not_zero(1e-20), 0)

    def test_not_zero_of_negative_value_preserves_sign(self):
        self.assertLess(utils.not_zero(-1e-20), 0)

    def test_not_zero_of_negative_value_closer_than_limit_returns_limit(self):
        self.assertEqual(-np.finfo(np.float64).resolution,
                         utils.not_zero(-1e-20))
