import search_helpers as search_helpers
from input_handler import get_user_input
from rich.console import Console
from rich.table import Table


def main():
    algorithms = {
        "binary_search": search_helpers.binary_search,
        "linear_search": search_helpers.linear_search,
        "ternary_search": search_helpers.ternary_search,
    }

    # Sorted array of length n
    n, target = get_user_input()    
    sorted_array = [i for i in range(n)]
    sorted_array = sorted(sorted_array)

    table = Table(title=f"Min Execution Time to Find Target {target} in Sorted Array of Length {n}")
    table.add_column("Algorithm")
    table.add_column("Min Time (s)")
    
    # Perform search for each algorithm
    print(f"Target: {target} in sorted array of length {n}\n")
    for algo_name, algo_func in algorithms.items():
        min_time = search_helpers.run_search_algorithm(algo_func, target, sorted_array)
        table = search_helpers.add_row_to_table(table, algo_name, min_time)

    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
