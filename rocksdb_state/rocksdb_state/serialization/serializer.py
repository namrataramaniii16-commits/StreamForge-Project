import json
from rocksdb_state.rocksdb_state.models.truck_state import TruckState
from rocksdb_state.rocksdb_state.exceptions.exceptions import SerializationError

class Serializer:
    """Handles serialization of TruckState to JSON bytes."""
    
    @staticmethod
    def serialize(state: TruckState) -> bytes:
        """Converts a TruckState object into a UTF-8 JSON byte array."""
        try:
            payload = {
                "truck_id": state.truck_id,
                "window_start": state.window_start,
                "window_end": state.window_end,
                "sum_temperature": state.sum_temperature,
                "count": state.count,
                "average_temperature": state.average_temperature,
                "last_updated": state.last_updated
            }
            return json.dumps(payload).encode('utf-8')
        except Exception as e:
            raise SerializationError(f"Failed to serialize state: {e}")
