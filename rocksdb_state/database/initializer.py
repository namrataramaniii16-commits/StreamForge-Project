import sys
from typing import Tuple
from rocksdb_state.config import load_config, Config, ConfigurationError
from rocksdb_state.logging import configure_logging, get_logger
from rocksdb_state.database.database_manager import DatabaseManager, DatabaseStateError

def initialize_storage() -> Tuple[Config, DatabaseManager]:
    """
    Orchestrates the startup of all foundational components.
    
    Sequence:
    1. Load Configuration
    2. Initialize Logger
    3. Create DatabaseManager
    4. Open RocksDB
    5. Validate Startup
    
    Fails fast and raises an exception if any step fails.
    """
    # 1. Load Configuration (Fails fast if invalid)
    try:
        config = load_config()
    except ConfigurationError as e:
        # Cannot log using the framework yet, fallback to stderr
        print(f"CRITICAL: Failed to load configuration: {e}", file=sys.stderr)
        raise
        
    # 2. Initialize Logger
    try:
        configure_logging(config.logging)
        logger = get_logger("Initializer")
        logger.info("Configuration loaded and logging initialized successfully.")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize logging: {e}", file=sys.stderr)
        raise

    # 3. Create DatabaseManager
    try:
        logger.info("Creating DatabaseManager...")
        db_manager = DatabaseManager(config.database)
    except Exception as e:
        logger.critical(f"Failed to create DatabaseManager: {e}", exc_info=True)
        raise

    # 4. Open RocksDB
    try:
        logger.info("Opening RocksDB database...")
        db_manager.open()
    except DatabaseStateError as e:
        logger.critical(f"Database failed to open: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.critical(f"Unexpected error while opening database: {e}", exc_info=True)
        raise
        
    # 5. Validate Startup
    if not db_manager.is_open():
        error_msg = "DatabaseManager reports database is not open after initialization."
        logger.critical(error_msg)
        raise DatabaseStateError(error_msg)
        
    logger.info("Database Initialization completed successfully. Storage layer is ready.")
    
    return config, db_manager
