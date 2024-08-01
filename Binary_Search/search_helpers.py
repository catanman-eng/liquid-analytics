from typing import List, Callable
from timeit import repeat
from tqdm import tqdm


def binary_search(target: int, arr: List[int]) -> int:
    """Performs binary search on a sorted array to find the target."""
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def linear_search(target: int, arr: List[int]) -> int:
    """Performs linear search on an array to find the target."""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1


def ternary_search(target: int, arr: List[int]) -> int:
    """Performs ternary search on a sorted array to find the target."""
    left = 0
    right = len(arr) - 1

    while left <= right:
        partition_size = (right - left) // 3
        mid1 = left + partition_size
        mid2 = right - partition_size

        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2

        if target < arr[mid1]:
            right = mid1 - 1
        elif target > arr[mid2]:
            left = mid2 + 1
        else:
            left = mid1 + 1
            right = mid2 - 1

    return -1


def run_search_algorithm(
    algorithm: Callable[[int, List[int]], int],
    target: int,
    array: List[int],
    repeat_val: int = 3,
    number: int =5,
) -> float:
    """Runs the given search algorithm and returns the minimum execution time."""
    setup_code = f"from search_helpers import {algorithm.__name__}"
    stmt = f"{algorithm.__name__}({target}, {array})"

    algo_name = remove_underscores_and_capitalize(algorithm.__name__)

    print(f"Executing: {algo_name}, {repeat_val * number} times")
    total_iterations = repeat_val * number
    times = []

    with tqdm(total=total_iterations) as pbar:
        for _ in range(repeat_val):
            time = repeat(setup=setup_code, stmt=stmt, number=number)
            times.extend(time)
            pbar.update(number)

    min_time = min(times)

    print(f"Algorithm: {algo_name}. Minimum execution time: {min_time:.5f} seconds")
    return min_time


def add_row_to_table(table, algo, min_time):
    """Adds a row to the Rich table with the algorithm name and minimum time."""
    algo_name = remove_underscores_and_capitalize(algo)
    table.add_row(algo_name, f"{min_time:.5f}")
    return table

def remove_underscores_and_capitalize(string : str) -> str:
    """Replaces underscores with spaces and capitalizes the first letter of each word."""
    return string.replace("_", " ").title()