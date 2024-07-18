import Binary_Search.search_helpers as search_helpers
from Binary_Search.input_handler import get_user_input
from rich.console import Console
from rich.table import Table


def main():
    algorithms = ["binary_search", "linear_search", "ternary_search"]

    # Sorted array of length n
    n, target = get_user_input()    
    sorted_array = [i for i in range(n)]

    table = Table(title=f"Min Execution Time to Find Target {target} in Sorted Array of Length {n}")
    table.add_column("Algorithm")
    table.add_column("Min Time (s)")
    
    # Perform search for each algorithm
    print(f"Target: {target} in sorted array of length {n}\n")
    for algo in algorithms:
        min_time = search_helpers.run_search_algorithm(algo, target, sorted_array)
        table = search_helpers.add_row_to_table(table, algo, min_time)
    
    console = Console()
    console.print(table)


if __name__ == "__main__":
    main()
