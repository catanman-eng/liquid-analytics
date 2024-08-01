from typing import Callable
from controllers.helpers import Helper
from controllers.user_controller import UserController
from pydantic import BaseModel
import uuid


class UserConfig(BaseModel):
    user_id: uuid.UUID
    kelly_multiplier: float
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
                id VARCHAR PRIMARY KEY,
                kelly_multiplyer DOUBLE,
                bankroll INTEGER
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
        user = self.user_controller.get_user(user_id)

        result = self.con.execute(
            "SELECT * FROM user_config WHERE id = ?", [user.config_id]
        )

        record = result.fetchone()
        if record:
            config = UserConfig(
                user_id=user_id, kelly_multiplier=record[1], bankroll=record[2]
            )
        else:
            print(f"User {username} has no config")
            return None
        
        return config

    @handle_database_errors
    def update_user_config(self, username, kelly_multiplier, bankroll):
        user_id = self.user_controller.get_user_id(username)
        user = self.user_controller.get_user(user_id)

        if not user:
            print(f"User '{username}' not found.")
            return

        config = UserConfig(
            user_id=user.id, kelly_multiplier=kelly_multiplier, bankroll=bankroll
        )

        if user.config_id is not None:
            print(f"Updating config for user {username}")
            self.con.execute(
                "UPDATE user_config SET kelly_multiplyer = ?, bankroll = ? WHERE id = ?",
                [config.kelly_multiplyer, config.bankroll, user.config_id],
            )
        else:
            print(f"Creating new config for user {username}")
            new_id = self.utils.generate_guid()

            self.con.execute(
                "INSERT INTO user_config VALUES (?, ?, ?)",
                [new_id, config.kelly_multiplyer, config.bankroll],
            )

            self.con.execute(
                "UPDATE users SET config_id = ? WHERE id = ?", [new_id, user.id]
            )

        print(f"Config updated for user {username} successfully")
