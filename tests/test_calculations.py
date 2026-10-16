import unittest

from campus_cafe.calculations import calculate


class CalculateTests(unittest.TestCase):
    def test_evaluates_break_even_formula(self):
        self.assertAlmostEqual(calculate("24000 / (8 * (1 - .35 - .03))"), 4838.709677419355)
        self.assertEqual(calculate("ceil(24000 / (8 * (1 - .35 - .03)))"), 4839)

    def test_rejects_python_code(self):
        with self.assertRaises(ValueError):
            calculate("__import__('os').system('echo unsafe')")

    def test_rejects_large_exponents(self):
        with self.assertRaises(ValueError):
            calculate("2 ** 9")


if __name__ == "__main__":
    unittest.main()