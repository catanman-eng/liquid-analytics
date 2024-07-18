from typing import Callable
from controllers.helpers import Helper
from controllers.user_controller import UserController

def handle_database_errors(func: Callable[..., any]) -> Callable[..., any]:
    def wrapper(*args, **kwargs) -> any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Database error in {func.__name__}: {str(e)}")

    return wrapper

class BookController:
    def __init__(self, con):
        self.con = con
        self.sportsbooks = ["bet365", "caesars", "draftkings", "fanduel"]
        self.user_controller = UserController(con)
        self.helper = Helper()
        
        self.create_books_table()
        self.create_books_user_table()

    @handle_database_errors
    def create_books_user_table(self):
        self.con.execute("""
              CREATE TABLE IF NOT EXISTS books_users(
                book_id VARCHAR, 
                user_id VARCHAR,
                PRIMARY KEY (book_id, user_id),
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
              )
          """)

    @handle_database_errors
    def get_book_id(self, book_name):
        result = self.con.execute("SELECT id FROM books WHERE name = ?", [book_name])
        return result.fetchdf().iloc[0]['id']
    
    @handle_database_errors
    def add_book_to_user(self, book_name, username):
        book_id = self.get_book_id(book_name)
        user_id = self.user_controller.get_user_id(username)
        self.con.execute("INSERT INTO books_users VALUES (?, ?)", [book_id, user_id])
        print(f"Book {book_name} added to user {user_id} successfully")

    @handle_database_errors
    def remove_book_from_user(self, book_name, username):
        book_id = self.get_book_id(book_name)
        user_id = self.user_controller.get_user_id(username)
        self.con.execute("DELETE FROM books_users WHERE book_id = ? AND user_id = ?", [book_id, user_id])
        print(f"Book {book_name} removed from user {user_id} successfully")
        
    @handle_database_errors
    def create_books_table(self):
        self.con.execute("CREATE TABLE IF NOT EXISTS books (id VARCHAR PRIMARY KEY, name VARCHAR)")
        for book in self.sportsbooks:
            self.add_book(book)

    @handle_database_errors
    def add_book(self, name):
        if self.check_book_exists(name):
          return
        book_id = self.helper.generate_guid()
        self.con.execute("INSERT INTO books VALUES (?, ?)", [book_id, name])
    
    @handle_database_errors
    def check_book_exists(self, name):
        result = self.con.execute('SELECT * FROM books WHERE name = ?',[name])
        return len(result.fetchdf()) > 0
  
    @handle_database_errors
    def get_all_books(self):
        result = self.con.execute("SELECT * FROM books")
        return result.fetchdf()