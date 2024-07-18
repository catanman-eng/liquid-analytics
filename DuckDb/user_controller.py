from typing import Callable
import uuid

def handle_database_errors(func: Callable[..., any]) -> Callable[..., any]:
    def wrapper(*args, **kwargs) -> any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Database error in {func.__name__}: {str(e)}")
    return wrapper

class UserController:
  def __init__(self, con):
    self.con = con
    self.create_users_table()

  def generate_guid(self):
    return str(uuid.uuid4())
  
  @handle_database_errors
  def create_users_table(self):
    self.con.execute("CREATE TABLE IF NOT EXISTS users (id VARCHAR PRIMARY KEY, username VARCHAR)")
  
  @handle_database_errors
  def check_user_exists(self, username):
    result = self.con.execute('SELECT * FROM users WHERE username = ?',[username])
    return len(result.fetchdf()) > 0
  
  @handle_database_errors
  def add_user(self, username):
    if not self.check_user_exists(username):
        user_id = self.generate_guid()
        self.con.execute("INSERT INTO users VALUES (?, ?)", [user_id, username])
        print(f"User {username} added successfully")
        return True
    else:
        print(f"User {username} already exists")
        return False
  
  @handle_database_errors
  def remove_user(self, username):
      self.con.execute("DELETE FROM users WHERE username = ?",[username])
      print(f"User {username} removed successfully")

  @handle_database_errors
  def get_all_users(self):
    result = self.con.execute("SELECT * FROM users")
    return result.fetchdf()
  
  @handle_database_errors
  def update_username(self, old_username, new_username):
    self.con.execute(f"UPDATE users SET username = '{new_username}' WHERE username = '{old_username}'")
  
  def logout(self):
    self.con.close()
    print("Logged out successfully")