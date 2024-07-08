import helpers

if __name__ == "__main__":
    algorithms = ["binary_search", "linear_search", "ternary_search"]
    # Sorted array of length 1000000
    sorted_array = [i for i in range(1000000)]

    # Perform search for each algorithm
    target = 5
    for algo in algorithms:
        helpers.run_search_algorithm(algo, target, sorted_array)
