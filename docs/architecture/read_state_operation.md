# Read State (get_state) Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification defines the architecture, workflow, and determinism of the **Read State (`get_state`)** operation. This operation is the sole retrieval mechanism for extracting a `TruckState` from RocksDB, orchestrating key lookup, deserialization, and validation while strictly ensuring no state mutations occur.

## 2. Architecture & Responsibilities
The `get_state` operation serves as a strict read-only boundary within the CRUD Engine.
- **Responsibilities:** Validating the requested storage key, querying RocksDB, passing serialized bytes to the Deserializer, and returning a strictly validated `TruckState` domain object (or a safe "Not Found" signal).
- **Out of Scope:** Aggregation logic, database connection management, serialization to JSON, updating state, or automatically generating default missing states.

```text
Caller → get_state(Key) → RocksDB.get() → Deserializer → Validated TruckState
```

## 3. Storage Key Lookup Strategy
The operation demands a deterministic storage key, identical to the one produced during `put_state`.
- **Expected Format:** `{truck_id}:{window_start_iso8601}`
- **Lookup Method:** Exact point-query (`RocksDB.get(key)`). No range scanning is performed in this operation.

## 4. Operation Workflow
1. **Key Validation:** Pre-verifies that the requested key string is non-null, non-empty, and adheres to expected format rules.
2. **Database Read:** Queries the active RocksDB instance using `RocksDB.get()`.
3. **Missing State Evaluation:**
   - If `RocksDB.get()` returns `None`/empty, the workflow immediately halts and returns a structured `State Not Found` result.
   - *Note:* Missing state is treated as a standard conditional flow, not an exception, since new trucks/windows frequently arrive.
4. **Deserialization Pipeline:** If bytes are returned, they are forwarded to the `Deserializer`, which handles UTF-8 decoding, JSON parsing, and field extraction.
5. **Revalidation:** The output of the Deserializer guarantees that the returned object satisfies all domain invariants (`count >= 0`, `window_start < window_end`, etc.).
6. **Return:** Yields the validated `TruckState` domain object to the caller.

## 5. Error Handling
Failures during `get_state` are strictly trapped and escalated safely:
- **Lookup Errors:** Hardware/Storage failures from RocksDB throw an `OperationError`.
- **Data Corruption:** If the bytes exist but fail UTF-8 decoding, JSON parsing, or invariant validation, the Deserializer throws a `DeserializationError`. `get_state` logs the critical data corruption and bubbles the exception up. Corrupt data is never returned to the application.
- **Null/Invalid Keys:** Fast-fails with an `ArgumentError` before touching disk.

## 6. Performance & Constraints
To guarantee sub-millisecond retrieval suitable for high-throughput streaming:
- Zero memory is allocated for missing keys (fast-fail on `None`).
- The bytes are decoded and instantiated precisely once.
- The function is strictly read-only and side-effect free.

## 7. Component Interactions
- **Inputs:** A storage key (String).
- **Outputs:** A validated `TruckState` object (or Not Found).
- **Dependencies:** Interacts cleanly with `RocksDB` (via `DatabaseManager`) and the `Deserializer`.
- **Consumers:** Heavily utilized by `update_state` (to retrieve existing metrics before incrementing) and `Recovery Manager`.
