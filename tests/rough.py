

def find_the_largest_num(nums: list[int | float]) -> float:
    """
    returns the largest number from the list of int or float values

    Args:
    nums - a list of int/float values

    Returns:
    The largest number from the list as a float

    Raises:
    TypeError - If nums is not a list

    """
    if not nums:
        raise ValueError("List can't be empty!")

    max_num = float('-inf')

    for num in nums:
        if not isinstance(num, (int, float)):
            raise TypeError(f"Invalid element: {num}. All elements must be int/float.")

        if num > max_num:
            max_num = num

    return max_num


print(find_the_largest_num([-10, -3, -1, -2]))
