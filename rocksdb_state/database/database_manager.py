from typing import Optional
from rocksdb_state.config import DatabaseConfig
from rocksdb_state.logging import get_logger

try:
    import rocksdb
except ImportError:
    # Allows the file to be imported for linting/docs even if rocksdb fails to build on Windows
    rocksdb = None

class DatabaseStateError(Exception):
    """Exception raised for database lifecycle violations."""
    pass

class DatabaseManager:
    """
    Manages the lifecycle of the RocksDB instance.
    Acts as a wrapper ensuring exactly one database connection exists.
    """
    
    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._db: Optional['rocksdb.DB'] = None
        self._logger = get_logger(self.__class__.__name__)
        
        if rocksdb is None:
            self._logger.warning("rocksdb library is not installed! DatabaseManager will fail to open.")

    def open(self) -> None:
        """
        Opens the RocksDB instance.
        Raises DatabaseStateError if already open or if initialization fails.
        """
        if self.is_open():
            self._logger.error("Attempted to open database when it is already open.")
            raise DatabaseStateError("Database is already open.")

        if rocksdb is None:
            raise RuntimeError("python-rocksdb is not installed.")

        try:
            self._logger.info(f"Opening RocksDB at '{self._config.database_path}' (create_if_missing={self._config.create_if_missing})")
            opts = rocksdb.Options(create_if_missing=self._config.create_if_missing)
            self._db = rocksdb.DB(self._config.database_path, opts)
            self._logger.info("Database opened successfully.")
        except Exception as e:
            self._logger.error(f"Failed to open database: {e}", exc_info=True)
            raise DatabaseStateError(f"Failed to open database: {e}") from e

    def close(self) -> None:
        """
        Closes the RocksDB instance safely.
        """
        if not self.is_open():
            self._logger.warning("Attempted to close database, but it is already closed.")
            return

        self._logger.info("Closing database...")
        # In python-rocksdb, the DB connection is closed when the object is destroyed/deleted.
        self._db = None
        self._logger.info("Database closed successfully.")

    def is_open(self) -> bool:
        """Returns True if the database is currently open and active."""
        return self._db is not None

    def get_database(self) -> 'rocksdb.DB':
        """
        Returns the active RocksDB instance.
        Raises DatabaseStateError if not open.
        """
        if not self.is_open():
            self._logger.error("Attempted to access database, but it is not open.")
            raise DatabaseStateError("Database is not open.")
        return self._db
