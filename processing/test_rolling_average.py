import unittest
from processing.rolling_average import calculate_average


class TestRollingAverage(unittest.TestCase):

    def test_average(self):
        self.assertEqual(calculate_average([10, 20, 30]), 20.0)

    def test_empty_list(self):
        self.assertEqual(calculate_average([]), 0)

    def test_decimal_average(self):
        self.assertEqual(calculate_average([10, 20, 25]), 18.33)


if __name__ == "__main__":
    unittest.main()