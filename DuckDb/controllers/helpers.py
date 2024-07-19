import uuid

class Helper:
    def __init__(self):
        pass

    def generate_guid(self):
        return str(uuid.uuid4())

    def navigate_menu(self, length):
        while True:
            choice = input("Enter your choice: ")
            if choice.isdigit() and 1 <= int(choice) <= length:
                return int(choice)
            else:
                print(f"Invalid choice. Please enter a number from 1 to {length}.")