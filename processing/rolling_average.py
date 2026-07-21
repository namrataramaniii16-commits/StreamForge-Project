def calculate_average(numbers):
    if len(numbers) == 0:
        return 0

    return round(sum(numbers) / len(numbers), 2)