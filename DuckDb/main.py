from datagolf_api import DataGolfAPI
from db_manager import DBManager

API_KEY = "97a47cb8af3ce0af6a0e6a2a9e56"
DB_FILE = ":memory:"


def main():
    # Initialize DataGolfAPI and fetch data
    api = DataGolfAPI(API_KEY)
    df_players_response = api.fetch_players_data()

    # Initialize DBManager and perform database operations
    db = DBManager(DB_FILE)
    db.connect()
    db.create_table("players", df_players_response)

    # Example query
    result = db.query("SELECT * FROM players LIMIT 5")
    print(result)


if __name__ == "__main__":
    main()
