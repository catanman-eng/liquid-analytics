from typing import List


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

if __name__ == "__main__":
    arr = [1, 3, 5, 7, 9]
    target = 5
    print(binary_search(target, arr))  # Output: 2