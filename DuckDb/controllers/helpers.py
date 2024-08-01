import uuid
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


class Helper:
    def __init__(self):
        pass

    def generate_guid(self):
        return str(uuid.uuid4())

    def navigate_menu(self, length):
        while True:
            choice = input("Enter your choice: ")
            if choice.isdigit() and 1 <= int(choice) <= length:
                return int(choice)
            else:
                print(f"Invalid choice. Please enter a number from 1 to {length}.")

    # convert American odds to percentage odds
    def american_to_percentage(self, american: float) -> float:
        if american == 100.0 or american == -100.0:
            return 0.5
        elif american > 100.0:
            return 100.0 / (american + 100.0)
        elif american < -100.0:
            return (american * -1.0) / ((american * -1.0) + 100.0)
        return 0.0

    # find the net profit for a bet based on american odds and stake
    def american_profit(self, odds: float, stake: float) -> float:
        if stake <= 0 or (odds < 100.0 and odds > -100.0):
            return 0.0
        elif odds >= 100.0:
            return (odds / 100.0) * stake
        elif odds <= -100.0:
            return (100 / ((-1.0) * odds)) * stake
        return 0.0

    def ev(self, bet_odds: float, fair_odds: float) -> float:
        fair_win_prob = self.american_to_percentage(fair_odds)
        profit = self.american_profit(bet_odds, 100.0)
        return ((fair_win_prob * profit) - ((1.0 - fair_win_prob) * 100.0)) / 100.0

    # returns bet size recommendation in units
    def kelly_stake(self, bet_odds: float, fair_odds: float, multiplier: float):
        p = self.american_to_percentage(fair_odds)
        q = 1 - p
        b = self.american_profit(bet_odds, 100.0) / 100.0
        return (p - (q / b)) * multiplier * 100.0

    def american_float_to_string(self, odds: float) -> str:
        if odds > 0:
            return f"+{odds:.0f}"
        return f"{odds:.0f}"

    def ev_check(self, book_odds, fair_odds, config, threshold):
        ev = self.ev(book_odds, fair_odds)
        if ev > threshold:
            kelly = round(
                self.kelly_stake(book_odds, fair_odds, config.kelly_multiplier), 2
            )
            return kelly, ev
        else:
            return None, None

    def create_play(
        self,
        filtered_odd,
        odds_list,
        book_name,
        play_odds,
        fair_odds,
        ev,
        kelly,
        bankroll,
        player=None,
    ):
        if odds_list["bet_type"] == "outright":
            return Play(
                event_name=odds_list["event_name"],
                bet_desc=f"{filtered_odd['player_name']}: {odds_list['sub_bet_type'].title()}",
                market=odds_list["market"],
                sub_market=filtered_odd["sub_market"],
                book=book_name,
                fair_odds=self.american_float_to_string(fair_odds),
                odds=play_odds,
                ev=round(ev * 100, 0),
                kelly=f"{kelly}u",
                bet_size=f"${kelly*(bankroll/100)}",
            )
        else:
            if odds_list["sub_bet_type"] == "3_balls":
                match player:
                    case 1:
                        bet_desc = f'{filtered_odd["p1_player_name"]} > {filtered_odd["p2_player_name"]}, {filtered_odd["p3_player_name"]}'
                    case 2:
                        bet_desc = f'{filtered_odd["p2_player_name"]} > {filtered_odd["p1_player_name"]}, {filtered_odd["p3_player_name"]}'
                    case 3:
                        bet_desc = f'{filtered_odd["p3_player_name"]} > {filtered_odd["p1_player_name"]}, {filtered_odd["p2_player_name"]}'

                return Play(
                    event_name=odds_list["event_name"],
                    bet_desc=bet_desc,
                    market=odds_list["bet_type"],
                    sub_market=odds_list["sub_bet_type"],
                    book=book_name,
                    fair_odds=self.american_float_to_string(fair_odds),
                    odds=self.american_float_to_string(play_odds),
                    ev=round(ev * 100, 0),
                    kelly=f"{kelly}u",
                    bet_size=f"${kelly*(bankroll/100)}",
                )
            elif odds_list["sub_bet_type"] == "tournament_matchups":
                match player:
                    case 1:
                        bet_desc = f'{filtered_odd["p1_player_name"]} > {filtered_odd["p2_player_name"]}'
                    case 2:
                        bet_desc = f'{filtered_odd["p2_player_name"]} > {filtered_odd["p1_player_name"]}'
                return Play(
                    event_name=odds_list["event_name"],
                    bet_desc=bet_desc,
                    market=odds_list["bet_type"],
                    sub_market=odds_list["sub_bet_type"],
                    book=book_name,
                    fair_odds=self.american_float_to_string(fair_odds),
                    odds=self.american_float_to_string(play_odds),
                    ev=round(ev * 100, 0),
                    kelly=f"{kelly}u",
                    bet_size=f"${kelly*(bankroll/100)}",
                )
