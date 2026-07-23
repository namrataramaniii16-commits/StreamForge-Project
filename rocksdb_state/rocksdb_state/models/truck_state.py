from dataclasses import dataclass

@dataclass
class TruckState:
    """
    Domain object representing the mathematical state of a specific truck 
    within a specific processing window.
    """
    truck_id: str
    window_start: int
    window_end: int
    sum_temperature: float
    count: int
    average_temperature: float
    last_updated: int
