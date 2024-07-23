import requests
from db_manager import DBManager
from controllers.user_controller import UserController
from controllers.book_controller import BookController


class DataGolfAPI:
    def __init__(self, api_key, con, db_manager: DBManager):
        self.api_key = api_key
        self.base_url = "https://feeds.datagolf.com"
        self.con = con
        self.db_manager = db_manager
        self.user_controller = UserController(con)
        self.book_controller = BookController(con)

        self.create_players_table()

    def fetch_players_data(self):
        url = f"{self.base_url}/get-player-list?file_format=json&key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response

    def create_players_table(self):
        data = self.fetch_players_data()

        self.db_manager.create_table("players", data)

    def get_outright_odds(self, market):
        url = f"{self.base_url}/betting-tools/outrights?&market={market}&key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response

    def filter_by_book(self, username, outright_response):
        odds_data = outright_response.json()

        odds_list = odds_data.get("odds", [])
        user_books = self.book_controller.get_user_books(username)

        books_list = user_books["Book"].tolist()

        always_keep_keys = ["datagolf", "player_name"]

        filtered_odds_list = [
            {
                **{key: value for key, value in odds_dict.items() if key in books_list},
                **{key: odds_dict[key] for key in always_keep_keys if key in odds_dict},
            }
            for odds_dict in odds_list
            if (
                "datagolf" in odds_dict
                and (
                    odds_dict["datagolf"].get("baseline_history_fit") is not None
                    or odds_dict["datagolf"].get("baseline") is not None
                )
            )
        ]

        result = {
            "books_offering": books_list,
            "event_name": odds_data.get("event_name"),
            "last_updated": odds_data.get("last_updated"),
            "market": odds_data.get("market"),
            "notes": odds_data.get("notes"),
            "odds": filtered_odds_list,
        }

        print(result)
