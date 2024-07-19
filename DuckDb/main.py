# from datagolf_api import DataGolfAPI
from db_manager import DBManager
from controllers.user_controller import UserController
from controllers.book_controller import BookController
from controllers.menu_definitions import get_main_menu

API_KEY = "97a47cb8af3ce0af6a0e6a2a9e56"
DB_FILE = "datagolf.db"

def main():
    # Create a DuckDB connection
    db = DBManager(DB_FILE)
    con = db.connect()
    try:
        # Instantiate controllers
        user_controller = UserController(con)
        book_controller = BookController(con)
        
        main_menu = get_main_menu(user_controller, book_controller)

        # Prompt for sign-in
        while True:
            username = input("Enter your username (or type 'exit' to quit): ")

            if username.lower() == "exit":
                print("Exiting application.")
                break

            if user_controller.check_user_exists(username):
                print(f"Welcome back, {username}!")
                break
            else:
                print(f"User '{username}' not found. Creating new user.")
                user_controller.add_user(username)
                print(f"Welcome, {username}! Your account has been created.")
                break

        # Main application loop
        while True:
            if not main_menu.display_menu():
                break
    finally:
        # Clean up resources
        con.close()


if __name__ == "__main__":
    main()
