class MenuController:
    def __init__(self, menu_text, choices: dict, exit_choice = None):
        self.menu_text = menu_text
        self.choices = choices
        self.exit_choice = exit_choice

    def display_menu(self):
        while True:
            print(self.menu_text)
            for key, (description, _) in self.choices.items():
                print(f"{key}. {description}")

            choice = input("Enter your choice: ")
            if choice in self.choices:
                action = self.choices[choice][1]
                if action:
                    action()
                if choice == self.exit_choice:
                    return False
            else:
                print("Invalid choice. Please choose a valid option.")