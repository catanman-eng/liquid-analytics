from typing import Callable
from controllers.helpers import Helper
from controllers.user_controller import UserController
from controllers.user_config_controller import UserConfigController
from controllers.book_controller import BookController
from datagolf_api import DataGolfAPI, Play
from rich.console import Console
from rich.text import Text
from typing import List


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
        self.book_controller = BookController(con)

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
                ev_percent decimal,
                UNIQUE (bet_name, event, sub_type)                  
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

    def get_matchup_plays(
        self, username, bet_type, ev_threshold: float, new: str = "n"
    ):
        if new == "n":
            new = False
        elif new == "y":
            new = True
        else:
            raise ValueError("Invalid input for new bets only. Please enter 'y' or 'n'")

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
            self.api.filter_by_book_matchup(
                username, matchup_response, "matchup", bet_type
            ),
            ev_threshold,
            user_config,
            bet_type,
        )

        if new:
            ev_filtered_response = self.filter_existing_bets(ev_filtered_response)

        if not ev_filtered_response:
            print("No new plays found.")
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

        self.add_bet_list(ev_filtered_response, username)

    @handle_database_errors
    def add_bet_list(self, bet_list: List[Play], username: str):
        user_id = self.user_controller.get_user_id(username)
        bet_ids = []
        for bet in bet_list:
            book_id = self.book_controller.get_book_id(bet.book)
            if self.check_bet_exists(bet.bet_desc, bet.event_name, bet.sub_market):
                continue
            bet_id = self.helper.generate_guid()
            bet_ids.append(bet_id)
            self.con.execute(
                """
                INSERT INTO bets (id, book_id, new, type, sub_type, book_odds, datagolf_odds, bet_name, event, kelly, ev_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (bet_name, event, sub_type)
                DO NOTHING
                """,
                [
                    bet_id,
                    book_id,
                    False,
                    bet.market,
                    bet.sub_market,
                    bet.odds,
                    bet.fair_odds,
                    bet.bet_desc,
                    bet.event_name,
                    float(bet.kelly.replace("u", "")),
                    bet.ev,
                ],
            )
        self.add_user_bets(user_id, bet_ids)

    @handle_database_errors
    def get_all_bets(self):
        return self.con.sql("SELECT * FROM bets")

    @handle_database_errors
    def add_user_bets(self, user_id, bet_ids):
        for bet_id in bet_ids:
            self.con.execute("INSERT INTO user_bets VALUES (?, ?)", [bet_id, user_id])

    @handle_database_errors
    def get_user_bets(self, username):
        user_id = self.user_controller.get_user_id(username)
        result = self.con.execute(
            """
            SELECT b.bet_name, b.event, b.type, b.sub_type, b.book_odds, b.datagolf_odds, b.kelly, b.ev_percent
            FROM user_bets ub
            JOIN bets b ON ub.bet_id = b.id
            WHERE ub.user_id = ?
            """,
            [user_id],
        )

        return result.fetchdf()

    @handle_database_errors
    def get_bet(self, bet_name, event, sub_type):
        result = self.con.execute(
            """
                        SELECT * FROM bets 
                        WHERE bet_name = ?
                        and event = ? 
                        and sub_type = ?""",
            [bet_name, event, sub_type],
        )
        return result.fetchdf()

    @handle_database_errors
    def check_bet_exists(self, bet_name, event, sub_type):
        result = self.con.execute(
            """
                        SELECT * FROM bets 
                        WHERE bet_name = ?
                        and event = ? 
                        and sub_type = ?""",
            [bet_name, event, sub_type],
        )
        return len(result.fetchdf()) > 0

    def filter_existing_bets(self, ev_filtered_response):
        bets_to_check = {
            (play.bet_desc, play.event_name, play.sub_market)
            for play in ev_filtered_response
        }

        existing_bets = self.get_existing_bets(bets_to_check)

        existing_bets_set = set(existing_bets)

        filtered_response = [
            play
            for play in ev_filtered_response
            if (play.bet_desc, play.event_name, play.sub_market)
            not in existing_bets_set
        ]

        return filtered_response

    @handle_database_errors
    def get_existing_bets(self, bets_to_check):
        #get 2 bets here for smaller subset to test
        bets_list = list(bets_to_check)

        conditions = " OR ".join(
            ["(bet_name = ? AND event = ? AND sub_type = ?)"] * len(bets_list)
        )
        query = f"""
            SELECT bet_name, event, sub_type 
            FROM bets 
            WHERE {conditions}
        """
        query_values = [item for sublist in bets_list for item in sublist] 
        existing_bets = self.con.execute(query, query_values).fetchall()
    
        return existing_bets
