import requests

class DataGolfAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://feeds.datagolf.com"

    def fetch_players_data(self):
        url = f"{self.base_url}/get-player-list?file_format=[file_format]&key={self.api_key}"
        response = requests.get(url)
        return response