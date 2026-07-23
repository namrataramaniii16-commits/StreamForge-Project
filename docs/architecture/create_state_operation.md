# Create State (put_state) Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification outlines the architecture, workflow, and deterministic guarantees of the **Create State (`put_state`)** operation. This operation is the primary entry point for storing newly generated `TruckState` aggregation objects into RocksDB while ensuring atomic writes and deterministic key management.

## 2. Architecture & Responsibilities
The `put_state` operation acts as the orchestrator for state creation within the CRUD Engine.
- **Responsibilities:** Validating the domain object, generating the unique storage key, triggering serialization, and executing the atomic `RocksDB.put()` operation.
- **Out of Scope:** Computing aggregation metrics, assigning windows, business logic processing, or managing the database lifecycle.

```text
Aggregation Engine → TruckState → put_state() → Serializer → RocksDB.put()
```

## 3. Storage Key Generation
Every `TruckState` must have a 100% deterministic, collision-free storage key ensuring constant time lookups and a predictable database layout.
- **Format:** `{truck_id}:{window_start_iso8601}`
- **Example:** `TRUCK-101:2026-07-24T10:00:00Z`
Given the same `TruckState`, the `GenerateKey(State)` phase will always yield the exact same key.

## 4. Operation Workflow
The operation follows a strict, linear progression to ensure data integrity:
1. **Pre-Validation:** Checks if the input is a non-null `TruckState` and explicitly verifies domain invariants. If invalid, aborts immediately.
2. **Key Generation:** Generates the UTF-8 encoded storage key using the deterministic format.
3. **Duplicate Check Policy:** In StreamForge, `put_state` is for creating new state. If the key already exists, it is rejected (or delegated to `update_state`), explicitly avoiding silent overwrites that mask data processing bugs.
4. **Serialization:** Passes the domain object to the `Serializer` to obtain UTF-8 JSON bytes.
5. **Persistence (Atomic Write):** Calls `RocksDB.put(key, bytes)`. The write either succeeds completely or fails completely; partial states are structurally impossible.
6. **Return:** Yields a `Success` or `Failure` status containing the generated key and operation timestamp.

## 5. Error Handling & Atomicity
The operation must be atomic. Failures at any stage halt the process before modifying disk contents.
- **Validation/Serialization Failures:** Immediate rejection. Returns a structured error or throws an exception without touching RocksDB.
- **I/O & RocksDB Failures:** If `RocksDB.put()` throws an exception (e.g., storage full, disk disconnected, permissions lost), it is caught, logged with full context, and propagated to the caller.
Errors are never swallowed.

## 6. Performance & Constraints
To sustain high-throughput stream processing environments:
- Key generation, validation, and serialization occur exactly once per invocation.
- Unnecessary object copying and intermediate string allocations are strictly prohibited.
- `put_state` itself maintains zero state and relies entirely on the provided `DatabaseManager` and `Serializer`.

## 7. Component Interactions
- **Inputs:** A strictly validated `TruckState` from the Aggregation Engine.
- **Outputs:** An explicit success/failure operation status.
- **Dependencies:** Interacts cleanly with `TruckState`, `Serializer`, and uses the active RocksDB handle retrieved from the `DatabaseManager`.
