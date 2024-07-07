# Design 1: Binary Search Implementation

## Problem Statement
Implement an efficient algorithm to find the position of a target value within a sorted array. This involves designing a binary search function that minimizes the number of comparisons by repeatedly dividing the search interval in half.

## Objective
Create a binary search function that returns the index of the target value if it exists in the array or `-1` if it does not.

## Input and Output
- **Input**: 
  - A sorted list of integers `arr`.
  - An integer `target` to be searched in the array.
- **Output**: 
  - The index of `target` in `arr` if found, otherwise `-1`.

## Design Approach
1. **Initialize Pointers**: Set `left` to 0 and `right` to `n-1` where n represents the length of the array
2. **Search**
  - Compute midpoint
  - Compare midpoint to target
  - Adjust left and right accordingly
  - Repeat until
3. **Return**: Return the index of target if found, else `-1` 

## Edge Cases
 - Empty array
 - Value is not in array
 - Elements of array are all the same
