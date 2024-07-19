import unittest
from controllers.book_controller import BookController
from controllers.user_controller import UserController
import duckdb


class TestBooksController(unittest.TestCase):
    def setUp(self) -> None:
        self.con = duckdb.connect(":memory:")
        self.book_controller = BookController(self.con)
        self.user_controller = UserController(self.con)

    def tearDown(self) -> None:
        return self.con.close()

    def test_init(self):
        result = self.con.execute("SELECT * FROM books")
        self.assertEqual(len(result.fetchdf()), 4)

    def test_add_book(self):
        self.book_controller.add_book("test_book")
        self.assertTrue(self.book_controller.check_book_exists("test_book"))

    def test_add_book_to_user(self):
        self.book_controller.add_book("test_book")
        self.book_controller.user_controller.add_user("test_user")
        self.book_controller.add_book_to_user("test_book", "test_user")

        result = self.con.execute("SELECT * FROM books_users")
        fetched_df = result.fetchdf()

        self.assertEqual(
            fetched_df.iloc[0]["book_id"], self.book_controller.get_book_id("test_book")
        )
        self.assertEqual(
            fetched_df.iloc[0]["user_id"], self.user_controller.get_user_id("test_user")
        )

    def test_remove_book_from_user(self):
        self.book_controller.add_book("test_book")
        self.book_controller.user_controller.add_user("test_user")
        self.book_controller.add_book_to_user("test_book", "test_user")
        self.book_controller.remove_book_from_user("test_book", "test_user")
        result = self.con.execute("SELECT * FROM books_users")
        self.assertEqual(len(result.fetchdf()), 0)


if __name__ == "__main__":
    unittest.main()
