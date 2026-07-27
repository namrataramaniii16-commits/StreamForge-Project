# Database Manager Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification defines the `DatabaseManager` component responsible for managing the complete lifecycle of the RocksDB database. It serves as the single entry point for opening, closing, and accessing the database connection, strictly avoiding any business logic or CRUD operations.

## 2. Architecture & Design Principles
- **Single Source of Access:** All modules (CRUD, Aggregation, Recovery, Cleanup) must ask the `DatabaseManager` for the active database handle.
- **Resource Management:** Ensures only one instance of the database is open at a time to prevent file locking and memory bloat.
- **Dependency Isolation:** Depends solely on the Configuration System (for the path and options) and Logging System (for lifecycle visibility).

## 3. Public Interface

- `__init__(config: DatabaseConfig)`: Initializes the manager with configuration.
- `open()`: Attempts to open the RocksDB instance. Creates the database if configured to do so. Raises an exception if already open.
- `close()`: Safely closes the database connection by removing the Python reference (which triggers the underlying RocksDB close via garbage collection).
- `is_open()`: Returns `True` if the database is currently available.
- `get_database()`: Returns the internal RocksDB handle for use by internal components (e.g., CRUD engine). Raises an exception if closed.

## 4. Internal State
The `DatabaseManager` tracks:
- `_config`: A reference to the immutable `DatabaseConfig`.
- `_db`: The active `rocksdb.DB` handle (or `None` if closed).
- `_logger`: The centralized logger instance.

## 5. Error Handling
The manager handles state violations safely:
- Attempting to `open()` an already open database raises a `DatabaseStateError`.
- Attempting to `get_database()` when closed raises a `DatabaseStateError`.
- Underlying `rocksdb` initialization errors are caught, logged, and re-raised as `DatabaseStateError`.

## 6. Future Extensibility
While currently a simple wrapper, the architecture permits future features such as:
- Read-only database instances.
- Adding database compaction methods.
- Managing backup configurations.
- Advanced performance metric tracking.
