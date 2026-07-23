from rocksdb_state.rocksdb_state.database.database_manager import DatabaseManager
from rocksdb_state.rocksdb_state.models.truck_state import TruckState
from rocksdb_state.rocksdb_state.serialization.serializer import Serializer
from rocksdb_state.rocksdb_state.serialization.deserializer import Deserializer
from rocksdb_state.rocksdb_state.storage.key_manager import KeyManager
from rocksdb_state.rocksdb_state.exceptions.exceptions import StorageException

class CRUDEngine:
    """Executes state operations against RocksDB."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        
    def put_state(self, state: TruckState) -> None:
        """Persists a TruckState into the database."""
        try:
            key = KeyManager.generate_key(state.truck_id, state.window_start)
            value = Serializer.serialize(state)
            self.db.put(key, value)
        except Exception as e:
            raise StorageException(f"Failed to put state: {e}")
            
    def get_state(self, truck_id: str, window_start: int) -> TruckState:
        """Retrieves a TruckState from the database."""
        try:
            key = KeyManager.generate_key(truck_id, window_start)
            value = self.db.get(key)
            if value is None:
                return None
            return Deserializer.deserialize(value)
        except Exception as e:
            raise StorageException(f"Failed to get state: {e}")
            
    def update_state(self, state: TruckState) -> None:
        """Updates an existing TruckState. Same as put_state in RocksDB."""
        # RocksDB handles updates as overwrites
        self.put_state(state)
        
    def delete_state(self, truck_id: str, window_start: int) -> None:
        """Removes a TruckState from the database."""
        try:
            key = KeyManager.generate_key(truck_id, window_start)
            self.db.delete(key)
        except Exception as e:
            raise StorageException(f"Failed to delete state: {e}")
            
    def exists_state(self, truck_id: str, window_start: int) -> bool:
        """Checks if a state exists without full deserialization."""
        try:
            key = KeyManager.generate_key(truck_id, window_start)
            value = self.db.get(key)
            return value is not None
        except Exception as e:
            raise StorageException(f"Failed to check state existence: {e}")
