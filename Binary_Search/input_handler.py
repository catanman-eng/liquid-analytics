def get_user_input():
    while True:
        try:
            n = int(input("Enter the length of the sorted array (e.g., 10000000): "))
            if n <= 0:
                print("Please enter a positive integer.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    while True:
        try:
            target = int(
                input(f"Enter the target value to find (between 0 and {n - 1}): ")
            )
            if target < 0 or target >= n:
                print(f"Please enter an integer between 0 and {n - 1}.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    return n, target