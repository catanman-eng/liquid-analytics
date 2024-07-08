import helpers

if __name__ == "__main__":
    algorithms = ["binary_search", "linear_search", "ternary_search"]

    # Sorted array of length n
    n = 10000000
    sorted_array = [i for i in range(n)]
    target = 5

    # Perform search for each algorithm
    print(f"Target: {target} in sorted array of length {n}\n")
    for algo in algorithms:
        helpers.run_search_algorithm(algo, target, sorted_array)
