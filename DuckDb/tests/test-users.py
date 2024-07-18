import unittest
from user_controller import UserController
import duckdb

class TestUserController(unittest.TestCase):
    def setUp(self) -> None:
        self.con = duckdb.connect(":memory:")
        self.user_controller = UserController(self.con)

    def tearDown(self) -> None:
        return self.con.close()
    
    def test_add_user(self):
        self.user_controller.add_user("test_user")
        self.assertTrue(self.user_controller.check_user_exists("test_user"))
    
    def test_modify_user(self):
        self.user_controller.add_user("test_user")
        self.user_controller.update_username("test_user", "new_user")
        self.assertTrue(self.user_controller.check_user_exists("new_user"))

    def test_remove_user(self):
        self.user_controller.add_user("test_user")
        self.user_controller.remove_user("test_user")
        self.assertFalse(self.user_controller.check_user_exists("test_user"))

if __name__ == "__main__":
    unittest.main()