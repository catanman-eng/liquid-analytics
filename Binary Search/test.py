import helpers
import unittest

class TestCalculations(unittest.TestCase):

  def test_binary_base(self):
    array = [1, 3, 5, 7, 9]
    target = 5
    self.assertEqual(helpers.binary_search(target, array), 2)

if __name__ == '__main__':
  unittest.main()