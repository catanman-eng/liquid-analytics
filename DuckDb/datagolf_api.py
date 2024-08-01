import requests
from db_manager import DBManager
from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.user_config_controller import UserConfig
from controllers.helpers import Helper, Play
from typing import List


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

        if sub_market == "tournament_matchups":
            always_keep_keys = ["datagolf", "ties", "p1_player_name", "p2_player_name"]
        elif sub_market == "3_balls":
            always_keep_keys = [
                "datagolf",
                "player_name",
                "p1_player_name",
                "p2_player_name",
                "p3_player_name",
                "ties",
            ]
        elif sub_market == "round_matchups":
            always_keep_keys = [
                "datagolf",
                "player_name",
                "p1_player_name",
                "p2_player_name",
                "ties",
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

        if matchup_response.get("round_num", None):
            result["round_num"] = matchup_response["round_num"]
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
                    except AttributeError:
                        print(f"Error calculating EV for {odd['player_name']}")

                    kelly, ev = self.helper.ev_check(
                        bet_odds, fair_odds, config, ev_threshold
                    )
                    if kelly:
                        filtered_odd[key] = value
                        bet = self.helper.create_play(
                            filtered_odd,
                            odds_list,
                            key,
                            value,
                            fair_odds,
                            ev,
                            kelly,
                            config.bankroll,
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
                    "ties",
                ]
            elif market == "round_matchups":
                always_keep_keys = [
                    "datagolf",
                    "player_name",
                    "p1_player_name",
                    "p2_player_name",
                    "ties",
                ]

            filtered_odd = {
                key: value for key, value in odds.items() if key in always_keep_keys
            }

            if market == "3_balls":
                try:
                    datagolf_odds = odds["odds"].get("datagolf", {})
                    p1_fair_odds = float(datagolf_odds.get("p1", "0").replace("+", ""))
                    p2_fair_odds = float(datagolf_odds.get("p2", "0").replace("+", ""))
                    p3_fair_odds = float(datagolf_odds.get("p3", "0").replace("+", ""))
                except ValueError as e:
                    print(f"Error extracting fair odds for {odds}: {e}")
                    continue

                book_odds = {
                    book: {
                        "p1": float(value["p1"].replace("+", "")),
                        "p2": float(value["p2"].replace("+", "")),
                        "p3": float(value["p3"].replace("+", "")),
                    }
                    for book, value in odds["odds"].items()
                    if book != "datagolf"
                }

                for book_name, book_odd in book_odds.items():
                    p1_book_odds = book_odd["p1"]
                    p2_book_odds = book_odd["p2"]
                    p3_book_odds = book_odd["p3"]
                    ties = filtered_odd["ties"]
                    book_name = book_name

                    p1_kelly, p1_ev = self.helper.ev_check(
                        p1_book_odds, p1_fair_odds, config, ev_threshold
                    )
                    p2_kelly, p2_ev = self.helper.ev_check(
                        p2_book_odds, p2_fair_odds, config, ev_threshold
                    )
                    p3_kelly, p3_ev = self.helper.ev_check(
                        p3_book_odds, p3_fair_odds, config, ev_threshold
                    )

                    if p1_kelly:
                        bet = self.helper.create_play(
                            filtered_odd,
                            matchups,
                            book_name,
                            p1_book_odds,
                            p1_fair_odds,
                            p1_ev,
                            p1_kelly,
                            config.bankroll,
                            player=1,
                            ties=ties,
                        )
                        filtered_plays.append(bet)
                    if p2_kelly:
                        bet = self.helper.create_play(
                            filtered_odd,
                            matchups,
                            book_name,
                            p2_book_odds,
                            p2_fair_odds,
                            p2_ev,
                            p2_kelly,
                            config.bankroll,
                            player=2,
                            ties=ties,
                        )
                        filtered_plays.append(bet)
                    if p3_kelly:
                        bet = self.helper.create_play(
                            filtered_odd,
                            matchups,
                            book_name,
                            p3_book_odds,
                            p3_fair_odds,
                            p3_ev,
                            p3_kelly,
                            config.bankroll,
                            player=3,
                            ties=ties,
                        )
                        filtered_plays.append(bet)
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
                ties = filtered_odd["ties"]

                p1_kelly, p1_ev = self.helper.ev_check(
                    p1_book_odds, p1_fair_odds, config, ev_threshold
                )
                p2_kelly, p2_ev = self.helper.ev_check(
                    p2_book_odds, p2_fair_odds, config, ev_threshold
                )

                if p1_kelly:
                    bet = self.helper.create_play(
                        filtered_odd,
                        matchups,
                        book_name,
                        p1_book_odds,
                        p1_fair_odds,
                        p1_ev,
                        p1_kelly,
                        config.bankroll,
                        player=1,
                        ties=ties,
                    )
                    filtered_plays.append(bet)
                elif p2_kelly:
                    bet = self.helper.create_play(
                        filtered_odd,
                        matchups,
                        book_name,
                        p2_book_odds,
                        p2_fair_odds,
                        p2_ev,
                        p2_kelly,
                        config.bankroll,
                        player=2,
                        ties=ties,
                    )
                    filtered_plays.append(bet)

        filtered_plays.sort(key=lambda x: x.ev, reverse=True)

        return filtered_plays
