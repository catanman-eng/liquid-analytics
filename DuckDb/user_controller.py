class UserController:
  def __init__(self, con):
    self.con = con
    self.create_users_table()

  def create_users_table(self):
    self.con.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR)")
  
  def check_user_exists(self, username):
    result = self.con.execute(f"SELECT * FROM users WHERE username = '{username}'")
    return len(result.fetchdf()) > 0
  
  def add_user(self, username):
    if not self.check_user_exists(username):
      self.con.execute(f"INSERT INTO users VALUES ('{username}')")
      return True
    else:
      print(f"User {username} already exists")
    return False
  
  def remove_user(self, username):
    self.con.execute(f"DELETE FROM users WHERE username = '{username}'")
  
  def get_all_users(self):
    result = self.con.execute("SELECT * FROM users")
    return result.fetchdf()
  
  def update_username(self, old_username, new_username):
    self.con.execute(f"UPDATE users SET username = '{new_username}' WHERE username = '{old_username}'")
  
  def logout(self):
    self.con.close()
    print("Logged out successfully")