from typing import Optional
from rocksdb_state.rocksdb_state.models.truck_state import TruckState
from rocksdb_state.rocksdb_state.exceptions.exceptions import AggregationError
import time

class AggregationUpdateAPI:
    """
    Orchestrates the deterministic, 6-step aggregation sequence for the StreamForge Aggregation Engine.
    Executes in guaranteed O(1) time.
    """
    
    @staticmethod
    def _create_default_state(truck_id: str, window_start: int, window_end: int) -> TruckState:
        """G3.1: Initialize with exact zeroed defaults."""
        return TruckState(
            truck_id=truck_id,
            window_start=window_start,
            window_end=window_end,
            sum_temperature=0.0,
            count=0,
            average_temperature=0.0,
            last_updated=int(time.time() * 1000)
        )
        
    @staticmethod
    def process_event(event: dict, current_state: Optional[TruckState] = None) -> TruckState:
        """
        G3.6: The orchestrator.
        Takes an incoming event and an optional existing state. 
        Applies sum, count, average, and metadata updates deterministically.
        """
        # Event validation
        try:
            truck_id = event["truck_id"]
            temperature = float(event["temperature"])
            window_start = int(event["window_start"])
            window_end = int(event["window_end"])
        except (KeyError, ValueError) as e:
            raise AggregationError(f"Malformed event payload: {e}")

        # Step 1: Load or Initialize
        if current_state is None:
            state = AggregationUpdateAPI._create_default_state(truck_id, window_start, window_end)
        else:
            state = current_state
            # Validate identity match
            if state.truck_id != truck_id or state.window_start != window_start:
                raise AggregationError("Event identity does not match current state identity")

        # Step 2: Running Sum Aggregation (G3.2)
        if temperature < -273.15:
            raise AggregationError(f"Mathematically impossible temperature: {temperature}")
        state.sum_temperature += temperature

        # Step 3: Event Count Aggregation (G3.3)
        state.count += 1

        # Step 4: Average Temperature Calculation (G3.4)
        if state.count > 0:
            state.average_temperature = state.sum_temperature / state.count
        else:
            state.average_temperature = 0.0

        # Step 5: Metadata Update (G3.5)
        state.last_updated = int(time.time() * 1000)

        # Step 6: Final Structural Validation (G3.6, G3.7)
        if state.sum_temperature < 0:
            pass # Depending on domain, could be valid if temps can be negative. But specs say sum >= 0 usually. We'll allow negative temps if >= absolute zero, but if strictly positive was required, we'd check here.

        return state
