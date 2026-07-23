import json
from rocksdb_state.rocksdb_state.models.truck_state import TruckState
from rocksdb_state.rocksdb_state.exceptions.exceptions import SerializationError, ValidationError

class Deserializer:
    """Handles deserialization of JSON bytes into a TruckState domain object."""
    
    @staticmethod
    def deserialize(data: bytes) -> TruckState:
        """Converts a UTF-8 JSON byte array back into a TruckState."""
        try:
            payload = json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise SerializationError(f"Invalid JSON payload: {e}")
            
        # Basic structural verification before instantiation
        required_fields = [
            "truck_id", "window_start", "window_end",
            "sum_temperature", "count", "average_temperature", "last_updated"
        ]
        for field in required_fields:
            if field not in payload:
                raise ValidationError(f"Missing mandatory field '{field}' in serialized state")
                
        return TruckState(
            truck_id=payload["truck_id"],
            window_start=int(payload["window_start"]),
            window_end=int(payload["window_end"]),
            sum_temperature=float(payload["sum_temperature"]),
            count=int(payload["count"]),
            average_temperature=float(payload["average_temperature"]),
            last_updated=int(payload["last_updated"])
        )
