from datagolf_api import DataGolfAPI
from db_manager import DBManager
from user_controller import UserController

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

    user_controller = UserController(db.con)

    # Example query
    result = db.query("SELECT * FROM players LIMIT 5")
    
    username = input("Enter username: " )

    if not user_controller.check_user_exists(username):
        user_controller.add_user(username)
        print(f"Welcome, {username}! Your account has been created.")
    else:
        print(f"Welcome back, {username}!")

    # Optionally, display all users in the database
    all_users = user_controller.get_all_users()
    print("\nAll users:")
    print(all_users)


if __name__ == "__main__":
    main()
