# CRUD Operations Testing Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification outlines the comprehensive **CRUD Testing Framework** designed to verify the functional correctness, reliability, data integrity, and performance of every State Storage operation implemented in Phase 2. The framework ensures the core storage engine behaves deterministically before integration with higher-level streaming logic.

## 2. Test Architecture & Scope
The testing framework operates across multiple dimensions:
- **Scope:** `TruckState` domain object, `Serializer`, `Deserializer`, and all CRUD primitives (`put_state`, `get_state`, `update_state`, `delete_state`, `exists_state`).
- **Layers:** Unit Tests (isolated component behavior), Integration Tests (full RocksDB lifecycle), and Performance/Stress Tests (throughput and durability bounds).

## 3. Unit Testing Strategy
Components are isolated and tested independently of RocksDB.

### 3.1 Domain Validation Tests (`TruckState`)
- **Valid States:** Instantiating objects with standard streaming metrics.
- **Invalid States (Rejection):** Empty `truck_id`, negative `count`, negative `sum_temperature`, or inverted processing windows (`window_end < window_start`).

### 3.2 Serialization Round-Trip Verification
- **`Serialize`:** Verifies deterministic JSON output (keys sorted, precise numerics, UTF-8 encoded bytes).
- **`Deserialize`:** Verifies proper coercion from bytes back to domain primitives.
- **Round-Trip Assertion:** `Deserialize(Serialize(State)) == Original State` logically.
- **Corrupted Data Handling:** Passing malformed JSON, truncated bytes, or missing mandatory fields ensures the deserializer fast-fails without crashing.

## 4. Integration Testing Strategy
Verifies the CRUD functions operating against a live (often temporary or in-memory) RocksDB instance.

### 4.1 Create (`put_state`) & Read (`get_state`)
- Insert a valid state. Retrieve it using the generated key. Assert properties match.
- Attempt to retrieve a non-existent key (verify `Not Found` handling).

### 4.2 Update (`update_state`)
- Create state -> Retrieve -> Mutate mutable fields (e.g., `count += 1`, `sum_temperature += X`) -> Trigger `update_state`.
- Read back to assert derivations (e.g., `average_temperature` recalculated).
- Attempt updating an immutable field (e.g., `truck_id`) to verify invariant protection.
- Attempt updating a missing key (verify rejection).

### 4.3 Delete (`delete_state`) & Exists (`exists_state`)
- Verify `exists_state` returns `True` for a known key and `False` for an unknown key.
- Verify `delete_state` permanently removes the key (`get_state` subsequently returns `Not Found`).

### 4.4 Full Lifecycle Workflow
Execute the end-to-end chain: `exists? (False)` → `put` → `get` → `update` → `exists? (True)` → `delete` → `get (Not Found)`.

## 5. Edge Case & Failure Testing
- **Edge Cases:** Zero events processed (average strictly 0), extremely large temperature floats, very old timestamps, max payload sizes.
- **Storage Failures:** Simulating RocksDB read/write IO errors (using mocks or corrupted file permissions) to ensure exceptions bubble up cleanly without corrupting application state.

## 6. Performance & Stress Testing
- **Latency Assertions:** CRUD operations should resolve in predictable microsecond ranges. `exists_state` latency must be demonstrably lower than `get_state` due to skipped deserialization.
- **Stress Runs:** Executing millions of alternating `put`/`update`/`delete` operations concurrently to detect memory leaks, verify thread safety of RocksDB wrappers, and confirm internal database compaction stability.

## 7. Regression Strategy
Any future modification to domain models or serialization logic mandates a full run of the Test Matrix. Integration tests serve as a strict gateway to ensure that backward compatibility is never broken (e.g., old JSON payload structures must remain deserializable).
