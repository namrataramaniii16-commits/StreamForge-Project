# Technical Requirements Document (TRD)
**StreamForge RocksDB State Storage Module**

## 1. Objective

This Technical Requirements Document (TRD) details how the StreamForge RocksDB State Storage module will be designed and implemented to satisfy the requirements established in the PRD. It serves as the definitive technical blueprint for development, ensuring architectural consistency, modularity, and maintainability.

## 2. System Overview and Architecture

The module is a local persistence layer responsible for managing the aggregation state of trucks. It encapsulates all RocksDB dependencies and logic, exposing a clean API for the Stream Processing Engine.

### High-Level Architecture
```text
                 Stream Processing Engine
                          │
                          ▼
                   Aggregation Engine
                          │
                          ▼
──────────────────────────────────────────────
          RocksDB State Storage Module
──────────────────────────────────────────────
        │            │             │
        ▼            ▼             ▼
   Public API   Serialization   Recovery
        │
        ▼
   Database Manager
        │
        ▼
       RocksDB
```

## 3. Core Components

The module's logic is cleanly divided into specialized internal components:

1. **Configuration:** Manages database paths, RocksDB options, and runtime settings from environment variables or config files.
2. **Logger:** Standardizes application, error, and debug logging.
3. **Database Manager:** Manages the RocksDB instance lifecycle (opening/closing the DB, maintaining the active handle).
4. **Key Manager:** Centralizes logic for key generation, parsing, and format validation.
5. **Serializer:** Converts `TruckState` Python objects into UTF-8 encoded JSON string bytes.
6. **Deserializer:** Converts raw RocksDB bytes back into JSON, then instantiates `TruckState` objects, handling corrupted data gracefully.
7. **CRUD Engine:** Implements the core persistence logic (`put_state`, `get_state`, `update_state`, `delete_state`, `exists`).
8. **Recovery Manager:** Orchestrates the retrieval of all state records on startup, applying validation and skipping bad records.
9. **Health Manager:** Monitors database connectivity and readiness.

## 4. Internal Architecture and Dependency Graph

The components depend on each other in a strictly unidirectional flow to prevent circular dependencies.

### Dependency Graph
```text
Configuration
      │
      ▼
   Logger
      │
      ▼
Database Manager
      │
      ▼
  Serializer & Deserializer
      │
      ▼
 CRUD Engine & Recovery Manager
      │
      ▼
 Health Manager
```

## 5. Data Flow

### Write Flow
```text
TruckState Object → Key Manager (Generate Key) → Serializer (JSON to UTF-8 Bytes) → Database Manager (Write) → RocksDB
```

### Read Flow
```text
Key → Database Manager (Read) → RocksDB → Raw Bytes → Deserializer (Bytes to JSON to TruckState) → TruckState Object
```

### Recovery Flow
```text
Restart → Database Manager (Open DB) → Iterator reads all records → Deserializer → Validate Objects → Return Recovered State List
```

## 6. Public and Internal Interfaces

### 6.1 Public Interfaces
External modules must strictly use the Public API to interact with the module:
- **Lifecycle:** `initialize_database()`, `shutdown_database()`, `is_initialized()`
- **CRUD:** `put_state()`, `get_state()`, `update_state()`, `delete_state()`, `exists()`
- **Recovery:** `recover_state()`, `recover_all_states()`
- **Health:** `health_check()`, `database_status()`, `ping()`
- **Utility:** `generate_key()`, `parse_key()`, `validate_key()`

### 6.2 Internal Interfaces
These interfaces are private to the module and are not exposed to the broader StreamForge application:
- Interaction between the CRUD Engine and the Serializer/Deserializer.
- Interaction between the Recovery Manager and the internal Database Manager Iterator.

## 7. Error Handling Strategy

Errors are categorized and encapsulated. The module catches native RocksDB exceptions and translates them into domain-specific Python exceptions.

- **Initialization Errors:** (e.g., `DatabaseNotInitializedError`, `ConfigurationError`) Raised on DB open failures or invalid paths.
- **Storage Errors:** (e.g., `StorageReadError`, `StorageWriteError`) Raised on I/O failures.
- **Serialization Errors:** (e.g., `SerializationError`, `DeserializationError`) Raised for invalid objects, malformed JSON, or UTF-8 decode failures.
- **Recovery Errors:** (e.g., `StateRecoveryError`) Non-fatal corruption results in skipped records and logged warnings.
- **Validation Errors:** (e.g., `InvalidKeyError`, `InvalidStateError`) Raised when API inputs fail strict formatting rules.

## 8. Testing Strategy

The module must be verified through multiple layers of testing:
- **Unit Tests:** Independently test the Key Manager, Serializer, and Configuration components using mocked database interactions.
- **Integration Tests:** Verify the full flow from Public API to a temporary, local RocksDB instance on disk.
- **Recovery Tests:** Simulate crash scenarios, write bad bytes to the DB, and ensure `recover_all_states()` handles corruption gracefully without crashing.
- **Health Check Tests:** Validate that `health_check()` fails correctly when the database is closed or locked.

## 9. Performance and Deployment Considerations

- **Performance Goals:** Ensure minimal serialization overhead (JSON), use fast RocksDB `Get` and `Put` operations, and maintain predictable low latency suitable for real-time stream processing.
- **Deployment:** The module must run cross-platform (Linux, Windows, macOS). Database paths must be injected via configuration (e.g., environment variables) to support containerized (Docker) environments without hardcoding local filesystem paths.

## 10. Security and Future Extensibility

- **Security:** Input validation prevents malformed state objects and injection-style keys. The module does not expose internal database handles. Encryption at rest (if required) should be handled by the filesystem or OS.
- **Future Extensibility:** The architecture explicitly supports adding batch operations (`batch_put`), prefix scanning, database compaction routines, metrics collection, and state schema migrations without requiring fundamental structural changes to the module.
