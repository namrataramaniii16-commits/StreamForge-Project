# RocksDB State Storage: Public API Specification

## 1. Objective and Design Principles

The Public API defines the complete, official external interface for the RocksDB State Storage module. It acts as the stable integration contract for other StreamForge components, ensuring internal RocksDB implementation details remain strictly hidden.

The API is designed according to the following principles:
- **Simple & Consistent:** Provides predictable and unified behavior across all methods.
- **Storage-agnostic:** Hides RocksDB specifics from external modules.
- **Easy to Test:** Facilitates straightforward mocking for dependent modules.
- **Easy to Extend:** Designed for additive evolution.
- **Strong Typing:** Operates on `TruckState` objects rather than raw bytes.

## 2. API Categories

The Public API is logically divided into five groups:
1. Lifecycle API
2. CRUD API
3. Recovery API
4. Health API
5. Utility API

---

### 2.1 Lifecycle API
Controls the initialization and termination of the RocksDB database.

#### Methods:
- `initialize_database()`: Loads configuration, opens the database connection, and allocates resources. Called when the application starts.
- `shutdown_database()`: Safely flushes data, closes the connection, and releases resources. Called during application shutdown.
- `is_initialized() -> bool`: Verifies whether the database is currently open and ready for operations.

#### Workflow:
```text
Application Starts → initialize_database() → Database Ready → shutdown_database() → Resources Released
```

---

### 2.2 CRUD API
Manages the persistence, retrieval, modification, and deletion of `TruckState` objects.

#### Methods:
- `put_state(state: TruckState)`: Serializes and stores a new `TruckState` object.
- `get_state(truck_id: str, window_start: str) -> TruckState`: Retrieves and reconstructs an existing state.
- `update_state(state: TruckState)`: Modifies an existing stored state.
- `delete_state(truck_id: str, window_start: str)`: Removes a stored state.
- `exists(truck_id: str, window_start: str) -> bool`: Checks whether a state record is currently stored without retrieving its full payload.

#### Workflow:
```text
TruckState → CRUD API → Serializer → RocksDB
```

---

### 2.3 Recovery API
Handles the safe restoration of persisted state following an application restart.

#### Methods:
- `recover_state(truck_id: str, window_start: str) -> TruckState`: Recovers a specific state record.
- `recover_all_states() -> List[TruckState]`: Recovers all states currently persisted in the database, gracefully skipping any corrupted entries.

#### Workflow:
```text
Restart → Recovery API → Deserializer → Recovered TruckState
```

---

### 2.4 Health API
Reports on the operational status and health of the storage layer.

#### Methods:
- `health_check() -> bool`: Verifies general database availability and read/write capability.
- `database_status() -> dict`: Reports detailed health information (e.g., status, storage availability).
- `ping() -> bool`: Performs a lightweight connectivity or responsiveness check.

#### Workflow:
```text
Request → Health API → Database Check → Health Report
```

---

### 2.5 Utility API
Provides internal helper methods that centralize common logic, exposed for controlled use by higher-level components.

#### Methods:
- `generate_key(truck_id: str, window_start: str) -> str`: Generates a standard RocksDB key.
- `parse_key(key: str) -> dict`: Parses a key string back into its components.
- `validate_key(key: str) -> bool`: Validates that a key follows the required format.
- `serialize_state(state: TruckState) -> bytes`: Converts a state object to bytes.
- `deserialize_state(data: bytes) -> TruckState`: Converts bytes back to a state object.

---

## 3. API Interaction Diagram

```text
                 Stream Processor
                        │
                        ▼
                RocksDB Public API
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
   Lifecycle         CRUD          Recovery
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                  Serialization
                        │
                        ▼
                     RocksDB
```

## 4. API Design Rules

Every public method implemented under this specification must adhere to these rules:
- Have a single, clear responsibility.
- Return predictable results based on the defined contract.
- Raise meaningful, domain-specific exceptions.
- Completely encapsulate RocksDB internal data structures.
- Use structured objects (e.g., `TruckState`) at the API boundary, never raw bytes.
- Be fully documented with type hints and docstrings.

## 5. Error Handling Strategy

The Public API translates RocksDB-specific faults into consistent, meaningful errors. The following error states should be clearly communicated:
- **Database Not Initialized:** Raised when operations are attempted before `initialize_database()` completes.
- **Invalid TruckState:** Raised when attempting to store a malformed object.
- **Missing Record:** Raised when querying a state that does not exist.
- **Corrupted Data / Serialization Failure:** Raised during failed `serialize_state()` or `deserialize_state()` operations.
- **Database Read/Write Failure:** Raised when underlying storage access fails.

Errors must be propagated in a controlled manner, allowing callers to implement resilient logic without dealing with underlying storage exceptions.

## 6. Future Extensibility

The API is structured to allow the addition of new capabilities without breaking backward compatibility. Potential future additions include:
- `batch_put()`, `batch_get()`, `batch_delete()`
- `scan_by_prefix()`
- `backup_database()`, `restore_database()`
- `compact_database()`
- `metrics()` (for detailed Prometheus/Grafana integration)
