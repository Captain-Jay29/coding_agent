import unittest
from calculator.calculator import Calculator

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_subtract(self):
        self.assertEqual(self.calc.subtract(5, 2), 3)

    def test_multiply(self):
        self.assertEqual(self.calc.multiply(3, 4), 12)

    def test_divide(self):
        self.assertEqual(self.calc.divide(10, 2), 5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError):
            self.calc.divide(5, 0)

    def test_modulo(self):
        self.assertEqual(self.calc.modulo(10, 3), 1)

    def test_modulo_by_zero(self):
        with self.assertRaises(ValueError):
            self.calc.modulo(5, 0)

if __name__ == '__main__':
    unittest.main()
