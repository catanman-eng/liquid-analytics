import requests
import pandas as pd


class DataGolfAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://datagolf.com"

    def fetch_players_data(self):
        url = f"{self.base_url}/get-player-list&key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return pd.DataFrame(data)


# Example usage:
# api = DataGolfAPI('your_api_key')
# df_players = api.fetch_players_data()
