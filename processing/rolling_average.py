def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.

    Returns 0 when the input list is empty.
    The result is rounded to two decimal places.
    """
    if len(numbers) == 0:
        return 0

    return round(sum(numbers) / len(numbers), 2)