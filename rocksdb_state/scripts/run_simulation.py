import sys
import os

# Add the project root to the Python path so the package can be imported correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import logging
from rocksdb_state.rocksdb_state.database.database_manager import DatabaseManager
from rocksdb_state.rocksdb_state.storage.crud import CRUDEngine
from rocksdb_state.rocksdb_state.aggregation.aggregator import AggregationUpdateAPI
from rocksdb_state.rocksdb_state.recovery.recovery_manager import RecoveryManager

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def run_simulation():
    print("--- 1. Application Startup (Initial) ---")
    db = DatabaseManager()
    db.open()
    crud = CRUDEngine(db)
    
    print("\n--- 2. Processing Events (Aggregation Engine) ---")
    # Event 1: Truck 100, Temp 30.0
    event1 = {"truck_id": "T-100", "window_start": 1000, "window_end": 2000, "temperature": 30.0}
    state = AggregationUpdateAPI.process_event(event1)
    
    # Event 2: Truck 100, Temp 40.0
    event2 = {"truck_id": "T-100", "window_start": 1000, "window_end": 2000, "temperature": 40.0}
    state = AggregationUpdateAPI.process_event(event2, current_state=state)
    
    # Save the state to the DB (simulating the Stream Processor persisting state)
    crud.put_state(state)
    print(f"Aggregated State: sum={state.sum_temperature}, count={state.count}, avg={state.average_temperature}")
    
    # Inject a corrupted state manually into the database to test Fault Tolerance
    print("\n--- 3. Injecting Corrupted State ---")
    db.put(b"T-999:1000", b'{"truck_id": "T-999", "count": -5}') # Missing fields, negative count
    
    # Simulate Application Crash / Shutdown
    print("\n--- 4. Simulating Application Crash ---")
    # In our mock, we keep the `_store` reference to simulate persistent disk, but we recreate the managers
    persisted_disk_data = db._store.copy()
    db.close()
    
    print("\n--- 5. Application Restart (Recovery Engine) ---")
    new_db = DatabaseManager()
    new_db.open()
    new_db._store = persisted_disk_data  # Mount our "disk"
    
    recovery_manager = RecoveryManager(new_db)
    summary = recovery_manager.execute_recovery()
    
    print("\n--- 6. Runtime Registry Verification ---")
    print(f"Active Registry Keys: {list(recovery_manager.active_registry.keys())}")
    
if __name__ == "__main__":
    run_simulation()
