# StreamForge Integration Contract: RocksDB State Storage

## 1. Objective

This Integration Contract defines how the **RocksDB State Storage** module communicates with other components of the StreamForge architecture (specifically the Stream Processing Engine and the Aggregation Engine). It specifies data exchange formats, module responsibilities, strict dependency rules, and ownership boundaries. This contract ensures loose coupling, predictable behavior, and hides all RocksDB implementation details behind a clean Public API.

### High-Level Architecture
```text
                 Kafka
                   │
                   ▼
        Stream Processing Engine
                   │
                   ▼
         Aggregation Engine
                   │
                   ▼
──────────────────────────────────────────
      RocksDB State Storage Module
──────────────────────────────────────────
                   │
                   ▼
             Local RocksDB
```

## 2. Module Responsibilities

Each module in the StreamForge architecture has distinct, non-overlapping responsibilities.

### 2.1 Stream Processing Engine
- **Responsibilities:** Reading Kafka events, parsing incoming event payloads, determining processing windows, calling the RocksDB API via the Aggregation Engine, and managing event routing.
- **Restrictions:** It **must not** directly access RocksDB or contain storage-level logic.

### 2.2 Aggregation Engine
- **Responsibilities:** Executing business logic, computing running sums, counts, and averages, and initializing new state when required.
- **Restrictions:** It must use the Public API provided by the RocksDB module to retrieve and persist state.

### 2.3 RocksDB State Storage
- **Responsibilities:** Persisting `TruckState` objects, reading stored state, updating state, recovering state after failures, handling serialization/deserialization, managing the database lifecycle, and performing health checks.
- **Restrictions:** It **must not** contain business logic, stream-processing logic, or Kafka-specific code.

## 3. Communication Flow

All interaction between the Stream Processing Engine and RocksDB strictly follows the Public API.

### Request Flow
```text
Stream Processor → Public API → Storage Layer → Serializer → RocksDB
```

### Response Flow
```text
RocksDB → Deserializer → TruckState → Public API → Stream Processor
```

### Typical Event Processing Flow
```text
Kafka Event
      │
      ▼
Stream Processor
      │
      ▼
Aggregation Engine
      │
      ▼
get_state() (via Public API)
      │
      ▼
TruckState Object Returned
      │
      ▼
Update Aggregation (in memory)
      │
      ▼
update_state() (via Public API)
      │
      ▼
Persist Updated State to RocksDB
```

## 4. Data Exchange Contract

Modules exchange structured data, never raw database bytes.

**The RocksDB module receives:**
- `TruckState` objects (for puts and updates).
- `truck_id` (Strings) and `window_start` (Strings/DateTimes) for targeted lookups and deletions.

**The RocksDB module returns:**
- Validated `TruckState` objects.
- `None` (if a requested state does not exist).
- `Boolean` values (for existence checks and health).
- Health Status dictionaries.
- Lists of `TruckState` objects (during recovery).

**No raw RocksDB bytes are ever exposed outside the storage module.**

## 5. Ownership Boundaries

To prevent tight coupling, ownership is strictly enforced:

- **Stream Processing Engine Owns:** Kafka consumers, event ordering, window assignment, and event routing.
- **Aggregation Engine Owns:** Running sums, event counts, average calculations, and the core business logic.
- **RocksDB Module Owns:** Persistence, state recovery, serialization, database lifecycle, key management, and storage health monitoring.

Each responsibility belongs to exactly one module.

## 6. Dependency Rules

The dependency graph flows in one direction to keep the storage layer reusable and isolated.

**The RocksDB module MAY depend on:**
- Python standard configuration and logging.
- JSON processing libraries.
- The RocksDB client library (`python-rocksdb`).
- The `TruckState` internal data model.

**The RocksDB module MUST NOT depend on:**
- Kafka clients.
- Stream processing frameworks (Faust, Bytewax, etc.).
- Web frameworks (FastAPI) or REST APIs.
- React, dashboards, or frontend code.
- Authentication, authorization, or networking modules.

## 7. Error Propagation

The storage module handles internal RocksDB exceptions and translates them into domain-specific errors. 

When an operation fails:
```text
RocksDB Internal Error
          ↓
Storage Exception Generated
          ↓
Propagated via Public API
          ↓
Stream Processor Catches Exception
          ↓
Stream Processor Decides Action (Retry, Dead-Letter, Crash)
```
The storage module reports the failure clearly but **does not** dictate how the application should recover.

## 8. Integration Sequence and Rules

All interacting components must abide by the following lifecycle sequence and rules:

### Initialization Sequence
```text
Application Starts
        ↓
initialize_database()
        ↓
Stream Processor Starts
        ↓
Receive Event → get_state() → Update Aggregation → update_state()
        ↓
Continue Processing
        ↓
Application Shutdown Initiated
        ↓
shutdown_database()
```

### Core Integration Rules
1. Always initialize the database before processing any events.
2. Never access the RocksDB instance or directory directly from outside the module.
3. Use only the defined Public API.
4. Always pass `TruckState` objects; never manually serialize data before calling the API.
5. Handle storage exceptions gracefully in the calling module.
6. Always cleanly close the database during application shutdown to prevent corruption.

## 9. Future Extensibility

This contract is designed to be backward compatible. Future components can be added without altering existing module responsibilities.
- **Examples of future integrations:** Backup services, monitoring and metrics collectors, replication layers, and state migration tools.
- These additions will integrate strictly through expansions to the Public API.
