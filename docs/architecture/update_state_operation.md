# Update State (update_state) Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification outlines the architecture, workflow, and concurrency considerations of the **Update State (`update_state`)** operation. This mechanism is responsible for safely retrieving, modifying, validating, and atomically persisting an existing `TruckState` domain object while enforcing data integrity and strict domain invariants.

## 2. Architecture & Responsibilities
The `update_state` operation acts as a high-level orchestrator composing multiple low-level components.
- **Responsibilities:** Retrieving the current state using `get_state`, applying incremental modifications (aggregation updates), recalculating derived values, running pre-persistence validation, serializing, and committing the changes to RocksDB.
- **Out of Scope:** Creating state if it does not exist (upsert behavior is explicitly avoided to separate concerns), window streaming logic, and altering immutable identifiers.

```text
Storage Key → Read State → Apply Updates → Validation → Serializer → RocksDB.put()
```

## 3. Mutable vs Immutable Fields
When an update is requested, the system strictly separates fields into mutable and immutable sets:
- **Immutable:** `truck_id`, `window_start`, `window_end` (Changing these destroys referential integrity and invalidates the deterministic key).
- **Mutable:** `sum_temperature`, `count`, `last_updated`.
- **Derived (Recalculated):** `average_temperature`. Any change to `sum_temperature` or `count` mathematically mandates the immediate recalculation of `average_temperature`.

## 4. Operation Workflow
1. **Validation of Request:** Validates the input key and update payload.
2. **Read Current State:** Invokes `get_state(key)` to retrieve the current validated `TruckState`.
3. **Missing State Check:** If `get_state` returns `Not Found`, the operation aborts and yields `State Not Found`. It strictly does **not** create new state.
4. **Apply Updates:** Applies the new event's metrics (e.g. `sum_temperature += event.temp`, `count += 1`, updates `last_updated`).
5. **Recalculation:** Recomputes `average_temperature = sum_temperature / count`.
6. **Revalidation:** Asserts that all invariants hold true (no negative counts, no negative temps, valid timestamps).
7. **Serialization:** Translates the updated object into UTF-8 JSON bytes.
8. **RocksDB Write:** Executes `RocksDB.put(key, bytes)`.

## 5. Concurrency & Atomicity
The update process guarantees a logical Read-Modify-Write (RMW) cycle.
- **Atomicity:** The `RocksDB.put()` call ensures that either the completely new state byte array overwrites the old one, or the write fails and the old one remains. There are no partial updates on disk.
- **Concurrency Strategy:** Depending on the stream-processing threading model (e.g., actor model, partitioned Kafka queues), writes are logically synchronized by key partitioning to prevent Lost Update anomalies (stale reads).

## 6. Error Handling
- **State Not Found:** Treated as an explicit failure condition within `update_state` since updates require an origin.
- **Validation Failure:** If applied updates violate invariants, an `UpdateError` is raised before serialization.
- **Storage/IO Failure:** Bubbles up from `RocksDB.put()`, ensuring the caller knows the state was not durably persisted.

## 7. Performance & Constraints
- **Execution Cost:** 1 Read (`RocksDB.get`), 1 Validation, 1 Serialization, 1 Write (`RocksDB.put`).
- **Memory Cost:** Minimal. The existing `TruckState` domain object is mutated in-place and serialized directly, avoiding excessive temporary allocations in high-throughput environments.
