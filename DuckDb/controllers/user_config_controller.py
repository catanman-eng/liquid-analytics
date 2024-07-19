from typing import Callable
from controllers.helpers import Helper


def handle_database_errors(func: Callable[..., any]) -> Callable[..., any]:
    def wrapper(*args, **kwargs) -> any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Database error in {func.__name__}: {str(e)}")

    return wrapper


class UserConfigController:
    def __init__(self, con):
        self.con = con
        self.utils = Helper()
        self.create_user_config_table()

    @handle_database_errors
    def create_config_table(self):
        self.con.execute("""
              CREATE TABLE IF NOT EXISTS config(
                id VARCHAR PRIMARY KEY,
                name VARCHAR
              )
          """)
        
    @handle_database_errors
    def create_user_config_table(self):
        self.con.execute("""
              CREATE TABLE IF NOT EXISTS user_config(
                user_id VARCHAR, 
                config_id VARCHAR,
                PRIMARY KEY (config_id, user_id),
                FOREIGN KEY (config_id) REFERENCES config(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
              )
          """)
