# from datagolf_api import DataGolfAPI
from db_manager import DBManager
from controllers.user_controller import UserController
from controllers.book_controller import BookController

API_KEY = "97a47cb8af3ce0af6a0e6a2a9e56"
DB_FILE = "datagolf.db"


# Function to display the menu and handle user input
def display_main_menu(user_controller, book_controller):

    print("\nMain Menu:")
    print("1. User Management")
    print("2. Book Management")
    print("3. Exit")

    while True:
          choice = input("Enter your choice: ")

          if choice == "1":
              user_management_menu(user_controller)
          elif choice == "2":
              book_management_menu(book_controller)
          elif choice == "3":
              print("Exiting application.")
              break
          else:
              print("Invalid choice. Please choose a valid option.")


# Function to display the user management menu and handle user input
def user_management_menu(user_controller):
    print("\nUser Management Menu:")
    print("1. Update username")
    print("2. Remove user")
    print("3. View all users")
    print("4. Back to Main Menu")

    while True:
        choice = input("Enter your choice: ")

        if choice == "1":
            old_username = input("Enter current username: ")
            new_username = input("Enter new username: ")
            user_controller.update_username(old_username, new_username)
            print("Username updated.")

        elif choice == "2":
            username = input("Enter username to remove: ")
            confirm = input(
                f"Are you sure you want to remove user '{username}'? (yes/no): "
            )
            if confirm.lower() == "yes":
                user_controller.remove_user(username)
                print("User removed.")

        elif choice == "3":
            all_users = user_controller.get_all_users()
            print("\nAll users:")
            print(all_users)

        elif choice == "4":
            break  # Return to main menu

        else:
            print("Invalid choice. Please choose a valid option.")


# Function to display the book management menu and handle user input
def book_management_menu(book_controller):
    print("\nBook Management Menu:")
    print("1. View all books")
    print("2. Back to Main Menu")

    while True:
        choice = input("Enter your choice: ")

        if choice == "1":
            all_books = book_controller.get_all_books()
            print("\nAll books:")
            print(all_books)

        elif choice == "2":
            break  # Return to main menu

        else:
            print("Invalid choice. Please choose a valid option.")


# Main function to run the application
def main():
    # Create a DuckDB connection
    db = DBManager(DB_FILE)
    con = db.connect()

    # Instantiate controllers
    user_controller = UserController(con)
    book_controller = BookController(con)

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
        main_choice = display_main_menu(user_controller, book_controller)

        if main_choice == 1:
            user_management_menu(user_controller)
        elif main_choice == 2:
            book_management_menu(book_controller)
        elif main_choice == 3:
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please choose a valid option.")

    # Clean up resources
    con.close()


if __name__ == "__main__":
    main()
