class RocksDBStateError(Exception):
    """Base exception for all StreamForge RocksDB State Engine errors."""
    pass

class StorageException(RocksDBStateError):
    """Raised when an underlying RocksDB I/O operation fails."""
    pass

class SerializationError(RocksDBStateError):
    """Raised when serialization to/from JSON byte arrays fails."""
    pass

class ValidationError(RocksDBStateError):
    """Raised when a state object fails domain structural or logic validation."""
    pass

class AggregationError(RocksDBStateError):
    """Raised during Phase 3 aggregation if mathematical logic is violated."""
    pass

class RecoveryError(RocksDBStateError):
    """Raised during Phase 4 if state recovery fails to restore a valid pipeline."""
    pass

class StartupError(RocksDBStateError):
    """Raised when application dependencies or the recovery integration sequence fails."""
    pass
