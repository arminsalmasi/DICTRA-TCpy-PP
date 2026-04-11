import unittest
import numpy as np

from dictra_analyzr.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        self.dl = DataLoader(".")

    def test_find_nearest_exact_match(self):
        idx, val = self.dl._find_nearest([1.0, 2.0, 3.0], 2.0)
        self.assertEqual(idx, 1)
        self.assertEqual(val, 2.0)

    def test_find_nearest_closest_match(self):
        idx, val = self.dl._find_nearest([10.0, 20.0, 30.0], 21.0)
        self.assertEqual(idx, 1)
        self.assertEqual(val, 20.0)

    def test_find_nearest_edge_case_smaller(self):
        idx, val = self.dl._find_nearest([10.0, 20.0, 30.0], 5.0)
        self.assertEqual(idx, 0)
        self.assertEqual(val, 10.0)

    def test_find_nearest_edge_case_larger(self):
        idx, val = self.dl._find_nearest([10.0, 20.0, 30.0], 35.0)
        self.assertEqual(idx, 2)
        self.assertEqual(val, 30.0)

if __name__ == '__main__':
    unittest.main()
