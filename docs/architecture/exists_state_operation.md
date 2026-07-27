# State Existence Check (exists_state) Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification defines the architecture, workflow, and optimization strategies for the **State Existence Check (`exists_state`)** operation. This operation provides a highly efficient, lightweight mechanism to query RocksDB for the presence of a `TruckState` without paying the computational cost of object deserialization or memory allocation.

## 2. Architecture & Responsibilities
The `exists_state` operation serves as a fast-path boolean query layer.
- **Responsibilities:** Validating the storage key format, executing a low-overhead presence check against RocksDB, and returning a strict `True` or `False`.
- **Out of Scope:** Pulling the entire byte array into memory, decoding UTF-8, parsing JSON, validating domain fields, or mutating the database.

```text
CRUD / Recovery Manager → exists_state(Key) → RocksDB Lookup → Boolean
```

## 3. Storage Key Lookup Strategy
The operation leverages the exact same deterministic storage key format used by `put_state` and `get_state`.
- **Format:** `{truck_id}:{window_start_iso8601}`
- **Lookup Method:** The implementation should ideally utilize RocksDB's `key_may_exist()` (leveraging Bloom filters) followed by a lightweight exact presence check. If the Python wrapper enforces standard `get()`, the payload bytes must be explicitly discarded immediately, strictly avoiding string coercion, JSON parsing, or object instantiation.

## 4. Operation Workflow
1. **Key Validation:** Ensures the key string is non-null and adheres to expected format rules.
2. **Persistence Layer Check:** Queries RocksDB for the key's presence.
3. **Boolean Result:** 
   - Returns `True` if the RocksDB engine confirms the key's presence.
   - Returns `False` if the key is missing.
4. **Immediate Return:** Halts further processing. No deserializer is invoked.

## 5. Performance Optimizations & Constraints
The primary purpose of this operation is optimization:
- **Zero Deserialization:** By skipping UTF-8 decoding and JSON parsing, CPU usage is heavily reduced.
- **Garbage Collection Optimization:** Avoids allocating Python objects, strings, and dictionaries just to check existence, reducing memory pressure.
- **Constraint:** The operation is strictly read-only and side-effect free.

## 6. Error Handling
It is critical to distinguish between a missing key and an operational failure:
- **Not Found:** Resolves to a clean `False`.
- **Validation Error:** Fast-fails with an `ArgumentError` on a malformed key string.
- **Storage/IO Error:** If RocksDB throws a hardware or connection exception, it is caught and rethrown as an `OperationError`. It must **never** be silently swallowed and returned as `False`, which could cause the application to erroneously overwrite data thinking it didn't exist.

## 7. Component Interactions
This operation acts as a high-frequency guard clause for other modules:
- **`update_state`:** May call `exists_state` to verify presence before attempting a full read-modify-write cycle.
- **`put_state`:** (If configured for strict insert-only) calls `exists_state` to reject duplicates instantly.
- **Recovery Manager:** Uses this to quickly scan which checkpointed keys actually survived in storage before queuing full deserializations.

## 8. Future Extensibility
While currently designed for single-key presence checks, the architecture supports natural evolution:
- **Batch Exists:** Verifying multiple keys simultaneously using RocksDB `MultiGet`.
- **Prefix/Window Exists:** Determining if *any* state exists for a specific processing window using a lightweight RocksDB iterator `Seek()`.
