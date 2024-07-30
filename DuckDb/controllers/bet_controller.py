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
MATCHUP_BET_TYPES = ["tournament_matchups", "round_matchups", "3_balls"]

# Define color mapping for books
BOOK_COLORS = {
    "fanduel": "blue",
    "draftkings": "bright green",
    "caesars": "gold1",
    "bet365": "green",
}


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
        for play in ev_filtered_response:
            # Separator line for readability
            separator = Text("-" * 40, style="bold yellow")
            console.print(separator)

            for key, value in play.model_dump().items():
                key_text = Text(
                    f"{key.replace('_', ' ').title()}: ", style="bold white"
                )
                if key == "book":
                    # Determine the color based on the book
                    book_color = BOOK_COLORS.get(
                        value, "white"
                    )  # Default to white if book not found
                    formatted_value = Text(str(value).title(), style=f"{book_color}")
                elif key == "ev":
                    formatted_value = Text(f"{value:.2f}%", style="green")
                else:
                    formatted_value = Text(str(value).title(), style="white")

                console.print(key_text, formatted_value)

            console.print(separator)

    def get_matchup_plays(self, username, bet_type, ev_threshold: float):
        if bet_type not in MATCHUP_BET_TYPES:
            raise ValueError(
                f"Bet type {bet_type} not supported.\nSupported types: {MATCHUP_BET_TYPES}"
            )

        if ev_threshold < 0 or ev_threshold > 1:
            raise ValueError("EV threshold must be between 0 and 1")

        if not isinstance(ev_threshold, float):
            raise ValueError("EV threshold must be a float")

        user_config = self.user_config_controller.get_user_config(username)
        matchup_response = self.api.get_matchup_odds(bet_type)
        
        if "offered" in matchup_response["match_list"]:
            print(matchup_response["match_list"])
            return
        
        ev_filtered_response = self.api.filter_by_ev_matchup(
            self.api.filter_by_book_matchup(username, matchup_response, "matchup"),
            ev_threshold,
            user_config,
        )

        console = Console()
        for play in ev_filtered_response:
            separator = Text("-" * 40, style="bold yellow")
            console.print(separator)

            for key, value in play.model_dump().items():
                key_text = Text(
                    f"{key.replace('_', ' ').title()}: ", style="bold white"
                )
                if key == "book":
                    book_color = BOOK_COLORS.get(value, "white")
                    formatted_value = Text(str(value).title(), style=f"{book_color}")
                elif key == "ev":
                    formatted_value = Text(f"{value:.2f}%", style="green")
                else:
                    formatted_value = Text(str(value).title(), style="white")

                console.print(key_text, formatted_value)

            console.print(separator)
