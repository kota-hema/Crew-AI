import unittest

from campus_cafe.dataset import load_student_spending


class StudentSpendingDatasetTests(unittest.TestCase):
    def test_loads_bundled_synthetic_sample(self):
        dataset = load_student_spending()
        self.assertEqual(len(dataset), 1000)
        self.assertIn("record_id", dataset.columns)
        self.assertIn("preferred_payment_method", dataset.columns)
        self.assertAlmostEqual(dataset["food"].mean(), 252.642)


if __name__ == "__main__":
    unittest.main()