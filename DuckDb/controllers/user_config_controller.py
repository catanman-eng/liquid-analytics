from typing import Callable
from controllers.helpers import Helper
from controllers.user_controller import UserController
from pydantic import BaseModel


class UserConfig(BaseModel):
    user_id: str
    kelly_multiplyer: float
    bankroll: int


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
        self.config = ["kelly_multiplyer", "bankroll"]
        self.create_user_config_table()
        self.user_controller = UserController(con)

    @handle_database_errors
    def create_user_config_table(self):
        self.con.execute("""
              CREATE TABLE IF NOT EXISTS user_config(
                user_id VARCHAR PRIMARY KEY,
                kelly_multiplyer DOUBLE,
                bankroll INTEGER
                FOREIGN KEY (user_id) REFERENCES users(id)
              )
          """)

    @handle_database_errors
    def check_config_exists(self, username):
        user_id = self.user_controller.get_user_id(username)
        result = self.con.execute(
            "SELECT * FROM user_config WHERE user_id = ?", [user_id]
        )
        return len(result.fetchdf()) > 0

    @handle_database_errors
    def get_all_configs(self):
        return self.con.sql("SELECT * FROM user_config")

    @handle_database_errors
    def get_user_config(self, username):
        user_id = self.user_controller.get_user_id(username)
        result = self.con.execute(
            "SELECT * FROM user_config WHERE user_id = ?", [user_id]
        )
        return result.fetchdf()

    @handle_database_errors
    def add_user_config(self, username, kelly_multiplyer, bankroll):
        user_id = self.user_controller.get_user_id(username)

        config = UserConfig(
            user_id=user_id, kelly_multiplyer=kelly_multiplyer, bankroll=bankroll
        )

        result = self.con.execute(
            "SELECT * FROM user_config WHERE user_id = ?", [config.user_id]
        )
        if len(result.fetchdf()) > 0:
            self.con.execute(
          "UPDATE user_config SET kelly_multiplyer = ?, bankroll = ? WHERE user_id = ?",
          [config.kelly_multiplyer, config.bankroll, config.user_id],
            )
        else:
            self.con.execute(
          "INSERT INTO user_config VALUES (?, ?, ?)",
          [config.user_id, config.kelly_multiplyer, config.bankroll],
            )
        print(f"Config updated for user {username} successfully")
