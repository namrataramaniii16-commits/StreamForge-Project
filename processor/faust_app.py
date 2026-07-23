"""
Main entry point for the StreamForge Stream Processing module.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import faust
import logging

from config import APP_NAME, KAFKA_BROKER
from rocksdb_state.rocksdb_state.database.database_manager import DatabaseManager
from rocksdb_state.rocksdb_state.storage.crud import CRUDEngine
from rocksdb_state.rocksdb_state.recovery.recovery_manager import RecoveryManager

# Create the Faust application
app = faust.App(
    APP_NAME,
    broker=f"kafka://{KAFKA_BROKER}"
)

@app.on_configured.connect
def configure_rocksdb(app, conf, **kwargs):
    logging.info("Initializing RocksDB State Engine...")
    db = DatabaseManager(db_path="./streamforge_data")
    db.open()
    
    crud = CRUDEngine(db)
    recovery_manager = RecoveryManager(db)
    
    summary = recovery_manager.execute_recovery()
    if summary['status'] == "FATAL":
        logging.critical("Startup aborted due to fatal recovery error.")
        sys.exit(1)
        
    app.rocksdb_db = db
    app.rocksdb_crud = crud
    app.rocksdb_registry = recovery_manager.active_registry
    logging.info("RocksDB State Engine initialized and recovered successfully.")

# Register all Faust agents
import agents
print("Faust application initialized successfully.")