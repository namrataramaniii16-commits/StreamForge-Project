import sys
import os
import json
import time
import logging
from kafka import KafkaConsumer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from rocksdb_state.rocksdb_state.database.database_manager import DatabaseManager
from rocksdb_state.rocksdb_state.storage.crud import CRUDEngine
from rocksdb_state.rocksdb_state.aggregation.aggregator import AggregationUpdateAPI
from rocksdb_state.rocksdb_state.recovery.recovery_manager import RecoveryManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger("IntegrationApp")

def get_window_boundaries(timestamp: int, window_size_ms: int = 10000):
    """Calculates window start and end (e.g., 10-second windows)."""
    window_start = (timestamp // window_size_ms) * window_size_ms
    window_end = window_start + window_size_ms
    return window_start, window_end

def main():
    logger.info("=== 1. Starting Bootstrapper ===")
    
    # 1. Init Database (RocksDB mocked)
    db = DatabaseManager(db_path="./streamforge_data")
    db.open()
    
    # 2. Init CRUD
    crud = CRUDEngine(db)
    
    # 3. Execute Recovery (G4.6 Integration sequence)
    recovery_manager = RecoveryManager(db)
    summary = recovery_manager.execute_recovery()
    
    if summary['status'] == "FATAL":
        logger.critical("Startup aborted due to fatal recovery error.")
        sys.exit(1)
        
    active_registry = recovery_manager.active_registry
    logger.info("=== 2. Runtime Ready. Connecting to Kafka... ===")

    try:
        consumer = KafkaConsumer(
            "truck-telemetry",
            bootstrap_servers="localhost:9092",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode("utf-8"))
        )
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        logger.error("Make sure Kafka is running locally on port 9092.")
        return

    logger.info("=== 3. Event Processing Started ===")
    
    for message in consumer:
        event = message.value
        try:
            # Transform event to ensure we have window boundaries
            truck_id = event["truck_id"]
            # Assume timestamp is in ms, if string, try to parse or use current time
            # For this example, we mock a timestamp if it's a string
            event_ts = int(time.time() * 1000) 
            w_start, w_end = get_window_boundaries(event_ts)
            
            event["window_start"] = w_start
            event["window_end"] = w_end
            
            registry_key = f"{truck_id}:{w_start}:{w_end}"
            
            # Fetch current state from memory registry if it exists
            current_state = active_registry.get(registry_key)
            
            # Update state in memory
            new_state = AggregationUpdateAPI.process_event(event, current_state)
            active_registry[registry_key] = new_state
            
            # Persist to disk
            crud.put_state(new_state)
            
            logger.info(f"Aggregated {truck_id} | Window: {w_start} | Sum: {new_state.sum_temperature:.2f} | Count: {new_state.count} | Avg: {new_state.average_temperature:.2f}")
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")

if __name__ == "__main__":
    main()
