from controllers.menu_controller import MenuController


def get_user_menu(user_controller):
    user_menu_text = "\nUser Management Menu:"
    user_choices = {
        "1": (
            "Update username",
            lambda: user_controller.update_username(
                input("Enter current username: "), input("Enter new username: ")
            ),
        ),
        "2": (
            "Remove user",
            lambda: user_controller.remove_user(input("Enter username to remove: ")),
        ),
        "3": ("View all users", lambda: print(user_controller.get_all_users())),
        "4": ("Back to Main Menu", lambda: None),
    }

    return MenuController(
        user_menu_text, user_choices, exit_choice=max(user_choices.keys(), key=int)
    )


def get_book_menu(book_controller, username):
    book_menu_text = "\nBook Management Menu:"
    book_choices = {
        "1": ("View all books", lambda: print(book_controller.get_all_books())),
        "2": ("View your books", lambda: print(book_controller.get_user_books(username))),
        "3": ("Back to Main Menu", lambda: None),
    }
    return MenuController(
        book_menu_text, book_choices, exit_choice=max(book_choices.keys(), key=int)
    )


def get_main_menu(user_controller, book_controller, username):
    user_menu = get_user_menu(user_controller)
    book_menu = get_book_menu(book_controller, username)

    main_menu_text = "\nMain Menu:"
    main_choices = {
        "1": ("User Management", user_menu.display_menu),
        "2": ("Book Management", book_menu.display_menu),
        "3": ("Exit", lambda: exit()),
    }
    return MenuController(main_menu_text, main_choices)
