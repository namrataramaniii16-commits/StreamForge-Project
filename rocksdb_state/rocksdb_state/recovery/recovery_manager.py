from rocksdb_state.rocksdb_state.storage.crud import CRUDEngine
from rocksdb_state.rocksdb_state.database.database_manager import DatabaseManager
from rocksdb_state.rocksdb_state.serialization.deserializer import Deserializer
from rocksdb_state.rocksdb_state.storage.key_manager import KeyManager
from rocksdb_state.rocksdb_state.models.truck_state import TruckState
from rocksdb_state.rocksdb_state.exceptions.exceptions import SerializationError, ValidationError, StorageException

import logging
logger = logging.getLogger("RecoveryEngine")

class RecoveryManager:
    """
    Coordinates the Phase 4 State Recovery Workflow upon application startup.
    Scans RocksDB, deserializes, validates, and registers states into the Active Runtime Registry.
    """
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.active_registry = {}  # In-memory Active Runtime Registry
        
    def _validate_state(self, state: TruckState) -> bool:
        """Applies the 5-tier validation rules."""
        try:
            if state.count < 0 or state.sum_temperature < 0:
                logger.error(f"Validation failed: Negative aggregation values for {state.truck_id}")
                return False
                
            if state.count > 0:
                expected_avg = state.sum_temperature / state.count
                # Allow minor floating point drift
                if abs(state.average_temperature - expected_avg) > 0.001:
                    logger.error(f"Validation failed: Math invariant broken for {state.truck_id}")
                    return False
            elif state.average_temperature != 0.0:
                logger.error(f"Validation failed: Zero count must have zero average for {state.truck_id}")
                return False
                
            if state.window_start >= state.window_end:
                logger.error(f"Validation failed: Logical time inversion for {state.truck_id}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Validation crashed: {e}")
            return False

    def execute_recovery(self) -> dict:
        """
        Executes the exact-once startup recovery pipeline.
        Returns the final Recovery Status Summary.
        """
        logger.info("Starting Recovery Pipeline...")
        total_processed = 0
        valid_registered = 0
        rejected = 0
        
        try:
            iterator = self.db.iterator()
            for key_bytes, value_bytes in iterator:
                total_processed += 1
                try:
                    # Tier 1 & 2: Deserialization & Structural
                    state = Deserializer.deserialize(value_bytes)
                    
                    # Tier 3 & 4: Aggregation Math & Metadata Validation
                    if not self._validate_state(state):
                        rejected += 1
                        continue
                        
                    # State Registration (Uniqueness check)
                    registry_key = f"{state.truck_id}:{state.window_start}:{state.window_end}"
                    if registry_key in self.active_registry:
                        logger.warning(f"Duplicate runtime identity rejected: {registry_key}")
                        rejected += 1
                    else:
                        self.active_registry[registry_key] = state
                        valid_registered += 1
                        
                except (SerializationError, ValidationError) as e:
                    logger.error(f"Failed to recover key {key_bytes}: {e}")
                    rejected += 1
                    continue
                    
        except StorageException as e:
            logger.critical(f"FATAL Storage failure during recovery: {e}")
            raise
            
        status = "SUCCESS" if rejected == 0 else "SUCCESS_WITH_WARNINGS"
        
        summary = {
            "status": status,
            "total_processed": total_processed,
            "valid_registered": valid_registered,
            "rejected": rejected
        }
        
        logger.info(f"=== RECOVERY SUMMARY ===")
        logger.info(f"Status: {summary['status']}")
        logger.info(f"Total Processed: {summary['total_processed']}")
        logger.info(f"Valid Registered: {summary['valid_registered']}")
        logger.info(f"Rejected: {summary['rejected']}")
        logger.info(f"========================")
        
        return summary
