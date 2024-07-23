import uuid


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
