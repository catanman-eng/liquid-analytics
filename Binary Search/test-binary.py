import helpers
import unittest

class TestCalculations(unittest.TestCase):
  
  @classmethod
  def setUp(self) -> None:
    self.array = [1, 3, 5, 7, 9]

  def test_empty_array(self):
    array = []
    target = 5
    self.assertEqual(helpers.binary_search(target, array), -1) 

  def test_target_not_in_array(self):
    target = 6
    self.assertEqual(helpers.binary_search(target, self.array), -1)

  def test_target_at_end_of_array(self):
    target = 9
    self.assertEqual(helpers.binary_search(target, self.array), 4)
  
  def test_target_at_start_of_array(self):  
    target = 1
    self.assertEqual(helpers.binary_search(target, self.array), 0)

  def test_target_at_middle_of_array(self):
    target = 5
    self.assertEqual(helpers.binary_search(target, self.array), 2)

  def test_same_value_array(self):
      array = [1, 1, 1, 1, 1]
      target = 1
      self.assertEqual(helpers.binary_search(target, array), 2)

if __name__ == '__main__':
  unittest.main()