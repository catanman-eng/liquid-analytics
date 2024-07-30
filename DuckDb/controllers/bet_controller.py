from typing import Callable
from controllers.helpers import Helper
from controllers.user_controller import UserController
from controllers.user_config_controller import UserConfigController
from datagolf_api import DataGolfAPI
from rich.console import Console
from rich.text import Text


def handle_database_errors(func: Callable[..., any]) -> Callable[..., any]:
    def wrapper(*args, **kwargs) -> any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Database error in {func.__name__}: {str(e)}")

    return wrapper


OUTRIGHT_BET_TYPES = ["win", "top_5", "top_10", "top_20", "mc", "make_cut", "frl"]

# Define color mapping for books
BOOK_COLORS = {"fanduel": "blue"}


class BetController:
    def __init__(self, con, api: DataGolfAPI):
        self.con = con
        self.user_controller = UserController(con)
        self.user_config_controller = UserConfigController(con)
        self.helper = Helper()
        self.api = api

        # table setup
        self.create_bets_table()
        self.create_user_bets_table()

    # Table Creation
    @handle_database_errors
    def create_bets_table(self):
        self.con.execute("""
              CREATE TABLE IF NOT EXISTS bets(
                id VARCHAR PRIMARY KEY,
                book_id VARCHAR,
                new BOOLEAN,
                type VARCHAR,
                sub_type VARCHAR,
                book_odds VARCHAR,
                datagolf_odds VARCHAR,
                bet_name VARCHAR,
                event VARCHAR,
                kelly decimal,
                ev_percent decimal                   
              )
          """)

    @handle_database_errors
    def create_user_bets_table(self):
        self.con.execute("""
              CREATE TABLE IF NOT EXISTS user_bets(
                bet_id VARCHAR, 
                user_id VARCHAR,
                PRIMARY KEY (bet_id, user_id),
                FOREIGN KEY (bet_id) REFERENCES bets(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
              )
          """)

    # api actions
    def get_outright_plays(self, username, bet_type, ev_threshold: float):
        if bet_type not in OUTRIGHT_BET_TYPES:
            raise ValueError(
                f"Bet type {bet_type} not supported.\nSupported types: {OUTRIGHT_BET_TYPES}"
            )
        if ev_threshold < 0 or ev_threshold > 1:
            raise ValueError("EV threshold must be between 0 and 1")

        if not isinstance(ev_threshold, float):
            raise ValueError("EV threshold must be a float")

        user_config = self.user_config_controller.get_user_config(username)

        outright_response = self.api.get_outright_odds(bet_type)
        ev_filtered_response = self.api.filter_by_ev(
            self.api.filter_by_book(username, outright_response, "outright"),
            ev_threshold,
            user_config,
        )

        console = Console()
        formatted_output = ""

        for play in ev_filtered_response:
            formatted_output += f"{'-'*40}\n"  # Separator line for readability

            for key, value in play.model_dump().items():
                formatted_value = Text(str(value))
                formatted_output += (
                    f"{key.replace('_', ' ').title()}: {formatted_value}\n"
                )
            formatted_output += f"{'-'*40}\n"  # Separator line for readability
        console.print(formatted_output)
