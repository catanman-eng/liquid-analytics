import requests
from db_manager import DBManager

class DataGolfAPI:
    def __init__(self, api_key, con, db_manager: DBManager):
        self.api_key = api_key
        self.base_url = "https://feeds.datagolf.com"
        self.con = con
        self.db_manager = db_manager

        self.create_players_table()
                

    def fetch_players_data(self):
        url = f"{self.base_url}/get-player-list?file_format=json&key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status() 
        return response
    
    def create_players_table(self):
        data = self.fetch_players_data()

        self.db_manager.create_table("players", data)