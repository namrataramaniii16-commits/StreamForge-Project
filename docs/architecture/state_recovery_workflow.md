# State Recovery Workflow Specification
**StreamForge RocksDB State Engine**

## 1. Objective
This specification defines the deterministic **State Recovery Workflow**, the strict sequence of operations executed by the Recovery Engine upon application startup. It guarantees that persisted raw data is consistently discovered, reconstructed, rigorously validated, and successfully registered into active memory before any new streaming events are processed.

## 2. Architecture & Responsibilities
The workflow operates as a linear, unyielding sequence.
- **Responsibilities:** Directing the storage layer to enumerate keys, parsing byte payloads via the Deserializer, enforcing domain invariants, and populating the active runtime state registry.
- **Out of Scope:** Making business decisions about window expiration, replaying Kafka logs, calculating new aggregations, or updating metadata.

```text
RocksDB Scan → Bytes → Deserializer → Validation → Active Registry → Aggregation Ready
```

## 3. Detailed Execution Flow
The recovery pipeline executes the following stages exactly in order:
1. **Locate Storage:** Bind to the local RocksDB instance via `DatabaseManager`.
2. **Enumerate Persisted States:** Utilize a RocksDB Iterator to scan all keys adhering to the `{truck_id}:{window_start}` format.
3. **Load Serialized Records:** Extract the raw JSON UTF-8 byte arrays from persistent storage.
4. **Deserialize:** Route bytes through the `Deserializer` to reconstruct the in-memory `TruckState` domain object.
5. **Validate:** Enforce structural integrity (e.g., all fields present, `count >= 0`, `sum >= 0`, timestamps mathematically logical).
6. **Register:** Store the validated `TruckState` into the active runtime memory registry so the Aggregation Engine can route new events to it.
7. **Complete:** Log recovery metrics (total states restored, time taken) and release the execution lock blocking the main stream processor.

## 4. Validation & Registration Stage
- **Validation Checkpoint:** A recovered object is inherently untrusted until fully validated. It must satisfy all domain constraints as if it were newly generated. If a state fails validation, the workflow halts registration for that object, quarantines the data, and logs the corruption.
- **Registration Checkpoint:** Registration is the final step. Once registered, the state is considered live. The workflow guarantees that a partially recovered or invalid object will **never** reach the Active Registry.

## 5. Recovery Guarantees
- **Deterministic Startup:** Every application boot follows the exact same enumeration and validation sequence.
- **Zero Event Loss Gap:** Because the active registry perfectly mirrors the disk state at the time of the crash, the event stream consumer can safely resume from its last committed offset without recalculating historical averages.
- **Strict Isolation:** The Aggregation Engine remains totally dormant until the recovery workflow announces full completion.

## 6. Error Handling
- **Database Unavailable:** The process throws a fatal `StartupError` and immediately halts execution.
- **Deserialization / Validation Failure:** The specific state is rejected and logged. Depending on configuration strictness, this may either increment a "corrupted state" counter and skip the record, or fatally crash the application to enforce strict consistency. The corrupted state will *never* enter active memory.

## 7. Performance Constraints
- **Iteration Speed:** Scanning the database must utilize native RocksDB C++ iterators rather than repeated single-key `get()` calls, minimizing memory and CPU overhead.
- **Memory Footprint:** The registry must efficiently hold the restored state without unnecessarily duplicating data structures or string payloads.

## 8. Future Extensibility
The pipeline structure naturally accommodates future operational upgrades:
- **Parallel Iteration:** Scanning multiple non-overlapping key ranges concurrently to drastically reduce startup latency.
- **Selective Loading:** Only scanning keys whose `window_end` is actively in the future (allowing the Phase 5 Cleanup Engine to purge expired states in the background).
- **Snapshot Support:** Booting from a specific RocksDB snapshot rather than the active HEAD.
