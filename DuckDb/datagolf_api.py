import requests
from db_manager import DBManager
from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.user_config_controller import UserConfig
from controllers.helpers import Helper
from typing import List
from pydantic import BaseModel


class Play(BaseModel):
    book: str
    bet_desc: str
    market: str
    sub_market: str
    ev: float
    odds: str
    fair_odds: str
    kelly: str = "0u"
    bet_size: str = "$0"
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
        return response.json()

    def get_matchup_odds(self, market):
        url = f"{self.base_url}/betting-tools/matchups?&market={market}&odds_format=american&key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def filter_by_book(self, username, outright_response, market=None):
        odds_list = outright_response["odds"]
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
            "event_name": outright_response["event_name"],
            "last_updated": outright_response["last_updated"],
            "bet_type": market,
            "sub_bet_type": outright_response["market"],
            "odds": filtered_odds_list,
        }

        return result

    def filter_by_book_matchup(
        self,
        username,
        matchup_response,
        market,
        sub_market,
    ):
        matchup_list = matchup_response["match_list"]

        user_books = self.book_controller.get_user_books(username)
        books_list = user_books["Book"].tolist()
        print(sub_market)
        if sub_market == "tournament_matchups":
            always_keep_keys = ["datagolf", "ties", "p1_player_name", "p2_player_name"]
        elif sub_market == "3_balls":
            always_keep_keys = [
                "datagolf",
                "player_name",
                "p1_player_name",
                "p2_player_name",
                "p3_player_name",
                "round_num",
            ]
        elif sub_market == "round_matchups":
            always_keep_keys = [
                "datagolf",
                "player_name",
                "p1_player_name",
                "p2_player_name",
                "round_num",
            ]

        filtered_matchup_list = []
        for matchup_dict in matchup_list:
            odds_dict = matchup_dict["odds"]
            filtered_odds = {
                book: odds_dict[book] for book in books_list if book in odds_dict
            }

            if filtered_odds:
                always_keep_data = {
                    key: matchup_dict[key]
                    for key in always_keep_keys
                    if key in matchup_dict
                }
                datagolf_odds = odds_dict.get("datagolf", {})

                updated_filtered_odds = {**filtered_odds, "datagolf": datagolf_odds}

                filtered_matchup = {**always_keep_data, "odds": updated_filtered_odds}
                filtered_matchup_list.append(filtered_matchup)

        result = {
            "books_offering": books_list,
            "event_name": matchup_response["event_name"],
            "last_updated": matchup_response["last_updated"],
            "bet_type": market,
            "sub_bet_type": matchup_response["market"],
            "odds": filtered_matchup_list,
        }

        return result

    def filter_by_ev(self, odds_list, ev_threshold, config: UserConfig) -> List[Play]:
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
                        bet_odds = float(value.replace("+", ""))
                        fair_odds = float(
                            odd["datagolf"]["baseline_history_fit"].replace("+", "")
                        )
                        ev = self.helper.ev(bet_odds, fair_odds)
                    except AttributeError:
                        print(f"Error calculating EV for {odd['player_name']}")
                        ev = 0

                    if ev > ev_threshold:
                        filtered_odd[key] = value
                        kelly = round(
                            self.helper.kelly_stake(
                                bet_odds,
                                fair_odds,
                                config.kelly_multiplyer,
                            ),
                            2,
                        )
                        bet = Play(
                            event_name=odds_list["event_name"],
                            bet_desc=f"{filtered_odd['player_name']}: {odds_list['sub_bet_type'].title()}",
                            market=odds_list["bet_type"],
                            sub_market=odds_list["sub_bet_type"],
                            book=key,
                            fair_odds=fair_odds,
                            odds=value,
                            ev=round(ev * 100, 0),
                            kelly=f"{kelly}u",
                            bet_size=f"${kelly*(config.bankroll/100)}",
                        )
                        filtered_plays.append(bet)

        filtered_plays.sort(key=lambda x: x.ev, reverse=True)

        return filtered_plays

    def filter_by_ev_matchup(
        self, matchups, ev_threshold, config: UserConfig, market
    ) -> List[Play]:
        odds_list = matchups["odds"]
        filtered_plays = []

        for odds in odds_list:
            if not odds:
                print("No odds found.")
                return []

            if market == "tournament_matchups":
                always_keep_keys = [
                    "datagolf",
                    "ties",
                    "p1_player_name",
                    "p2_player_name",
                ]
            elif market == "3_balls":
                always_keep_keys = [
                    "datagolf",
                    "player_name",
                    "p1_player_name",
                    "p2_player_name",
                    "p3_player_name",
                    "round_num",
                ]
            elif market == "round_matchups":
                always_keep_keys = [
                    "datagolf",
                    "player_name",
                    "p1_player_name",
                    "p2_player_name",
                    "round_num",
                ]

            filtered_odd = {
                key: value for key, value in odds.items() if key in always_keep_keys
            }

            if market == "3_balls" or market == "round_matchups":
                pass
            elif market == "tournament_matchups":
                try:
                    datagolf_odds = odds["odds"].get("datagolf", {})
                    p1_fair_odds = float(datagolf_odds.get("p1", "0").replace("+", ""))
                    p2_fair_odds = float(datagolf_odds.get("p2", "0").replace("+", ""))
                except ValueError as e:
                    print(f"Error extracting fair odds for {odds}: {e}")
                    continue

                book_odds = {
                    book: {
                        "p1": float(value["p1"].replace("+", "")),
                        "p2": float(value["p2"].replace("+", "")),
                    }
                    for book, value in odds["odds"].items()
                    if book != "datagolf"
                }
                book_name = next(iter(book_odds))
                book_name_odds = book_odds[book_name]
                p1_book_odds = book_name_odds["p1"]
                p2_book_odds = book_name_odds["p2"]

                p1_ev = self.helper.ev(p1_book_odds, p1_fair_odds)
                p2_ev = self.helper.ev(p2_book_odds, p2_fair_odds)

                if p1_ev > ev_threshold:
                    kelly = round(
                        self.helper.kelly_stake(
                            p1_book_odds,
                            p1_fair_odds,
                            config.kelly_multiplyer,
                        ),
                        2,
                    )
                    bet = Play(
                        event_name=matchups["event_name"],
                        bet_desc=f'{filtered_odd["p1_player_name"]} > {filtered_odd["p2_player_name"]}',
                        market=matchups["bet_type"],
                        sub_market=matchups["sub_bet_type"],
                        book=next(iter(book_odds)),
                        odds=self.helper.american_float_to_string(p1_book_odds),
                        ev=round(p1_ev * 100, 0),
                        kelly=f"{kelly}u",
                        bet_size=f"${kelly*(config.bankroll/100)}",
                        fair_odds=self.helper.american_float_to_string(p1_fair_odds),
                    )
                    filtered_plays.append(bet)
                elif p2_ev > ev_threshold:
                    kelly = round(
                        self.helper.kelly_stake(
                            p2_book_odds,
                            p2_fair_odds,
                            config.kelly_multiplyer,
                        ),
                        2,
                    )
                    bet = Play(
                        event_name=matchups["event_name"],
                        bet_desc=f'{filtered_odd["p2_player_name"]} > {filtered_odd["p1_player_name"]}',
                        market=matchups["bet_type"],
                        sub_market=matchups["sub_bet_type"],
                        book=next(iter(book_odds)),
                        odds=self.helper.american_float_to_string(p2_book_odds),
                        ev=round(p2_ev * 100, 0),
                        kelly=f"{kelly}u",
                        bet_size=f"${kelly*(config.bankroll/100)}",
                        fair_odds=self.helper.american_float_to_string(p2_fair_odds),
                    )
                    filtered_plays.append(bet)

        filtered_plays.sort(key=lambda x: x.ev, reverse=True)

        return filtered_plays
