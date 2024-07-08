from typing import List
from timeit import repeat

def binary_search(target: int, arr: List[int]) -> int:
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
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def ternary_search(target: int, arr: List[int]) -> int:
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

def run_search_algorithm(algorithm: str, target: int, array: List[int]) -> int:
    setup_code = f"from helpers import {algorithm}"
    stmt = f"{algorithm}({target}, {array})"
    times = repeat(setup=setup_code, stmt=stmt, repeat=3, number=10)

    print(f"Algorithm: {algorithm}. Minimum execution time: {min(times)}")