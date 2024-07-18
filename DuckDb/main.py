from datagolf_api import DataGolfAPI
from db_manager import DBManager
from user_controller import UserController

API_KEY = "97a47cb8af3ce0af6a0e6a2a9e56"
DB_FILE = "datagolf.db"

# Function to display the menu and handle user input
def display_menu():
    print("\nWhat would you like to do?")
    print("1. Update username")
    print("2. Remove user")
    print("3. View all users")
    print("4. Logout")

    while True:
        choice = input("Enter your choice: ")

        if choice in ["1", "2", "3", "4"]:
            return int(choice)
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")


# Main function to run the application
def main():
    # Create a DuckDB connection
    db = DBManager(DB_FILE)
    con = db.connect()

    # Instantiate UserController with the connection
    user_controller = UserController(con)

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

    # User actions loop
    while True:
        choice = display_menu()

        if choice == 1:
            old_username = username
            new_username = input("Enter new username: ")
            user_controller.update_username(old_username, new_username)
            print("Username updated.")

        elif choice == 2:
            confirm = input(
                f"Are you sure you want to remove user '{username}'? (yes/no): "
            )
            if confirm.lower() == "yes":
                user_controller.remove_user(username)
                print("User removed.")
                break  # Exit after removing user

        elif choice == 3:
            all_users = user_controller.get_all_users()
            print("\nAll users:")
            print(all_users)

        elif choice == 4:
            user_controller.logout()
            break  # Exit after logout

        else:
            print("Invalid choice. Please choose a valid option.")


if __name__ == "__main__":
    main()