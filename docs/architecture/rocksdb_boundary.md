# Architecture Boundary: RocksDB State Storage Module

## 1. Purpose and Objective

The RocksDB State Storage module acts as the **persistent state layer** for the StreamForge project. Its primary purpose is to provide a lightweight, embedded storage engine for the Stream Processing Engine, responsible exclusively for storing, retrieving, updating, and recovering the aggregation state of individual trucks during stream processing.

This module is designed with strict boundaries to prevent feature creep, simplify implementation, and ensure seamless integration with the rest of the StreamForge ecosystem. It does not perform event processing; it simply manages the persistence of state.

## 2. Responsibilities

The RocksDB module is strictly responsible for the following tasks:

- **State Persistence:** Persisting truck aggregation state to local storage.
- **State Retrieval:** Reading previously stored state efficiently.
- **State Updates:** Modifying and updating existing state.
- **State Deletion:** Deleting obsolete or expired state.
- **State Recovery:** Recovering state safely after an application restart or crash.
- **API Exposure:** Providing a clean, robust storage API for other components.
- **Lifecycle Management:** Managing the initialization and shutdown of the RocksDB instance.
- **Serialization/Deserialization:** Handling the serialization and deserialization of state objects (e.g., using JSON).
- **Health Checks:** Providing mechanisms to verify the health and readiness of the database.
- **Data Cleanup:** Supporting future capabilities for the cleanup of expired data.

## 3. Explicit Out-of-Scope Items

To maintain a clean architectural boundary, the RocksDB module is **not responsible** for:

- Reading, consuming, or acknowledging events from Kafka.
- Processing event streams or executing any streaming logic.
- Implementing sliding, tumbling, or any other window calculations.
- Executing aggregation algorithms or business logic.
- Providing REST API endpoints or handling HTTP requests.
- Managing authentication, authorization, or security protocols.
- Dashboard, UI, or frontend development.
- Distributed coordination, clustering, or node consensus.
- Cluster management or deployment orchestration.

These responsibilities are explicitly delegated to other components within StreamForge.

## 4. Module Position and Integration Points

The RocksDB State Storage Module integrates closely with the Stream Processing Engine but remains decoupled from external systems like Kafka or frontend applications.

### High-Level Architecture Flow

```text
                Kafka
                  │
                  ▼
      Stream Processing Engine
                  │
                  ▼
      Aggregation Logic
                  │
                  ▼
────────────────────────────────────
     RocksDB State Storage Module
────────────────────────────────────
                  │
                  ▼
          Persistent Local State
```

### High-Level Execution Workflow

```text
Incoming Event
        │
        ▼
Stream Processor
        │
        ▼
Request Current State
        │
        ▼
RocksDB State Storage
        │
        ▼
Return Stored State
        │
        ▼
Aggregation Updated
        │
        ▼
Persist Updated State
```

## 5. External Dependencies

The module requires the following dependencies to function:

- **Python 3.x:** The primary programming language.
- **RocksDB (python-rocksdb):** The embedded key-value store.
- **JSON Serialization:** For converting state objects to and from byte streams.
- **Logging Framework:** Standard Python logging for operational observability.
- **Configuration System:** To manage paths, options, and database settings.

It is independent of Kafka client libraries, web frameworks (like FastAPI), and UI libraries.

## 6. Public Interface

The module will expose a clean, well-defined public interface (API) for the Stream Processing Engine to interact with. Expected functionality includes:

- `initialize_database()`: Set up and open the database connection.
- `shutdown_database()`: Safely close the database connection.
- `put_state(key, value)`: Insert new state data.
- `get_state(key)`: Retrieve existing state data.
- `update_state(key, value)`: Modify existing state data.
- `delete_state(key)`: Remove state data.
- `exists(key)`: Check if a key exists in the database.
- `recover_state()`: Load previously persisted state upon startup.
- `health_check()`: Verify that the database is accessible and functional.
