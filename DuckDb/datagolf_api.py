import requests
from db_manager import DBManager
from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.helpers import Helper
from typing import List
from pydantic import BaseModel


class OutrightPlay(BaseModel):
    book: str
    player_name: str
    ev: float
    odds: str
    market: str
    sub_market: str
    event_name: str


class DataGolfAPI:
    def __init__(self, api_key, con, db_manager: DBManager):
        self.api_key = api_key
        self.base_url = "https://feeds.datagolf.com"
        self.con = con
        self.db_manager = db_manager
        self.user_controller = UserController(con)
        self.book_controller = BookController(con)
        self.helper = Helper()

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
        url = f"{self.base_url}/betting-tools/outrights?&market={market}&odds_format=american&key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response

    def filter_by_book(self, username, outright_response, market=None):
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
            "bet_type": market,
            "sub_bet_type": odds_data.get("market"),
            "notes": odds_data.get("notes"),
            "odds": filtered_odds_list,
        }

        return result

    def filter_by_ev(self, odds_list, ev_threshold) -> List[OutrightPlay]:
        odds = odds_list["odds"]

        if not odds:
            print("No odds found.")
            return []

        filtered_plays = []
        always_keep_keys = ["datagolf", "player_name"]

        for odd in odds:
            filtered_odd = {
                key: value for key, value in odd.items() if key in always_keep_keys
            }

            for key, value in odd.items():
                if key not in always_keep_keys:
                    try:
                        ev = self.helper.ev(
                            float(value.replace("+", "")),
                            float(
                                odd["datagolf"]["baseline_history_fit"].replace("+", "")
                            ),
                        )
                    except AttributeError:
                        print(f"Error calculating EV for {odd['player_name']}")
                        ev = 0

                    if ev > ev_threshold:
                        filtered_odd[key] = value

                        bet = OutrightPlay(
                            event_name=odds_list["event_name"],
                            player_name=filtered_odd["player_name"],
                            market=odds_list["bet_type"],
                            sub_market=odds_list["sub_bet_type"],
                            book=key,
                            odds=value,
                            ev=ev * 100,
                        )
                        filtered_plays.append(bet)
        
        filtered_plays.sort(key=lambda x: x.ev, reverse=True)

        return filtered_plays
