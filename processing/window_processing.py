from processing.rolling_average import calculate_average
window = []

WINDOW_SIZE = 3  # Maximum size of sliding window

def add_temperature(temp):
    window.append(temp)

    if len(window) > WINDOW_SIZE:
        window.pop(0)    # Remove oldest temperature
    average = calculate_average(window)

    return {
        "window": window.copy(),
        "average": round(average, 2)
    }
    