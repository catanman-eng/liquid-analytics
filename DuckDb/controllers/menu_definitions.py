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
        "2": (
            "View your books",
            lambda: print(book_controller.get_user_books(username)),
        ),
        "3": (
            "Add book to your list",
            lambda: book_controller.add_book_to_user(
                input("Enter book name: "), username
            ),
        ),
        "4": (
            "Remove book from your list",
            lambda: book_controller.remove_book_from_user(
                input("Enter book name: "), username
            ),
        ),
        "5": ("Back to Main Menu", lambda: None),
    }
    return MenuController(
        book_menu_text, book_choices, exit_choice=max(book_choices.keys(), key=int)
    )

def get_config_menu(config_controller, username):
    config_menu_text = "\nUser Configuration Menu:"
    config_choices = {
        "1": (
            "Update user configuration",
            lambda: config_controller.update_user_config(
                username,
                input("Enter kelly multiplyer (percent as decimal): "),
                input("Enter bankroll: "),
            ),
        ),
        "2": (
            "View user configuration",
            lambda: print(config_controller.get_user_config(username)),
        ),
        "3": ("Back to Main Menu", lambda: None),
    }
    return MenuController(
        config_menu_text, config_choices, exit_choice=max(config_choices.keys(), key=int)
    )


def get_main_menu(user_controller, book_controller, user_config_controller, bet_controller, username):
    user_menu = get_user_menu(user_controller)
    book_menu = get_book_menu(book_controller, username)
    config_menu = get_config_menu(user_config_controller, username)
    bet_menu = get_bet_menu(bet_controller, username)

    main_menu_text = "\nMain Menu:"
    main_choices = {
        "1": ("User Management", user_menu.display_menu),
        "2": ("Book Management", book_menu.display_menu),
        "3": ("User Configuration", config_menu.display_menu),
        "4": ("Bet Menu", bet_menu.display_menu),
        "5": ("Exit", lambda: exit())
    }
    return MenuController(main_menu_text, main_choices)

def get_bet_menu(bet_controller, username):
    config_menu_text = "\nUser Configuration Menu:"
    config_choices = {
        "1": (
            "Get Outright Plays",
            lambda: bet_controller.get_outright_plays(
                username,
                input("Enter Market: "),
                float(input("Enter EV Threshold (0 to 1): ")),
            ),
        ),
        "2": ("Back to Main Menu", lambda: None),
    }
    return MenuController(
        config_menu_text, config_choices, exit_choice=max(config_choices.keys(), key=int)
    )