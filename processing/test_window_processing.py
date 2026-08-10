import unittest

from processing.window_processing import add_temperature, window


class TestWindowProcessing(unittest.TestCase):

    def setUp(self):
        window.clear()

    def test_first_temperature(self):
        current_window, average = add_temperature(10)
        self.assertEqual(current_window, [10])
        self.assertEqual(average, 10.0)

    def test_window_average(self):
        add_temperature(10)
        add_temperature(20)
        current_window, average = add_temperature(30)

        self.assertEqual(current_window, [10, 20, 30])
        self.assertEqual(average, 20.0)

    def test_window_removes_oldest(self):
        add_temperature(10)
        add_temperature(20)
        add_temperature(30)

        current_window, average = add_temperature(40)

        self.assertEqual(current_window, [20, 30, 40])
        self.assertEqual(average, 30.0)


if __name__ == "__main__":
    unittest.main()