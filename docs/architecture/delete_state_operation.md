# Delete State (delete_state) Design Specification
**StreamForge RocksDB State Storage Module**

## 1. Objective
This specification defines the architecture and workflow for the **Delete State (`delete_state`)** operation. This operation is the primary mechanism for permanently and atomically removing an obsolete or expired `TruckState` from RocksDB, ensuring long-term storage consistency and safe lifecycle cleanup.

## 2. Architecture & Responsibilities
The `delete_state` operation provides a direct, low-overhead interface to RocksDB's deletion mechanism.
- **Responsibilities:** Validating the storage key format and triggering `RocksDB.delete(key)`.
- **Out of Scope:** Deserializing the object (unless existence verification is strictly required by business logic), triggering aggregations, or manipulating the domain model.

```text
Cleanup Manager → delete_state(Key) → RocksDB.delete()
```

## 3. Deletion Strategy & State Existence
StreamForge adopts the **Delete Directly (Strategy 2)** approach for optimal performance during large-scale cleanup phases.
- **Direct Delete:** `delete_state` does not perform a prior `RocksDB.get()` to verify existence. It issues the delete command immediately. If the key doesn't exist, RocksDB safely ignores the operation (idempotent behavior). 
- **Benefit:** Eliminates read latency and object deserialization overhead during aggressive window expiration sweeps.

## 4. Operation Workflow
1. **Key Validation:** Pre-verifies the storage key format (e.g., non-null, non-empty string).
2. **Persistence Layer Call:** Invokes `RocksDB.delete(key)` through the `DatabaseManager`.
3. **Verification:** Validates that the underlying storage engine acknowledged the operation without throwing IO exceptions.
4. **Result:** Returns an Operation Status (`Success` or `Delete Failed`).

## 5. Atomicity & State Lifecycle
- **Atomicity:** The deletion is strictly atomic at the storage engine level. The state is either fully removed or the operation fails. There is no partial deletion state.
- **Lifecycle Integration:** Once a processing window expires, the Cleanup Manager invokes this operation. Any subsequent `get_state()` or `update_state()` calls using this key will immediately receive a `State Not Found` signal, terminating the object's lifespan.

## 6. Error Handling
Failures during deletion are strictly trapped and propagated:
- **Validation Errors:** Fast-fails with an `ArgumentError` if the key string is null or invalid.
- **Storage/IO Errors:** RocksDB exceptions (e.g., storage disconnected, write permissions revoked) are caught, logged, and rethrown. It is essential that the caller knows the state was *not* removed to avoid continuous storage growth.

## 7. Performance & Constraints
- **Execution Cost:** 1 Write (`RocksDB.delete`). Zero reads. Zero deserialization overhead.
- **Constraints:** The operation must depend solely on the RocksDB delete interface. It must never attempt to recreate missing state or read the state prior to deletion.

## 8. Future Extensibility
While this operation handles single-key permanent deletion, the architecture allows for natural future extensions:
- **Batch Delete:** Utilizing RocksDB `WriteBatch` for clearing thousands of keys efficiently.
- **Range Delete:** Leveraging `RocksDB.delete_range()` to clear an entire processing window by time-prefix instantly.
- **Soft Deletes/TTL:** Relying on RocksDB's native TTL properties for automatic garbage collection.
