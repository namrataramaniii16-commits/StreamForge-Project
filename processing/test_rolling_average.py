import unittest
from processing.rolling_average import calculate_average


class TestRollingAverage(unittest.TestCase):

    def test_average(self):
        self.assertEqual(calculate_average([10, 20, 30]), 20.0)

    def test_empty_list(self):
        self.assertEqual(calculate_average([]), 0)

    def test_decimal_average(self):
        self.assertEqual(calculate_average([10, 20, 25]), 18.33)

    def test_negative_numbers(self):
        self.assertEqual(calculate_average([-10, -20, -30]), -20.0)

    def test_single_value(self):
        self.assertEqual(calculate_average([50]), 50.0)


if __name__ == "__main__":
    unittest.main()